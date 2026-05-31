import json
from dataclasses import dataclass
import bm25s
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from sqlalchemy import create_engine, text

from llm import generateResponse

DATABASE_URL = "postgresql+psycopg2://nuvolos:test@nv-service-da6d6081f2d71ff42469db91faef5de9:5432/vectordb"
engine = create_engine(DATABASE_URL)



@dataclass
class Chunk:
    text: str
    case_id: str
    chunk_idx: int
    source: str = ""
    author: str = ""
    url: str = ""

@dataclass
class Result:
    chunk: Chunk
    first_stage_score: float 
    rerank_score: float = 0.0
    rank: int = 0

def load_bm25(save_dir="chunks"):
    retriever = bm25s.BM25.load(save_dir, load_corpus=False)
    with open(f"{save_dir}/chunks_meta.json") as f:
        chunks = [Chunk(**d) for d in json.load(f)]
    return retriever, chunks

def search_bm25(query, retriever, chunks, top_k=50):
    tokens = bm25s.tokenize([query], stopwords="en")
    idxs, scores = retriever.retrieve(tokens, k=min(top_k, len(chunks)))
    return [(chunks[int(i)], float(s)) for i, s in zip(idxs[0], scores[0])]

def search_dense_db(query, encoder, engine, top_k=50):
    q = encoder.encode(query).tolist()
    sql = text("""
        SELECT text, case_id, source, author, url,
               1 - (embedding <=> cast(:embedding as vector)) AS score
        FROM documents
        ORDER BY embedding <=> cast(:embedding as vector)
        LIMIT :top_k
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"embedding": str(q), "top_k": top_k}).fetchall()

    chunks = [Chunk(text=r.text, case_id=r.case_id, chunk_idx=i,
                    source=r.source, author=r.author, url=r.url)
              for i, r in enumerate(rows)]
    scores = [r.score for r in rows]
    return list(zip(chunks, scores))

def get_case_metadata_db(case_id, engine):
    sql = text("SELECT * FROM documents WHERE case_id = :case_id LIMIT 1")
    with engine.connect() as conn:
        row = conn.execute(sql, {"case_id": case_id}).fetchone()
    if row is None:
        return {}
    return {"court": row.author, "url": row.url, "source": row.source}
def rrf(ranked_lists, k=60, weights=None):
    if weights is None:
        weights = [1.0] * len(ranked_lists)
    scores, chunk_map = {}, {}
    for lst, w in zip(ranked_lists, weights):
        for rank, (chunk, _) in enumerate(lst, 1):
            key = f"{chunk.case_id}::{chunk.chunk_idx}"
            scores[key] = scores.get(key, 0.0) + w / (k + rank)
            chunk_map[key] = chunk
    merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(chunk_map[k], s) for k, s in merged]

def load_reranker(model_name="Qwen/Qwen3-Reranker-0.6B"):
    model = CrossEncoder(model_name, trust_remote_code=True)
    return model

def rerank(query, candidates, model, top_k=10):
    passages = [chunk.text for chunk, _ in candidates]
    scores = model.predict([(query, p) for p in passages])
    results = [
        Result(chunk=chunk, first_stage_score=s, rerank_score=float(score))
        for (chunk, s), score in zip(candidates, scores)
    ]
    results.sort(key=lambda r: r.rerank_score, reverse=True)
    for i, r in enumerate(results[:top_k], 1):
        r.rank = i
    return results[:top_k]

def get_full_documents(results, engine):
    case_ids = list({r.chunk.case_id for r in results})
    sql = text("""
        SELECT case_id, string_agg(text, ' ' ORDER BY id) AS full_text
        FROM documents
        WHERE case_id = ANY(:case_ids)
        GROUP BY case_id
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"case_ids": case_ids}).fetchall()
    return {r.case_id: r.full_text for r in rows}

def retrieve(query, bm25_retriever, bm25_chunks, encoder, reranker, engine,
             candidate_k=10, final_k=5, bm25_weight=0.5, dense_weight=0.5):

    bm25_hits  = search_bm25(query, bm25_retriever, bm25_chunks, top_k=candidate_k)
    dense_hits = search_dense_db(query, encoder, engine, top_k=candidate_k)
    merged     = rrf([bm25_hits, dense_hits], weights=[bm25_weight, dense_weight])

    return rerank(query, merged, reranker, top_k=final_k)

def format_for_api(results):
    return [
        {
            "title":      r.chunk.case_id,
            "court":      r.chunk.author,
            "snippet":    r.chunk.text[:500],
            "full":         r.chunk.text,
            "score":      round(r.rerank_score, 4),
            "source_url": r.chunk.url,
        }
        for r in results
    ]

def generate_answer(model,tokenizer,query: str, retrieved_chunks: list, results, engine, full_text = False): 
    #answer = (
    #    f"You asked: '{query}'. Based on the retrieved legal references, "
    #    "this prototype would explain whether the cases support or contradict the claim."
    # )

    # retrieved = [text['title']+text['court']+text['full'] for text in retrieved_chunks]
    
    # answer = generateResponse(model,tokenizer,query,retrieved).split("### Answer:")[-1]

    if full_text:
        full_docs = get_full_documents(results, engine)

        retrieved = [
            chunk["title"] + chunk["court"] + full_docs.get(chunk["title"], chunk["full"])
            for chunk in retrieved_chunks
        ]
    else:
        retrieved = [text['title']+text['court']+text['full'] for text in retrieved_chunks]

    answer = generateResponse(model, tokenizer, query, retrieved).split("### Answer:")[-1]

    print(answer)

    return answer

    #reasoning_path = [
    #    "User submits a legal question or claim.",
    #    "The API sends the query to the retriever.",
    #    "The retriever returns the top-k most relevant legal case chunks.",
    #    "The system generates a user-friendly answer with references."
    # ]
