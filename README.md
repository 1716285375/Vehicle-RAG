# Vehicle-RAG

车载知识库 RAG 问答系统的本地可运行 MVP。

## 快速开始

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001
```

摄入 Markdown 示例:

```bash
python scripts/ingest_directory.py --dir data/raw --doc-type manual --metadata "{\"vehicle_model\":\"L9\"}"
```

问答:

```bash
curl -X POST http://localhost:8001/v1/qa -H "Content-Type: application/json" -d "{\"question\":\"AUTOHOLD 怎么开\",\"filters\":{\"vehicle_model\":\"L9\"}}"
```

默认实现使用确定性的本地 Hash embedding 和 JSON 向量索引，便于无 GPU、无外部服务时开发验证。

