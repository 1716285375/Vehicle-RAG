from app.models import Page


class TableRepairCleaner:
    def clean(self, pages: list[Page]) -> list[Page]:
        repaired: list[Page] = []
        for page in pages:
            lines = []
            for line in page.lines:
                line = " | ".join(part.strip() for part in line.split("\t") if part.strip())
                lines.append(line)
            repaired.append(page.with_text("\n".join(lines)))
        return repaired

