import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    ascii_terms = re.findall(r"[a-zA-Z0-9]+", text.lower())
    cjk_terms = [char for char in text if "\u4e00" <= char <= "\u9fff"]
    return ascii_terms + cjk_terms


def bm25_scores(query: str, documents: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    query_terms = tokenize(query)
    if not query_terms or not documents:
        return [0.0 for _ in documents]

    doc_terms = [tokenize(document) for document in documents]
    doc_freq: Counter[str] = Counter()
    for terms in doc_terms:
        doc_freq.update(set(terms))

    avg_len = sum(len(terms) for terms in doc_terms) / max(1, len(doc_terms))
    total_docs = len(doc_terms)
    scores: list[float] = []
    for terms in doc_terms:
        term_counts = Counter(terms)
        doc_len = len(terms) or 1
        score = 0.0
        for term in query_terms:
            freq = term_counts.get(term, 0)
            if freq == 0:
                continue
            idf = math.log(1 + (total_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            denom = freq + k1 * (1 - b + b * doc_len / max(avg_len, 1e-9))
            score += idf * (freq * (k1 + 1) / denom)
        scores.append(score)
    return scores


def reciprocal_rank_fusion(
    vector_scores: list[float],
    lexical_scores: list[float],
    k: int = 60,
    vector_weight: float = 0.7,
    lexical_weight: float = 0.3,
) -> list[float]:
    fused = [0.0 for _ in vector_scores]
    vector_order = sorted(range(len(vector_scores)), key=lambda index: vector_scores[index], reverse=True)
    lexical_order = sorted(range(len(lexical_scores)), key=lambda index: lexical_scores[index], reverse=True)

    for rank, index in enumerate(vector_order, start=1):
        fused[index] += vector_weight / (k + rank)
    for rank, index in enumerate(lexical_order, start=1):
        if lexical_scores[index] > 0:
            fused[index] += lexical_weight / (k + rank)
    return fused
