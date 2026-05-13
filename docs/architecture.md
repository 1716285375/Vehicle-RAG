# Architecture

当前实现是本地 MVP:

- ingestion: loader -> cleaner -> splitter -> embedding -> JSON vector store
- processed output: cleaned chunks are written as JSONL under `data/processed/chunks`
- retrieval: vector recall -> lightweight rerank -> context assembly
- hallucination guard: low relevance results are dropped before context assembly
- evaluation: JSONL test sets can report citation and keyword hit rates
- qa: extractive fallback LLM or OpenAI-compatible chat completion endpoint
- api: FastAPI `/v1/ingest`, `/v1/qa`, `/v1/qa/stream`, `/v1/knowledge/documents`

生产替换点保留在 `app/embedding/bge_m3.py`, `app/retrieval/vector_store.py`, `app/llm/client.py`。
