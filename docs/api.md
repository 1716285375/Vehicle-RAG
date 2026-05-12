# API

## `POST /v1/ingest`

Multipart form:

- `file`: PDF/DOCX/Markdown/HTML/TXT
- `doc_type`: `manual | faq | trouble_code | policy`
- `metadata`: JSON string

## `POST /v1/qa`

```json
{"question":"AUTOHOLD 怎么开","filters":{"vehicle_model":"L9"}}
```

## `POST /v1/qa/stream`

返回 SSE 事件: `query_rewritten`, `retrieved`, `reranked`, `token`, `final`, `done`。

