"""Upstage Solar 클라이언트.

⚠️ 사용 전 준비 (오프라인 샌드박스라 여기서 설치는 못 함):
    uv add --directory backend langchain-upstage
    export UPSTAGE_API_KEY=...        # Upstage 콘솔 발급
    export SOLAR_MODEL=solar-pro      # (선택) 기본값 solar-pro

planning.md: Solar의 JSON 출력을 코드가 해석한다 → 여기선 raw JSON만 받고,
검증/재시도는 pipeline이 담당한다. langchain_upstage import는 지연(lazy)해서
키가 없을 때(FakeLLM 경로)는 이 모듈이 의존성을 요구하지 않게 한다.
"""

import json
import os

from app.schemas.item import ContextBundle

_SYSTEM = """너는 비정형 텍스트에서 실행 항목을 뽑아 분류하는 분석기다.
반드시 아래 JSON 스키마만 출력한다(설명/마크다운 금지).

{
  "input_type": "meeting_note|chat|notice|memo|none",
  "items": [{
    "type": "task|calendar|memo|risk|pending|ignore",
    "title": "string",
    "assignee": "string|null",
    "date": "YYYY-MM-DD|null",
    "time": "HH:MM|null",
    "priority": "high|medium|low",
    "source_sentence": "근거 원문",
    "recommended_tool": "create_task|create_calendar_event|create_memo|create_risk_log|save_to_pending",
    "type_certainty": 0.0-1.0,
    "date_status": "concrete|vague|missing",
    "assignee_present": true/false,
    "time_present": true/false,
    "needs_base_event": true/false,
    "required_ok": true/false
  }]
}

규칙:
- 점수(confidence)는 매기지 마라. 위 플래그만 정확히 채운다.
- 특정 시각이 있으면 calendar, 산출물+마감이면 task.
- 상대 날짜는 기준 날짜(KST)로 환산한다.
- 한 입력에 여러 항목이 섞이면 독립 항목으로 분해한다.
- 실행 항목이 없으면 input_type="none", items=[]."""


class SolarLLM:
    def __init__(self) -> None:
        from langchain_upstage import ChatUpstage  # lazy

        self._llm = ChatUpstage(model=os.getenv("SOLAR_MODEL", "solar-pro"))

    def analyze(self, *, raw_text: str, base_date: str, context: ContextBundle) -> dict:
        human = (
            f"기준 날짜(KST): {base_date}\n"
            f"User Preference: {json.dumps(context.preferences, ensure_ascii=False)}\n"
            f"Guideline: {json.dumps(context.guidelines, ensure_ascii=False)}\n"
            f"기존 항목 요약: {context.existing_items_summary}\n\n"
            f"입력:\n{raw_text}"
        )
        resp = self._llm.invoke([("system", _SYSTEM), ("human", human)])
        return _extract_json(resp.content)


def _extract_json(content: str) -> dict:
    """코드펜스가 끼어도 본문 JSON만 떼어낸다. 파싱 실패는 pipeline이 재시도로 처리."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        text = text[4:] if text.lower().startswith("json") else text
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1])
