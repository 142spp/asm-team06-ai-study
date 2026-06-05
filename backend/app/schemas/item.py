"""
공통 데이터 계약 (6-1 산출물).

⚠️ DUMMY/임시: D1(공통 Item 스키마)은 다른 팀원이 정리해서 보내주기로 함.
   여기 정의는 6-1을 독립적으로 굴리기 위한 **자리표시자**다.
   확정본이 오면 이 파일을 교체하고 import 경로만 맞추면 된다.

설계 메모(단순화):
- 입력 유형(회의록/공지/메모…) 다중분류는 두지 않는다. 실행 항목이 없으면 items=[]로
  표현한다(= "none"). 추출 로직이 입력 유형에 따라 갈리지 않으므로 라벨이 불필요.
- 항목 유형은 Tool 라우팅의 핵심이라 유지하되, 가짜 유형은 정리한다:
    · 보류(pending) → 별도 type이 아니라 needs_confirmation 플래그로 표현.
    · 무시(ignore)  → 출력하지 않음(필터).
    · 분석 실패/미분류 → type=None.
"""

from typing import Literal

from pydantic import BaseModel, Field

# Tool로 라우팅되는 실질 유형 4종
ItemType = Literal["task", "calendar", "memo", "risk"]
ToolName = Literal[
    "create_task", "create_calendar_event", "create_memo",
    "create_risk_log", "save_to_pending",   # save_to_pending은 6-2가 확인 필요 항목에 사용
]
Priority = Literal["high", "medium", "low"]
DateStatus = Literal["concrete", "vague", "missing"]

# 코드 enum → 화면 한글 라벨 (None/미분류는 호출부에서 기본값 처리)
LABELS: dict[str, str] = {
    "task": "할 일", "calendar": "일정", "memo": "메모", "risk": "리스크",
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


class Item(LLMItem):
    """완성도 판단까지 끝난 최종 항목 (6-1 → 6-2 핸드오프 단위).

    type=None은 분석 실패/미분류(원문 보류)를 뜻한다.
    """
    type: ItemType | None = None
    all_day: bool = False
    confidence: float = 1.0                      # 표시용 = min(완성도, 분류확신도)
    needs_confirmation: bool = False
    confirmation_reason: str | None = None       # "분류 애매" | "정보 부족" | None
    clarification_question: str | None = None


class LLMOutput(BaseModel):
    """Solar 응답 전체. pipeline이 이걸로 검증한다. 실행 항목 없으면 items=[]."""
    items: list[LLMItem] = Field(default_factory=list)


class AnalyzeResult(BaseModel):
    """POST /analyze 응답. items=[] 이면 실행 항목 없음(요약만)."""
    items: list[Item] = Field(default_factory=list)
