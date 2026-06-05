# backend AGENTS.md (backend 정본)

FastAPI + LangGraph 기반 Action Router Agent 백엔드. backend 단독 uv 프로젝트.

상위 참조: 전체 구조/문서 맵은 루트 AGENTS.md / README.md에 있다. 폴더 밖 맥락은 루트 문서를 참조한다.
갱신 규칙: 이 폴더의 구조나 역할이 바뀌면 이 파일을 갱신한다.

## 구조

- `app/main.py` - FastAPI 인스턴스. 현재는 `GET /health`만 존재.
- `app/` - 향후 Agent 코드/라우터를 둘 위치.
- (향후) LangGraph 노드/그래프, 프롬프트는 안정화 후 `docs/prompts`에서 backend로 이전한다.
- (향후) 데모 시나리오 테스트는 `docs/samples`에서 `backend/tests`로 이전한다.

## 실행 (레포 루트 셸에서)

```bash
uv sync --directory backend
uv run --directory backend fastapi dev app/main.py
```

`fastapi[standard]`에 uvicorn/fastapi-cli가 포함되므로 별도 추가하지 않는다.

## 의존성 정책

- 현재 의존성: `fastapi[standard]`, `langgraph`, `langchain-upstage`, `pydantic`.
- `langchain-upstage`가 의존하는 `tokenizers==0.20.3` 빌드/휠 호환성 때문에 Python은 3.12 계열(`>=3.12,<3.13`)로 제한한다.

## 코드 스타일 (미해결)

- CONTRIBUTING은 들여쓰기 Tab(Tab=4 spaces) 통일을 명시하나, Python은 PEP8/관용상 스페이스가 표준이라 충돌한다.
- 팀 확인 전까지 PEP8 4-space로 작성한다. 결정은 `docs/decisions.md`에 미해결로 기록한다.
