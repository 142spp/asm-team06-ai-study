# Decisions

변경/결정 이력을 담는다.

## 2026-06-05 - 코드 들여쓰기 규칙 확정 (Tab -> 4 Spaces)

- **확정: Python 들여쓰기는 PEP8 4 Spaces** (Tab 문자 미사용). CONTRIBUTING의 기존
  "Tab(=4 Spaces)" 규칙을 4 Spaces 로 변경. 기존 코드(backend, feat/preferences)가 이미
  스페이스이고 Python 표준이라 코드 변경은 없다. (이전까지 '미해결'이던 항목을 해결.)

## 2026-06-05 - 통합 토폴로지: 단일 LangGraph + interrupt HITL

- **확정: 6-1 -> 6-2 -> 6-3 를 하나의 LangGraph 로 통합한다.** 단계 간 핸드오프는
  `AgentState`(공유 상태). 사용자 개입(승인 등)은 LangGraph `interrupt()`로 그래프 중간에서
  정지하고, **checkpointer(MemorySaver) + thread_id(=session_id)** 로 상태를 보관했다가 재개한다.
- **HTTP 표현**: `POST /run`(시작 -> 승인 지점 interrupt) -> `POST /resume`(사용자 결정으로 재개).
  HITL이 있으므로 호출은 최소 2회. (대안이던 "단계별 HTTP 분리 / 무상태 2-call(/route,/approve)"는
  폐기. 흐름 제어와 상태를 그래프 한 곳에 모으기 위함.)
- **checkpointer = MemorySaver**(in-process, 데모용). 서버 재시작 시 세션 소멸. 영속 필요 시
  SqliteSaver 로 교체(의존성 추가).
- **6-3 연결부(seam)**: 6-2 그래프는 `feedback_entry` 노드에서 끝나고(현재 END), 6-3 담당자가
  그 뒤에 노드를 붙여 흡수한다. 6-2는 `final_output` + 수정 `(original, modified)` 쌍을 상태로 넘긴다.

## 2026-06-05 - 6-2 라우팅/검증/승인

- **저장소: SQLite 단일 파일 `backend/storage.db`** (테이블 분리). planning.md 정본이자
  feat/preferences의 SQLite 노선과 일관. 신규 의존성 0. 경로는 `ACTION_ROUTER_DB_PATH`
  env var / `configure_db_path()` 훅으로 주입 가능(테스트 격리).
- **Tool 선택 / 충돌 검사 LLM 미사용 (규칙 기반)**. type->tool 매핑, calendar 시간 겹침,
  task 제목 Jaccard>=0.6 + 담당자 + 마감 근접. LLM 보조는 `# TODO` 훅만(모델 미정).
- **승인 시 경량 재검증**: 실행 직전 `item.type`에서 tool 재도출 + 필수 필드 재확인. 누락/실패 시 Pending 폴백.
- **pytest를 `[dependency-groups] dev`로 추가** (런타임 의존성 아님). 실행:
  `uv run --directory backend pytest`.
- **feat/preferences `feedback.db`와 DB 통합은 6-3 그래프 흡수 시 재결정** (현재는 storage.db 단일).
- **seed는 데모 전용**: `POST /mock/seed` / 테스트 fixture에서만 실행. 일반 요청 경로
  자동 실행 금지("저장 전 사용자 승인" 제약과 구분되는 시연용 시스템 데이터).

## 2026-06-08 - 외부 연동(Google Calendar/Tasks) Tool 내장

- **백엔드 소스코드에 직접 내장**(에이전트/MCP 대행 PoC 아님). `tools/external.py` 푸시 훅을
  `local_tools.create_calendar_event`/`create_task` 에 얹어, 로컬 SQLite 저장 + 외부 생성을 함께.
- **seam = 키 자동감지**(LLM seam 과 동일): 키 없으면 no-op(로컬만) -> 기존 데모/테스트 무변경.
  `.env` 에 OAuth 자격(서버 단일 계정 refresh token) 주입 시 자동 활성. `TOOL_EXTERNAL` 로 강제.
- **의존성 0 추가**: `fastapi[standard]` 의 `httpx` 로 raw REST. google SDK 미사용(무게/휠 회피).
- **FE 무변경**: 서버 단일 계정 방식이라 사용자별 OAuth 로그인 없음. `execution_node`/스키마/계약 불변.
- **실패 정책**: 외부 실패는 WARNING 으로 삼키고 로컬 저장 유지(데모가 외부 오류로 죽지 않게).
- **범위 메모**: planning/AGENTS 의 "외부 실시간 연동 제외"를 데모 한정으로 완화. 단일 계정 푸시까지만,
  멀티유저 OAuth/양방향 동기화는 여전히 범위 밖.

