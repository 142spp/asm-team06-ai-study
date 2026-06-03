# backend

FastAPI + LangGraph 기반 Action Router Agent 백엔드. backend 단독 uv 프로젝트다.

상위 참조: 전체 구조/문서 맵은 루트 README.md / AGENTS.md에 있다. 폴더 밖 맥락은 루트 문서를 참조한다.
갱신 규칙: 이 폴더의 구조나 역할이 바뀌면 이 파일을 갱신한다.

## 실행 (레포 루트 셸에서)

```bash
# 의존성 설치(.venv + uv.lock 생성)
uv sync --directory backend

# 개발 서버 기동 (GET /health -> {"status":"ok"})
uv run --directory backend fastapi dev app/main.py
```

`--directory backend`는 서브프로세스 cwd만 backend로 옮긴다. 사람과 에이전트는 루트 셸을 유지한다.
