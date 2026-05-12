from app.models import Page


class DedupeCleaner:
    def clean(self, pages: list[Page]) -> list[Page]:
        seen: set[str] = set()
        cleaned_pages: list[Page] = []
        for page in pages:
            kept: list[str] = []
            for paragraph in page.text.split("\n\n"):
                normalized = " ".join(paragraph.split())
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                kept.append(paragraph.strip())
            cleaned_pages.append(page.with_text("\n\n".join(kept)))
        return cleaned_pages

