# Architecture

当前实现是本地 MVP:

- ingestion: loader -> cleaner -> splitter -> embedding -> JSON vector store
- retrieval: vector recall -> lightweight rerank -> context assembly
- qa: extractive fallback LLM or OpenAI-compatible chat completion endpoint
- api: FastAPI `/v1/ingest`, `/v1/qa`, `/v1/qa/stream`, `/v1/knowledge/documents`

生产替换点保留在 `app/embedding/bge_m3.py`, `app/retrieval/vector_store.py`, `app/llm/client.py`。

