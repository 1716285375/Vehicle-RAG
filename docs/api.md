# API

## `GET /health`

返回服务健康状态。
所有 HTTP 响应都会包含 `X-Request-ID` 响应头,可传入同名请求头进行链路追踪。

## `GET /health/db`

返回可选数据库后端健康状态。未配置 MySQL 时使用本地 no-op 后端并返回 `ok: true`。

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
`final` 事件和同步问答响应包含 `cached` 字段,用于标识是否命中问答缓存。
问题中的故障码和车型会自动提取为检索过滤条件,并通过 `query_filters` SSE 事件返回。

## `GET /v1/sessions/{session_id}`

返回指定会话的问答历史。

## `GET /v1/sessions`

返回本地会话摘要列表,包含会话 ID、轮数、最近问题和更新时间。

## `DELETE /v1/sessions/{session_id}`

删除指定会话的本地历史记录。

## `GET /v1/knowledge/documents`

支持 `doc_id`, `doc_type`, `vehicle_model` 查询参数过滤文档列表。

## `POST /v1/knowledge/rebuild`

请求体:

```json
{"directory":"data/raw","doc_type":"manual","metadata":{"vehicle_model":"L9"}}
```

清空当前向量索引后批量摄入目录内支持的文档。