## 2026-06-08 - 외부 연동 양방향(읽기) + 테스트 격리

- **conflict_check 가 구글도 읽는다**: 로컬 storage + `fetch_calendar_events`/`fetch_tasks`(구글)를
  합쳐 충돌/중복을 검사. 구글 데이터는 로컬 dict 형식으로 변환(`calendar_event_to_local`/`task_to_local`).
  이전 단방향(쓰기만)에서 "출력은 미러, 입력은 로컬 폐쇄계"였던 비대칭을 해소.
- **read 폴백**: 외부 off/조회 실패 시 빈 list -> 로컬만으로 검사 계속(구글 장애가 분석을 멈추지 않음).
  쓰기(push) 폴백과 같은 best-effort 원칙.
- **테스트 격리(중요)**: `.env` 에 토큰을 넣으면 `main.py` load_dotenv 로 그 값이 테스트에도 로드되어
  conflict_check(읽기)/execution(쓰기)이 실제 구글 API 를 호출(네트워크 의존 + 실제 캘린더 변경)했다.
  `conftest.py` autouse fixture 로 모든 테스트에서 `TOOL_EXTERNAL=off` 강제(외부 자체 테스트만 자체 제어).
- **events.list timeMin**: `fetch_calendar_events` 는 `timeMin`(어제~)으로 조회한다. timeMin 없이
  orderBy=startTime 이면 먼 과거의 반복 일정(생일 등)이 maxResults 를 채워 정작 충돌 대상인 미래
  일정이 잘린다(실제 e2e 검증에서 발견). 어제부터 조회해 오늘/미래 일정을 충돌 검사에 포함한다.
- **한계**: 구글 timed 이벤트 시각은 offset 의 로컬 표기를 그대로 사용(KST 가정). 다른 timezone 의
  외부 이벤트 정확 환산, item 날짜 기준 timeMax 범위 최적화는 데모 범위 밖.

## 2026-06-08 - 저장된 선호 재주입(D3) 연결

- **`load_context()` 가 6-3 `feedback.db` 의 `load_user_preferences()` 를 호출**해 저장된
  선호를 `ContextBundle.preferences` 로 채운다. 그동안 stub(빈 컨텍스트)이라 저장만 되고
  분석에 반영되지 않던 경로(D3)를 연결. 읽기 함수/프롬프트 주입점은 이미 준비돼 있었고,
  비어있던 `load_context()` 만 채웠다.
- **선호 로드 실패는 분석을 막지 않는다**: DB 오류 시 빈 선호로 폴백(WARNING 로그)하고
  분석을 계속 진행한다. 선호가 실제로 주입될 때만 INFO 로그(시연 영상용 분기 기록).
- **후속(같은 브랜치에서 구현 완료)**: 기존 항목 요약 주입, Guideline(D4) JSON 주입,
  `_postprocess` 선호 코드 보정까지 이어서 채웠다. Context Loader stub 전반이 실데이터로 연결됨.

## 2026-06-08 - _postprocess 선호 코드 보정(이중 안전장치)

- LLM 출력(`AnalyzeResult.items`)을 코드가 한 번 더 검사해 저장된 선호대로 강제 치환한다.
  프롬프트 주입(D3)은 확률적이라 가끔 무시되므로, 코드 후보정으로 결정적 보장을 더한다.
- 필드값은 `model_dump(mode="json")` 기준으로 비교/치환하고 `Item.model_validate` 로 재검증해
  date/enum 타입을 강제한다(model_copy 의 무검증 치환 회피).

## 미해결

- (없음)

## 프롬프트 변경 로그

### 2026-06-08 - Solar 시스템 프롬프트: User Preference 반영 규칙 추가

- `app/llm/solar.py` `_SYSTEM` 에 규칙 1줄 추가. User Preference 가 주어지면 같은 field 에서
  입력이 해당 original_pattern 상황일 때 과거 선택값(preferred)을 기본값으로 반영하되,
  입력에 명시적 값이 있으면 입력을 우선하도록 명시.
- 배경: 선호가 프롬프트(human 메시지)에 실리고는 있었으나 활용 지시가 없어 LLM 이 무시할 수
  있었다. 재주입(D3) 연결과 함께 실제 반영되도록 규칙화.

### 2026-06-08 - Solar 시스템 프롬프트: Guideline 반영 규칙 추가

- `app/llm/solar.py` `_SYSTEM` 에 규칙 1줄 추가. Guideline 이 주어지면 분석/분류 시 그 지침을
  따르되 입력과 충돌하면 입력을 우선하도록 명시.
- 배경: D4 지침을 `guidelines.json` 으로 주입(`load_context`)하면서, User Preference 와 같은
  이유로 활용 지시를 프롬프트에 명시.
