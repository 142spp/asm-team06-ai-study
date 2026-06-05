# backend AGENTS.md (backend 정본)

FastAPI + LangGraph 기반 Action Router Agent 백엔드. backend 단독 uv 프로젝트.

상위 참조: 전체 구조/문서 맵은 루트 AGENTS.md / README.md에 있다. 폴더 밖 맥락은 루트 문서를 참조한다.
갱신 규칙: 이 폴더의 구조나 역할이 바뀌면 이 파일을 갱신한다.

## 구조

- `app/main.py` - FastAPI 인스턴스. `GET /health`, `/analyze/`, `/confirm/`, `/feedback/*` 라우터를 등록한다.
- `app/analysis/` - 6-1 분석 파이프라인(Context stub -> LLM -> 검증/재시도 -> completeness).
- `app/llm/` - Solar/FakeLLM 클라이언트. `UPSTAGE_API_KEY` 없으면 FakeLLM 폴백.
- `app/schemas/items.py` - 6-1 출력이자 6-2 입력인 공통 Item 정본.
- `app/conflict/`, `app/storage/`, `app/tools/` - 6-2 라우팅 기반 모듈(충돌검사, SQLite, Local Tool).

## 실행 (레포 루트 셸에서)

```bash
uv sync --directory backend
uv run --directory backend fastapi dev app/main.py
```

`fastapi[standard]`에 uvicorn/fastapi-cli가 포함되므로 별도 추가하지 않는다.

## 의존성 정책

- 현재 의존성: `fastapi[standard]`, `langgraph`, `langchain-upstage`, `pydantic`.
- dev 의존성: `pytest`.
- `langchain-upstage`가 의존하는 `tokenizers==0.20.3` 빌드/휠 호환성 때문에 Python은 3.12 계열(`>=3.12,<3.13`)로 제한한다.

## 코드 스타일

- Python은 PEP8 4-space를 따른다. 결정 이력은 `docs/decisions.md` 참조.
