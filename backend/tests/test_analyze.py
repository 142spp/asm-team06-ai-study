"""6-1 회귀 테스트 + 데모 픽스처. FakeLLM 기반이라 키/네트워크 없이 돈다.

실행: uv run --directory backend python tests/test_analyze.py
"""

from app.analysis.completeness import finalize_item
from app.analysis.pipeline import analyze
from app.llm.fake import FakeLLM
from app.schemas.item import LLMItem

BASE = "2026-06-05"


def _run(text: str):
    return analyze(raw_text=text, base_date=BASE, llm=FakeLLM())


def test_scenario1_multi_item():
    r = _run("내일까지 성종은 발표자료, 동근은 API 테스트 정리, 우태는 데모 영상 준비. 금요일 오전 10시 최종 리허설하자.")
    assert len(r.items) == 4
    assert [i.type for i in r.items] == ["task", "task", "task", "calendar"]
    assert all(not i.needs_confirmation for i in r.items)  # 전부 명확
    assert r.items[3].all_day is False                     # 일정에 time 있음


def test_scenario2_vague_calendar_and_risk():
    r = _run("다음 주쯤 멘토님께 보여드리고, 안 되면 캘린더 연동은 Mock으로 대체하자.")
    cal = next(i for i in r.items if i.type == "calendar")
    risk = next(i for i in r.items if i.type == "risk")
    # 모호 일정(날짜 vague, calendar 필수) → 정보 부족으로 확인 필요
    assert cal.needs_confirmation is True
    assert cal.confirmation_reason == "정보 부족"
    assert cal.clarification_question is not None
    assert cal.all_day is True            # 날짜 없는 calendar → all_day
    assert cal.confidence <= 0.7
    assert risk.needs_confirmation is False


def test_scenario3_single_calendar_for_conflict():
    r = _run("다음 주 화요일 오전 10시에 팀 회의 잡자.")
    assert len(r.items) == 1
    cal = r.items[0]
    assert cal.type == "calendar" and cal.time == "10:00"
    assert cal.needs_confirmation is False  # 6-2가 기존 일정과 충돌 검증


def test_low_certainty_branches_to_class_ambiguous():
    # 보류(pending)는 type이 아니라 플래그: 분류 애매 → needs_confirmation
    item = finalize_item(LLMItem(
        type="task", title="기획서 다시 보기", type_certainty=0.5,
        date_status="missing", required_ok=True,
    ))
    assert item.needs_confirmation is True
    assert item.confirmation_reason == "분류 애매"   # 분류가 먼저, 완성도는 안 봄


def test_no_action_items_is_empty():
    # 입력 유형 라벨 없이, 실행 항목 없으면 빈 결과
    class Empty:
        def analyze(self, **_):
            return {"items": []}

    r = analyze(raw_text="ㅎㅇ", base_date=BASE, llm=Empty())
    assert r.items == []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")
