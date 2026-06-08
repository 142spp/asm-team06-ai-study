"""외부 연동 Tool (Google Calendar / Tasks).

local_tools 의 create_calendar_event / create_task 가 로컬 SQLite 저장 직후 여기 훅을
호출한다. 키(GOOGLE_REFRESH_TOKEN 등)가 없으면 no-op 이라 기존 로컬 데모/테스트는 그대로다.
키가 주입되면 로컬 저장 + 외부 생성이 함께 일어난다("토큰만 넣으면 동작").

의존성: httpx(이미 fastapi[standard] 에 포함) 로 raw REST 호출. google-api-python-client
같은 무거운 SDK 는 쓰지 않는다(의존성 0 추가).

인증: OAuth2 refresh token 흐름. refresh_token 으로 access_token 을 발급(만료 전 캐시)하고
Bearer 로 Calendar/Tasks API 를 호출한다. Calendar 와 Tasks 는 같은 Google OAuth 자격으로
커버되므로 한 번 셋업하면 둘 다 된다.

필요 환경변수(.env):
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN   # 필수(외부 활성)
    GOOGLE_CALENDAR_ID   # 선택, 기본 "primary"
    GOOGLE_TASKLIST_ID   # 선택, 기본 "@default"
    TOOL_EXTERNAL=google|off   # 선택. 미설정이면 refresh_token 유무로 자동 판단
"""

import os
import time
from datetime import date, datetime, timedelta

import httpx

from app.logging_config import get_logger

logger = get_logger("tools.external")

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
_TASKS_URL = "https://tasks.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks"
_TZ = "Asia/Seoul"
_HTTP_TIMEOUT = 10.0

# access_token 캐시(만료 전 재사용). time.monotonic 기준(벽시계 불필요).
_token_cache: dict[str, object] = {"token": None, "exp": 0.0}


def external_enabled() -> bool:
    """외부 연동을 켤지 판단한다.

    TOOL_EXTERNAL=off 면 강제 비활성, google 이면 강제 활성, 미설정이면 refresh_token
    유무로 자동 판단(LLM seam 의 키-자동감지와 같은 패턴).
    """
    mode = os.getenv("TOOL_EXTERNAL", "").strip().lower()
    if mode == "off":
        return False
    if mode == "google":
        return True
    return bool(os.getenv("GOOGLE_REFRESH_TOKEN"))


def _date_str(value: object) -> str | None:
    """date/datetime/str -> 'YYYY-MM-DD' (없으면 None)."""
    if value is None or value == "":
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    return str(value)[:10]


def _next_day(day: str) -> str:
    return (date.fromisoformat(day) + timedelta(days=1)).isoformat()


