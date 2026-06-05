# Agent Design

LangGraph 흐름, LLM 입출력 계약, 모델 선택, 외부 연동(향후)을 담는다.

현재 구현 범위: 6-1 mock + 6-2 라우팅/검증/승인(`backend/app/agent/`). 6-1 분석은 mock,
6-3 피드백/선호는 feat/preferences 에 있고 그래프 연결부(seam) 뒤에 흡수 예정.
전체 3단계 흐름은 [planning.md](planning.md) 6장 참조.

## 1. 통합 토폴로지 - 단일 LangGraph + interrupt HITL

6-1 -> 6-2 -> 6-3 를 **하나의 StateGraph** 로 잇는다. 사용자 개입(승인)은 LangGraph
`interrupt()`로 그래프 중간에서 정지하고, checkpointer(MemorySaver) + `thread_id`(=session_id)로
상태를 보관했다가 `resume` 으로 재개한다. 단계 간 핸드오프는 `AgentState`(공유 상태)로 한다.

```
START -> analysis(6-1 mock) -> tool_selection -> conflict_check
      -> [reviewables 있으면] request_approval(interrupt) -> execution
      -> feedback_entry(6-3 seam) -> END
      ([reviewables 없으면] conflict_check -> feedback_entry 로 바로)
```

- 정본: `backend/app/agent/graph.py`(`build_graph`, MemorySaver 포함, lru_cache 로 1회 컴파일).
- 상태: `AgentState`(TypedDict, total=False, `backend/app/agent/state.py`).
- HTTP 표현: `POST /run`(시작->interrupt) / `POST /resume`(재개). [api-contract.md](api-contract.md) 참조.
- 항목 리스트 단위 분기(type별)는 각 노드 내부 루프로 처리.

## 2. 노드 입출력 계약

### analysis_node (`nodes/analysis.py`) - 6-1, 현재 mock
- 입력: `state["items"]`(mock 또는 6-1 산출) 또는 `raw_input`
- 처리: 현재는 items 통과(placeholder). 실제 6-1(LLM) 구현 시 raw_input -> items 생성으로 교체.
- 출력: `{items}`

### tool_selection_node (`nodes/tool_selection.py`)
- 입력: `state["items"]`
- 처리: id 정규화(`item-{idx}`) -> `type -> ToolName` 규칙 매핑 -> `routing_reason`. `ignore`는 `skipped`.
- 출력: `{items(정규화), selections, skipped}` / 로그: INFO

### conflict_check_node (`nodes/conflict_check.py`)
- 입력: `items`, `selections`, 저장소(calendar_events/tasks)
- 처리: calendar/task 만 검사. `conflict.rules.check_conflict`. `ReviewableItem(item+selection+conflict)` 구성.
- 출력: `{conflicts, reviewables}` / 로그: INFO, 충돌 시 WARNING

### request_approval_node (`nodes/approval.py`) - HITL
- 처리: `interrupt({reason, reviewables, skipped})` 로 정지. resume 값 = ApprovalDecision 리스트.
- 출력: `{decisions}` / 로그: INFO(승인 대기, 결정 수신)

### execution_node (`nodes/execution.py`)
- 입력: `reviewables`, `decisions`
- 처리(action별):
  - approve: **경량 재검증**(echo tool 불신, `item.type`에서 재도출) + 필수 필드 재확인 -> Tool 호출+저장.
    누락 시 Pending 폴백(`failed`), Tool 예외 시 Pending 폴백(`pending`).
  - modify: 저장 안 함, `recheck_required=true`(`needs_recheck`).
  - exclude: 저장 안 함(`excluded`).
- 출력: `{results, summary}` / 로그: INFO, Tool 실패 ERROR

### feedback_entry_node (`nodes/feedback_seam.py`) - 6-3 연결부
- 처리: `final_output`(Result Summary 입력) 구성 + 수정 항목 `(original, modified)` 쌍을 `modifications` 로 정리.
- 출력: `{final_output, modifications}`
- **6-3 seam**: 6-3 담당자는 이 노드 **다음에** 노드(Verification -> Feedback Analyzer ->
  선호 확인 interrupt -> Preference Store)를 붙인다. 현재는 END. `modifications` 는 6-3
  `/feedback/analyze(original, modified)` 와 맞물린다.

## 3. 충돌 검사 규칙 (`conflict/rules.py`, LLM 미사용)

- **Calendar (calendar_overlap)**: all_day 제외. 같은 일자 `[start, start+dur)` 범위 겹침
  (`new_start < ev_end AND ev_start < new_end`). dur 기본 60분. 대안: modify, pending.
- **Task (task_duplicate)**: 제목 정규화 후 완전일치 또는 토큰 Jaccard >= 0.6, 담당자 동일,
  마감일 +-1일 근접 -> 셋 다 만족 시 중복. 대안: merge(제안만), modify, pending.
- **Memo / Risk / Pending / Ignore**: 검사 없음.
- 병합(merge)은 제안만(자동 실행 없음, planning.md 제약).

## 4. 로깅 (시연 영상용)

정본: `backend/app/logging_config.py`. `agent.*` 네임스페이스.
- DEBUG: 노드 내부 / INFO: 분기,단계 전환 / WARNING: 충돌,Pending / ERROR: Tool 실패
- 레벨은 `ACTION_ROUTER_LOG_LEVEL` 로 조정.

## 5. LLM / 모델 선택 (미정)

- 6-2는 현재 **LLM 미사용**. Tool 선택은 규칙 매핑, 충돌 검사는 규칙 기반.
- LLM 보조 자리(미구현 `# TODO`): (a) Task 제목 유사도의 애매한 경계 판정, (b) modify 재검증.
- 6-1 분석(분해/분류/추출, analysis_node 교체)과 6-3 피드백 분석이 LLM 주 사용처.
- 모델(Solar 유력) 확정 시 LLM SDK 추가.

## 6. 외부 연동 (향후)

- 현재 모든 Tool은 로컬 SQLite mock(`tools/local_tools.py`).
- `create_calendar_event` 를 Google Calendar 등으로 대체 가능하나 현재 범위(로컬 데모) 밖.

## 7. Checkpointer / 세션

- 현재 **MemorySaver**(in-process). `thread_id = session_id`. 서버 재시작 시 세션 소멸(데모 충분).
- 영속이 필요하면 SqliteSaver 로 교체(langgraph-checkpoint-sqlite 의존성 추가). [decisions.md](decisions.md) 참조.

## 8. Mock 시연 데이터 정책

- `POST /mock/seed`(시연용 기존 데이터)와 `POST /mock/run/{scenario}`(6-1 출력 대체 입력)는
  **데모 초기화 전용**이다. 운영/일반 사용자 흐름이 아니며, "저장 전 사용자 승인" 대상과 무관한
  시연용 시스템 데이터를 다룬다. seed 는 `/run` 등 일반 경로에서 자동 실행하지 않는다.
