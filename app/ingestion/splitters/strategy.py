from app.ingestion.splitters.base import BaseSplitter
from app.ingestion.splitters.fixed_window import FixedWindowSplitter
from app.ingestion.splitters.heading_splitter import HeadingSplitter
from app.ingestion.splitters.semantic_splitter import FAQSplitter, TroubleCodeSplitter


class SplitterRouter:
    def __init__(self) -> None:
        self.strategies: dict[str, BaseSplitter] = {
            "manual": HeadingSplitter(max_tokens=500),
            "faq": FAQSplitter(),
            "trouble_code": TroubleCodeSplitter(),
            "policy": FixedWindowSplitter(window=800, overlap=100),
        }

    def get(self, doc_type: str) -> BaseSplitter:
        return self.strategies.get(doc_type, self.strategies["policy"])

