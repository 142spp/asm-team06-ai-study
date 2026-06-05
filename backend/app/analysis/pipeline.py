"""6-1 파이프라인 오케스트레이션.

Context Loader → (1 LLM 호출) → Pydantic 검증(1회 재시도) → 선호 2차(stub) → Completeness.
planning.md: 검증 실패 시 1회 재시도, 그래도 실패하면 분석 실패 + 원문을 Pending으로.
"""

from pydantic import ValidationError

from app.analysis.completeness import finalize
from app.llm.base import LLMClient, get_llm
from app.schemas.item import AnalyzeResult, ContextBundle, Item, LLMOutput


def load_context() -> ContextBundle:
    """Context Loader (M1 stub).

    M3에서 6-3의 feedback.db `load_user_preferences()`를 재사용해 선호를 채우고(D3),
    Guideline Store(D4)·기존 항목 요약을 붙인다. 지금은 빈 컨텍스트.
    """
    return ContextBundle()


def _postprocess(result: AnalyzeResult, context: ContextBundle) -> AnalyzeResult:
    """선호·지침 2차 재보정 (M3에서 구현). 지금은 통과."""
    return result


def analyze(*, raw_text: str, base_date: str, llm: LLMClient | None = None) -> AnalyzeResult:
    llm = llm or get_llm()
    context = load_context()

    output = _call_with_retry(llm, raw_text, base_date, context)
    if output is None:
        return _analysis_failed(raw_text)

    result = finalize(output)
    return _postprocess(result, context)


def _call_with_retry(
    llm: LLMClient, raw_text: str, base_date: str, context: ContextBundle, attempts: int = 2
) -> LLMOutput | None:
    for _ in range(attempts):
        try:
            raw = llm.analyze(raw_text=raw_text, base_date=base_date, context=context)
            return LLMOutput.model_validate(raw)
        except (ValidationError, ValueError, KeyError):
            continue
    return None


def _analysis_failed(raw_text: str) -> AnalyzeResult:
    """분석 실패 → 원문을 보류 항목으로 (확인 필요)."""
    return AnalyzeResult(
        input_type="none",
        items=[Item(
            type="pending", title="분석 실패", source_sentence=raw_text,
            recommended_tool="save_to_pending", type_certainty=0.0,
            date_status="missing", required_ok=False,
            confidence=0.0, needs_confirmation=True, confirmation_reason="정보 부족",
            clarification_question="자동 분석에 실패했습니다. 원문을 직접 확인해 주세요.",
        )],
    )
