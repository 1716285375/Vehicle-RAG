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

## `GET /v1/sessions/{session_id}`

返回指定会话的问答历史。

## `DELETE /v1/sessions/{session_id}`

删除指定会话的本地历史记录。

## `GET /v1/knowledge/documents`

支持 `doc_id`, `doc_type`, `vehicle_model` 查询参数过滤文档列表。
