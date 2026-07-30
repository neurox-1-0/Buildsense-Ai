from core.utils import clamp

def score_confidence(evidence_count: int, source_count: int, extracted_count: int) -> float:
    return round(clamp(0.25 + min(evidence_count, 20) * 0.025 + min(source_count, 4) * 0.08 + min(extracted_count, 10) * 0.02), 2)
