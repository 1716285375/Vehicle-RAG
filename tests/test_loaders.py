import asyncio
from pathlib import Path

from app.ingestion.loaders.html_loader import HTMLLoader
from app.ingestion.loaders.markdown_loader import MarkdownLoader
from app.ingestion.loaders.text_utils import read_text_with_fallback


def test_read_text_with_fallback_reads_gb18030(tmp_path: Path):
    path = tmp_path / "manual.txt"
    path.write_bytes("座椅记忆".encode("gb18030"))
    assert read_text_with_fallback(path) == "座椅记忆"


def test_markdown_loader_uses_encoding_fallback(tmp_path: Path):
    asyncio.run(_run_markdown_loader_uses_encoding_fallback(tmp_path))


async def _run_markdown_loader_uses_encoding_fallback(tmp_path: Path):
    path = tmp_path / "manual.md"
    path.write_bytes("# 座椅\n\n座椅记忆设置".encode("gb18030"))
    pages = await MarkdownLoader().load(path)
    assert "座椅记忆" in pages[0].text


def test_html_loader_uses_encoding_fallback(tmp_path: Path):
    asyncio.run(_run_html_loader_uses_encoding_fallback(tmp_path))


async def _run_html_loader_uses_encoding_fallback(tmp_path: Path):
    path = tmp_path / "manual.html"
    path.write_bytes("<html><body>售后 FAQ</body></html>".encode("gb18030"))
    pages = await HTMLLoader().load(path)
    assert "售后 FAQ" in pages[0].text
