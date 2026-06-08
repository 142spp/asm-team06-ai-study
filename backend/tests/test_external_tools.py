"""외부 연동 Tool(Google Calendar/Tasks) 단위 테스트.

실제 Google API 는 호출하지 않는다. enabled 분기/페이로드 변환/훅 호출만 검증한다.
키가 없으면(기본) no-op 이라 기존 로컬 데모/테스트가 그대로라는 것도 확인한다.
"""

from datetime import date

import pytest

from app.tools import external


@pytest.fixture(autouse=True)
def _clear_external_env(monkeypatch):
    # 외부 관련 env 를 깨끗이 비운 상태에서 시작(자동감지 기본=off).
    for key in (
        "TOOL_EXTERNAL",
        "GOOGLE_REFRESH_TOKEN",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_CALENDAR_ID",
        "GOOGLE_TASKLIST_ID",
    ):
        monkeypatch.delenv(key, raising=False)
    external._token_cache["token"] = None
    external._token_cache["exp"] = 0.0


# --- external_enabled 분기 -------------------------------------------------

def test_disabled_by_default_without_token():
    assert external.external_enabled() is False


def test_enabled_when_refresh_token_present(monkeypatch):
    monkeypatch.setenv("GOOGLE_REFRESH_TOKEN", "rt")
    assert external.external_enabled() is True


def test_off_overrides_token(monkeypatch):
    monkeypatch.setenv("GOOGLE_REFRESH_TOKEN", "rt")
    monkeypatch.setenv("TOOL_EXTERNAL", "off")
    assert external.external_enabled() is False


def test_google_forces_on_without_token(monkeypatch):
    monkeypatch.setenv("TOOL_EXTERNAL", "google")
    assert external.external_enabled() is True


# --- 페이로드 변환 ---------------------------------------------------------

def test_calendar_body_timed_event_has_start_end():
    body = external.build_calendar_body(
        "팀 회의", date(2026, 6, 12), "10:00", all_day=False, duration_estimate=90
    )
    assert body["summary"] == "팀 회의"
    assert body["start"]["dateTime"] == "2026-06-12T10:00:00"
    assert body["end"]["dateTime"] == "2026-06-12T11:30:00"  # +90분
    assert body["start"]["timeZone"] == "Asia/Seoul"


def test_calendar_body_all_day_uses_exclusive_end():
    body = external.build_calendar_body("워크샵", date(2026, 6, 12), None, all_day=True)
    assert body["start"]["date"] == "2026-06-12"
    assert body["end"]["date"] == "2026-06-13"  # end.date 는 배타적


def test_calendar_body_none_when_no_date():
    assert external.build_calendar_body("날짜없음", None) is None


def test_task_body_packs_assignee_priority_into_notes():
    body = external.build_task_body("발표자료", assignee="박성종", due_date=date(2026, 6, 8), priority="high")
    assert body["title"] == "발표자료"
    assert "담당: 박성종" in body["notes"]
    assert "우선순위: high" in body["notes"]
    assert body["due"].startswith("2026-06-08T")


# --- try_push_* 게이트 -----------------------------------------------------

def test_try_push_calendar_noop_when_disabled():
    # 비활성이면 None 반환 + 외부 호출 없음.
    assert external.try_push_calendar_event(title="x", date_value=date(2026, 6, 12)) is None


def test_try_push_task_noop_when_disabled():
    assert external.try_push_task(title="x") is None


def test_try_push_calendar_posts_when_enabled(monkeypatch):
    monkeypatch.setenv("TOOL_EXTERNAL", "google")
    captured = {}

    def fake_post(url, body):
        captured["url"] = url
        captured["body"] = body
        return {"id": "evt_123"}

    monkeypatch.setattr(external, "_post", fake_post)
    monkeypatch.setenv("GOOGLE_CALENDAR_ID", "primary")

    result = external.try_push_calendar_event(
        title="팀 회의", date_value=date(2026, 6, 12), time_value="10:00"
    )
    assert result == "evt_123"
    assert "calendars/primary/events" in captured["url"]
    assert captured["body"]["summary"] == "팀 회의"


def test_try_push_swallows_external_error(monkeypatch):
    # 외부 실패는 예외를 던지지 않고 None(로컬은 이미 저장됨).
    monkeypatch.setenv("TOOL_EXTERNAL", "google")

    def boom(url, body):
        raise RuntimeError("google down")

    monkeypatch.setattr(external, "_post", boom)
    assert external.try_push_task(title="x") is None


# --- local_tools 통합: 외부 OFF 면 기존 로컬 동작 그대로 -------------------

def test_local_tool_still_works_when_external_disabled(tmp_db):
    from app.tools.local_tools import create_calendar_event

    pk = create_calendar_event("로컬 일정", date(2026, 6, 12), "10:00")
    assert isinstance(pk, int) and pk >= 1
