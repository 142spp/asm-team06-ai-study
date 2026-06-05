"""6-1 회귀 테스트 + 데모 픽스처. FakeLLM 기반이라 키/네트워크 없이 돈다.

실행: uv run --directory backend python tests/test_analyze.py
"""

from app.analysis.pipeline import analyze
from app.llm.fake import FakeLLM

BASE = "2026-06-05"


def _run(text: str):
    return analyze(raw_text=text, base_date=BASE, llm=FakeLLM())


def test_scenario1_multi_item():
    r = _run("내일까지 성종은 발표자료, 동근은 API 테스트 정리, 우태는 데모 영상 준비. 금요일 오전 10시 최종 리허설하자.")
    assert r.input_type == "meeting_note"
    assert len(r.items) == 4
    types = [i.type for i in r.items]
    assert types == ["task", "task", "task", "calendar"]
    # 전부 명확 → 확인 불필요
    assert all(not i.needs_confirmation for i in r.items)
    # 일정은 time 있으니 all_day 아님
    assert r.items[3].all_day is False


def test_scenario2_vague_calendar_and_risk():
    r = _run("다음 주쯤 멘토님께 보여드리고, 안 되면 캘린더 연동은 Mock으로 대체하자.")
    cal = next(i for i in r.items if i.type == "calendar")
    risk = next(i for i in r.items if i.type == "risk")
    # 모호 일정(날짜 vague, calendar 필수) → 정보 부족으로 확인 필요
    assert cal.needs_confirmation is True
    assert cal.confirmation_reason == "정보 부족"
    assert cal.clarification_question is not None
    # 날짜 없는 calendar → all_day 처리, 모호 날짜로 confidence 감점(1.0 미만)
    assert cal.all_day is True
    assert cal.confidence <= 0.7
    # 리스크는 통과
    assert risk.needs_confirmation is False


def test_low_certainty_branches_to_class_ambiguous():
    from app.schemas.item import LLMItem
    from app.analysis.completeness import finalize_item

    item = finalize_item(LLMItem(
        type="task", title="기획서 다시 보기", type_certainty=0.5,
        date_status="missing", required_ok=True,
    ))
    assert item.needs_confirmation is True
    assert item.confirmation_reason == "분류 애매"   # 분류가 먼저, 완성도는 안 봄


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")
