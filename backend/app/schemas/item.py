"""
공통 데이터 계약 (6-1 산출물).

⚠️ DUMMY/임시: D1(공통 Item 스키마)은 다른 팀원이 정리해서 보내주기로 함.
   여기 정의는 6-1을 독립적으로 굴리기 위한 **자리표시자**다.
   확정본이 오면 이 파일을 교체하고 import 경로만 맞추면 된다.
   필드 근거는 planning.md(출력 JSON 예시 + confidence 플래그 표).
"""

from typing import Literal

from pydantic import BaseModel, Field

ItemType = Literal["task", "calendar", "memo", "risk", "pending", "ignore"]
InputType = Literal["meeting_note", "chat", "notice", "memo", "none"]
ToolName = Literal[
    "create_task", "create_calendar_event", "create_memo",
    "create_risk_log", "save_to_pending",
]
Priority = Literal["high", "medium", "low"]
DateStatus = Literal["concrete", "vague", "missing"]

# 코드 enum → 화면 한글 라벨
LABELS: dict[str, str] = {
    "task": "할 일", "calendar": "일정", "memo": "메모",
    "risk": "리스크", "pending": "보류", "ignore": "무시",
}


class ContextBundle(BaseModel):
    """Context Loader 결과 (선호/지침/기존 항목 요약)."""
    preferences: list[dict] = Field(default_factory=list)
    guidelines: list[dict] = Field(default_factory=list)
    existing_items_summary: str = ""


class LLMItem(BaseModel):
    """LLM(Solar)이 항목별로 내놓는 원본. 점수는 LLM이 매기지 않고 플래그만 준다."""
    type: ItemType
    title: str
    assignee: str | None = None
    date: str | None = None          # "YYYY-MM-DD"
    time: str | None = None          # "HH:MM" (KST)
    priority: Priority = "medium"
    source_sentence: str = ""
    recommended_tool: ToolName | None = None   # 6-1 힌트, 6-2가 확정(D5)

    # 판단 플래그 (planning.md confidence 절)
    type_certainty: float = 1.0
    date_status: DateStatus = "concrete"
    assignee_present: bool = False
    time_present: bool = False
    needs_base_event: bool = False
    required_ok: bool = True


class LLMOutput(BaseModel):
    """Solar 응답 전체. pipeline이 이걸로 검증한다."""
    input_type: InputType
    items: list[LLMItem] = Field(default_factory=list)


class Item(LLMItem):
    """완성도 판단까지 끝난 최종 항목 (6-1 → 6-2 핸드오프 단위)."""
    all_day: bool = False
    confidence: float = 1.0                      # 표시용 = min(완성도, 분류확신도)
    needs_confirmation: bool = False
    confirmation_reason: str | None = None       # "분류 애매" | "정보 부족" | None
    clarification_question: str | None = None


class AnalyzeResult(BaseModel):
    """POST /analyze 응답."""
    input_type: InputType
    items: list[Item] = Field(default_factory=list)
