"""Completeness Check — 6-1의 핵심 IP.

LLM은 의미 플래그만 주고, 점수 계산과 임계값 분기는 코드(여기)가 한다.
규칙은 planning.md "confidence 산정 및 확인 필요 분기" 절을 그대로 옮긴 것.
LLM 없이 단위 테스트가 가능하도록 순수 함수로 작성한다.
"""

from app.analysis import config
from app.schemas.item import LABELS, AnalyzeResult, Item, LLMItem, LLMOutput


def _completeness_score(item: LLMItem) -> float:
    """기본 1.0에서 규칙 기반 감점. 0~1 clamp."""
    score = 1.0
    if item.type in config.DATE_RELEVANT_TYPES:
        if item.date_status == "vague":
            score -= config.PENALTY_DATE_VAGUE
        elif item.date_status == "missing":
            score -= config.PENALTY_DATE_MISSING
    if item.type == "task" and not item.assignee_present:
        score -= config.PENALTY_TASK_NO_ASSIGNEE
    if item.needs_base_event:
        score -= config.PENALTY_NEEDS_BASE_EVENT
    # 일정의 time 없음은 감점 아님 → all_day로 처리(아래 finalize)
    return max(0.0, min(1.0, score))


def _required_missing(item: LLMItem) -> bool:
    """필수 필드가 모호/누락이면 점수와 무관하게 확인 필요(무조건)."""
    if not item.required_ok:
        return True
    if item.type in config.DATE_REQUIRED_TYPES and item.date_status in ("vague", "missing"):
        return True
    return False


def _make_question(item: LLMItem, reason: str) -> str:
    label = LABELS.get(item.type, item.type)
    if reason == "분류 애매":
        return f"'{item.title}' 항목의 유형이 '{label}'가 맞나요?"
    # 정보 부족 — 무엇이 비었는지 짚어준다
    missing = []
    if item.type in config.DATE_REQUIRED_TYPES and item.date_status != "concrete":
        missing.append("날짜")
    if item.type == "task" and not item.assignee_present:
        missing.append("담당자")
    if item.needs_base_event:
        missing.append("기준 이벤트")
    if not missing:
        missing.append("필수 정보")
    return f"'{item.title}'의 {', '.join(missing)}을(를) 확인해 주세요."


def finalize_item(item: LLMItem) -> Item:
    completeness = _completeness_score(item)
    certainty = item.type_certainty
    confidence = min(completeness, certainty)
    all_day = item.type == "calendar" and not item.time_present

    # 분기 순서: 분류가 먼저. 분류 애매면 완성도는 보지 않는다(OR 게이트).
    needs_confirmation = False
    reason: str | None = None
    if certainty < config.CERTAINTY_THRESHOLD:
        needs_confirmation, reason = True, "분류 애매"
    elif _required_missing(item) or completeness < config.COMPLETENESS_THRESHOLD:
        needs_confirmation, reason = True, "정보 부족"

    question = _make_question(item, reason) if needs_confirmation else None

    return Item(
        **item.model_dump(),
        all_day=all_day,
        confidence=round(confidence, 2),
        needs_confirmation=needs_confirmation,
        confirmation_reason=reason,
        clarification_question=question,
    )


def finalize(output: LLMOutput) -> AnalyzeResult:
    return AnalyzeResult(items=[finalize_item(it) for it in output.items])
