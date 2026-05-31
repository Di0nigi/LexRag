from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import torch

from schemas import ChatRequest, ChatResponse, Reference
from retriever import (load_bm25, load_reranker, retrieve, format_for_api,
                        engine, generate_answer)
from sentence_transformers import SentenceTransformer, CrossEncoder

torch.cuda.empty_cache()

from llm import loadModel2B,loadModel4B

bm25_retriever, bm25_chunks = load_bm25("/files/chunks")
encoder  = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
reranker = load_reranker("cross-encoder/ms-marco-MiniLM-L-6-v2")
model, tokenizer = loadModel4B()


app = FastAPI(title="Legal RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Legal RAG backend is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    
    results = retrieve(
        request.query,
        bm25_retriever, bm25_chunks, encoder, reranker, engine,
        candidate_k=25, final_k=5,
    )

    retrieved_chunks = format_for_api(results)
    answer= generate_answer(model,tokenizer,request.query, retrieved_chunks, results, engine)

    references = [
        Reference(
            title=item["title"],
            court=item.get("court"),
            date=item.get("date"),
            snippet=item["snippet"],
            full = item["full"],
            score=item["score"],
            source_url=item.get("source_url")
        )
        for item in retrieved_chunks
    ]

    return ChatResponse(
        answer=answer,
        reasoning_path=[""],
        references=references
    )