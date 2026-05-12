from collections import Counter

from app.models import Page


class HeaderFooterCleaner:
    def detect_repeating_lines(self, pages: list[Page]) -> set[str]:
        if len(pages) < 3:
            return set()
        counter: Counter[str] = Counter()
        for page in pages:
            lines = [line.strip() for line in page.lines if line.strip()]
            for line in lines[:3] + lines[-3:]:
                counter[line] += 1
        threshold = max(2, int(len(pages) * 0.6))
        return {line for line, count in counter.items() if count >= threshold}

    def clean(self, pages: list[Page]) -> list[Page]:
        repeating = self.detect_repeating_lines(pages)
        if not repeating:
            return pages
        cleaned: list[Page] = []
        for page in pages:
            lines = [line for line in page.lines if line.strip() not in repeating]
            cleaned.append(page.with_text("\n".join(lines)))
        return cleaned

