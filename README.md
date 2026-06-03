# asm-team06-ai-study - Action Router Agent

비정형 텍스트에서 실행 항목을 추출/분류하고 적절한 Tool로 라우팅하는 Action Router Agent 로컬 데모.
소마 AI 기술교육용 3주 과제 레포다.

## 모노레포 구조

- `frontend/` - 사용자 인터페이스. FE 스택은 미정(담당자 결정 후 작성).
- `backend/` - FastAPI + LangGraph 기반 Agent 백엔드.
- `docs/` - 설계/계약/결정 문서.

## 문서 맵

- `docs/planning.md` - 기획서(과제 정의, 범위, 시나리오). ※ 작성자가 직접 관리.
- `docs/api-contract.md` - FE <-> BE HTTP 계약.
- `docs/data-model.md` - 항목/출력 JSON 스키마 + 저장소 스키마.
- `docs/agent-design.md` - LangGraph 흐름 + LLM 입출력 계약 + 모델 선택 + 외부연동(향후).
- `docs/decisions.md` - 변경/결정 이력 + 프롬프트 변경 로그.
- `docs/prompts/` - 프롬프트 텍스트 보관(안정화 후 backend로 이전 예정).
- `docs/samples/` - 데모 시나리오 입력/기대출력 보관(안정화 후 backend/tests로 이전 예정).
- `.github/CONTRIBUTING.md` - 브랜치/커밋/코드스타일 규칙(정본).
- `.github/PULL_REQUEST_TEMPLATE.md` - PR 양식.

## 확정 / 미정 스택

- 확정: Python / FastAPI(BE) / LangGraph / Pydantic.
- 미정: FE 스택(담당자 결정), Agent용 LLM(Solar 유력, 필요시 Gemini/Claude/GPT), 저장소(SQLite or JSON).

## 실행 방법

backend는 backend 단독 uv 프로젝트다. 레포 루트 셸에서 다음을 실행한다.

```bash
# 의존성 설치(.venv + uv.lock 생성)
uv sync --directory backend

# 개발 서버 기동 (GET /health -> {"status":"ok"})
uv run --directory backend fastapi dev app/main.py
```

`--directory backend`는 서브프로세스의 작업 디렉토리만 backend로 옮긴다. 사람과 에이전트는 레포 루트 셸을 유지한다.

## 개인 지침 설정

팀원 각자 `~/.claude/action-router.md`를 만들면 루트 `CLAUDE.md`가 이를 자동 import한다(개인 작업 규칙 레이어).
이 파일은 레포에 커밋되지 않는다. 파일이 없어도 설정은 깨지지 않으며, 개인 레이어만 로드되지 않을 뿐이다
(첫 실행 시 import 승인 1회 필요).

## 에이전트 실행 규칙

- AI 에이전트(Claude Code / Codex)는 반드시 레포 루트에서 기동하고, 코드 실행 위치도 루트로 통일한다.
- 전체 구조/폴더 역할/문서 맵이 바뀌면 이 루트 문서(README.md / AGENTS.md)를 갱신한다.
  특정 폴더 내부만 바뀌면 해당 폴더의 AGENTS.md / README.md를 갱신한다.