def _end_dt(day: str, hhmm: str, minutes: int) -> str:
    start = datetime.strptime(f"{day} {hhmm}", "%Y-%m-%d %H:%M")
    return (start + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")


def build_calendar_body(
    title: str,
    date_value: object = None,
    time_value: str | None = None,
    all_day: bool = False,
    duration_estimate: int | None = None,
) -> dict | None:
    """Item -> Google Calendar events.insert 바디. 날짜가 없으면 None(외부 푸시 스킵)."""
    day = _date_str(date_value)
    if not day:
        return None
    body: dict = {"summary": title}
    if time_value and not all_day:
        body["start"] = {"dateTime": f"{day}T{time_value}:00", "timeZone": _TZ}
        body["end"] = {
            "dateTime": _end_dt(day, time_value, duration_estimate or 60),
            "timeZone": _TZ,
        }
    else:
        # 종일 일정: Google 의 end.date 는 배타적이라 다음 날로 둔다.
        body["start"] = {"date": day}
        body["end"] = {"date": _next_day(day)}
    return body


def build_task_body(
    title: str,
    assignee: str | None = None,
    due_date: object = None,
    priority: str | None = None,
) -> dict:
    """Item -> Google Tasks tasks.insert 바디.

    Google Tasks 에는 담당자/우선순위 개념이 없어 notes 에 적는다.
    due 는 RFC3339(UTC)지만 Tasks 는 날짜만 의미 있게 쓴다.
    """
    body: dict = {"title": title}
    notes = []
    if assignee:
        notes.append(f"담당: {assignee}")
    if priority:
        notes.append(f"우선순위: {priority}")
    if notes:
        body["notes"] = " / ".join(notes)
    due = _date_str(due_date)
    if due:
        body["due"] = f"{due}T00:00:00.000Z"
    return body


def _access_token() -> str:
    """refresh_token 으로 access_token 발급(만료 전 캐시 재사용)."""
    cached = _token_cache.get("token")
    if cached and time.monotonic() < float(_token_cache.get("exp", 0.0)):
        return str(cached)

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    missing = [
        name
        for name, val in (
            ("GOOGLE_CLIENT_ID", client_id),
            ("GOOGLE_CLIENT_SECRET", client_secret),
            ("GOOGLE_REFRESH_TOKEN", refresh_token),
        )
        if not val
    ]
    if missing:
        raise RuntimeError(f"Google OAuth 환경변수 누락: {', '.join(missing)}")

    resp = httpx.post(
        _TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    token = payload["access_token"]
    # expires_in(보통 3600s) 에서 60s 여유를 빼고 캐시.
    _token_cache["token"] = token
    _token_cache["exp"] = time.monotonic() + float(payload.get("expires_in", 3600)) - 60
    logger.debug("Google access_token 갱신 완료(expires_in=%s)", payload.get("expires_in"))
    return token


def _post(url: str, body: dict) -> dict:
    resp = httpx.post(
        url,
        headers={"Authorization": f"Bearer {_access_token()}"},
        json=body,
        timeout=_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def try_push_calendar_event(
    *,
    title: str,
    date_value: object = None,
    time_value: str | None = None,
    all_day: bool = False,
    duration_estimate: int | None = None,
) -> str | None:
    """외부가 켜져 있으면 Google Calendar 에 이벤트를 만든다(반환=event id).

    비활성이면 no-op(None). 외부 실패는 삼키고 WARNING 만 남긴다(로컬 저장은 이미 끝났고
    데모가 외부 오류로 죽지 않게). 개인 지침: 외부 Tool 실패는 ERROR/WARNING 으로 기록.
    """
    if not external_enabled():
        return None
    body = build_calendar_body(title, date_value, time_value, all_day, duration_estimate)
    if body is None:
        logger.warning("외부 연동 스킵(Calendar): 날짜 없음 title=%s", title)
        return None
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    try:
        created = _post(_CALENDAR_URL.format(calendar_id=calendar_id), body)
        event_id = created.get("id")
        logger.info("외부 연동: Google Calendar 이벤트 생성 id=%s title=%s", event_id, title)
        return event_id
    except Exception as exc:  # noqa: BLE001 - 외부 실패는 로컬을 막지 않는다
        logger.warning(
            "외부 연동 실패(Calendar), 로컬만 저장: %s: %s", exc.__class__.__name__, exc
        )
        return None


def try_push_task(
    *,
    title: str,
    assignee: str | None = None,
    due_date: object = None,
    priority: str | None = None,
) -> str | None:
    """외부가 켜져 있으면 Google Tasks 에 할 일을 만든다(반환=task id). 규칙은 위와 동일."""
    if not external_enabled():
        return None
    body = build_task_body(title, assignee, due_date, priority)
    tasklist_id = os.getenv("GOOGLE_TASKLIST_ID", "@default")
    try:
        created = _post(_TASKS_URL.format(tasklist_id=tasklist_id), body)
        task_id = created.get("id")
        logger.info("외부 연동: Google Tasks 항목 생성 id=%s title=%s", task_id, title)
        return task_id
    except Exception as exc:  # noqa: BLE001 - 외부 실패는 로컬을 막지 않는다
        logger.warning(
            "외부 연동 실패(Tasks), 로컬만 저장: %s: %s", exc.__class__.__name__, exc
        )
        return None
