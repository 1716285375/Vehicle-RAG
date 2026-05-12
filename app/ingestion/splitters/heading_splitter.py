import re
from dataclasses import dataclass, field
from typing import Any

from app.ingestion.splitters.base import BaseSplitter, count_tokens
from app.models import Chunk, Page


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$|^(\d+(?:\.\d+)*)[、. ]+(.{1,80})$")


@dataclass
class Section:
    level: int
    title: str
    content: list[str] = field(default_factory=list)
    path: list[str] = field(default_factory=list)


class HeadingSplitter(BaseSplitter):
    def __init__(self, max_tokens: int = 500) -> None:
        self.max_tokens = max_tokens

    def split(self, pages: list[Page], base_metadata: dict[str, Any]) -> list[Chunk]:
        sections = self._sections(pages)
        chunks: list[Chunk] = []
        for section in sections:
            text = "\n".join(section.content).strip()
            if not text:
                continue
            if count_tokens(text) <= self.max_tokens:
                chunks.append(self._chunk(text, section, base_metadata, 0))
                continue
            for idx, part in enumerate(self._split_paragraphs(text)):
                chunks.append(self._chunk(part, section, base_metadata, idx))
        return chunks

    def _sections(self, pages: list[Page]) -> list[Section]:
        stack: list[Section] = []
        sections: list[Section] = []
        current = Section(level=1, title="未分章节", path=["未分章节"])
        sections.append(current)

        for page in pages:
            for raw_line in page.text.splitlines():
                line = raw_line.strip()
                if not line:
                    current.content.append("")
                    continue
                heading = self._parse_heading(line)
                if heading:
                    level, title = heading
                    while stack and stack[-1].level >= level:
                        stack.pop()
                    path = [s.title for s in stack] + [title]
                    current = Section(level=level, title=title, path=path)
                    stack.append(current)
                    sections.append(current)
                else:
                    current.content.append(line)
        return sections

    def _parse_heading(self, line: str) -> tuple[int, str] | None:
        match = HEADING_RE.match(line)
        if not match:
            return None
        if match.group(1):
            return len(match.group(1)), match.group(2).strip()
        numbering = match.group(3)
        return numbering.count(".") + 1, f"{numbering} {match.group(4).strip()}"

    def _split_paragraphs(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: list[str] = []
        buf: list[str] = []
        for paragraph in paragraphs:
            candidate = "\n\n".join(buf + [paragraph])
            if buf and count_tokens(candidate) > self.max_tokens:
                chunks.append("\n\n".join(buf))
                buf = [paragraph]
            else:
                buf.append(paragraph)
        if buf:
            chunks.append("\n\n".join(buf))
        return chunks

    def _chunk(
        self, text: str, section: Section, base_metadata: dict[str, Any], sub_idx: int
    ) -> Chunk:
        return Chunk(
            text=text,
            metadata={
                **base_metadata,
                "heading_path": section.path,
                "section": " / ".join(section.path),
                "sub_idx": sub_idx,
            },
        )

