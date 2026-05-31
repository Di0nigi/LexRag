# LexRag

### Project Overview:  
**LexRAG** is a retrieval-augmented system designed to enable **semantic search over 6.7M US case law records** using hybrid retrieval strategies. It combines dense vector embeddings (for semantic understanding) and sparse keyword matching (BM25) to surface legally relevant cases, supporting claim-level reasoning and explainable answers.  

---

### Key Features:  
- **Hybrid Retrieval**:  
  - **Dense Vector Search**: Uses cosine similarity on sentence embeddings (sentence encoder) to find semantically relevant legal chunks.  
  - **BM25 Sparse Retrieval**: Captures keyword matches for broader coverage.  
  - **Reciprocal Rank Fusion (RRF)**: Fuses dense and sparse results for unified ranking.  
  - **Cross-Encoder Reranking**: Final reranking with `ms-marco-MiniLM-L-6-v2` improves relevance ordering.  

- **Legal Reasoning Support**:  
  - Surfaces cases that **corroborate or contradict** a legal proposition.  
  - Provides **traceable reasoning paths** via an instruction-tuned language model.  

- **Explainable Answers**:  
  - Responses are structured, cite retrieved documents, and avoid hallucination by strictly relying on input data.  

---

### Dataset: 
- **Source**: [common-pile/caselaw_access_project](https://huggingface.co/datasets/common-pile/caselaw_access_project) (HuggingFace)  
- **Content**: Digitized US federal and state court opinions (~6.7M rulings) with metadata (court, jurisdiction, date).  
- **Used Subset**: First 15,000 rows due to size constraints.  

---

### Authors:  
- **Amrithavarshini Satheesh** (25-753-997)  
- **Cyril Smetanka** (24-754-434)  
- **Dionigi Rodriguez** (24-755-688)  
- **Roshni Gopal** (24-745-325)  
