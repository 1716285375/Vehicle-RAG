# Splitting Strategy

- `manual`: 标题层级切片,标题路径写入 `heading_path`。
- `faq`: 优先把 Q/A 相邻段落合成一个 chunk。
- `trouble_code`: 每行一个 chunk,首列作为 `metadata.code`。
- `policy`: 固定窗口 + overlap。

