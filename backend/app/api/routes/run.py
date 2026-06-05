"""6-1~6-2 단일 그래프 HTTP 엔드포인트 (interrupt/resume 기반 HITL).

- POST /run            : 그래프 시작 -> 승인 지점(interrupt)에서 정지, reviewables 반환
- POST /resume         : 사용자 결정(decisions)으로 그래프 재개 -> 실행 + 요약
- GET  /storage/{kind} : 저장소 행 조회 (데모 확인용)
- POST /mock/seed      : 시연용 시스템 데이터 초기화 (데모 전용, 일반 흐름 아님)
- POST /mock/run/{scenario} : Mock 시나리오를 /run 으로 흘려보내는 데모 트리거

세션 상태는 MemorySaver(checkpointer)에 session_id(=thread_id)로 보관된다.
"""

from fastapi import APIRouter, HTTPException
from langgraph.types import Command

from app.agent.graph import build_graph
from app.mock_data import SAMPLE_SCENARIOS, get_scenario
from app.schemas.run import ResumeRequest, RunRequest, RunResponse, RunStatus
from app.storage.db import TABLES
from app.storage.queries import list_table
from app.storage.seed import seed_if_empty

router = APIRouter(tags=["routing"])


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _to_response(session_id: str, result: dict) -> RunResponse:
    """그래프 invoke 결과를 응답으로 변환. interrupt 면 승인 대기, 아니면 완료."""
    interrupts = result.get("__interrupt__")
    if interrupts:
        payload = interrupts[0].value
        return RunResponse(
            session_id=session_id,
            status=RunStatus.awaiting_approval,
            reviewables=payload.get("reviewables", []),
            skipped=payload.get("skipped", []),
        )
    return RunResponse(
        session_id=session_id,
        status=RunStatus.completed,
        results=result.get("results", []),
        summary=result.get("summary", {}),
        final_output=result.get("final_output"),
    )


@router.post("/run", response_model=RunResponse)
def run(req: RunRequest) -> RunResponse:
    """그래프 시작. 승인 지점에서 정지하고 검토 패키지를 반환한다."""
    graph = build_graph()
    result = graph.invoke(
        {
            "session_id": req.session_id,
            "items": [it.model_dump(mode="json") for it in req.items],
            "raw_input": req.raw_input,
        },
        _config(req.session_id),
    )
    return _to_response(req.session_id, result)


@router.post("/resume", response_model=RunResponse)
def resume(req: ResumeRequest) -> RunResponse:
    """사용자 결정으로 그래프 재개. approve 만 저장된다."""
    graph = build_graph()
    result = graph.invoke(
        Command(resume=[d.model_dump(mode="json") for d in req.decisions]),
        _config(req.session_id),
    )
    return _to_response(req.session_id, result)


@router.get("/storage/{kind}")
def storage(kind: str) -> dict:
    """저장소 테이블 행 조회 (데모 확인용)."""
    try:
        rows = list_table(kind)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"알 수 없는 저장소 종류: {kind}. 가능: {sorted(TABLES)}",
        )
    return {"kind": kind, "count": len(rows), "rows": rows}


@router.post("/mock/seed")
def mock_seed() -> dict:
    """시연용 시스템 데이터 초기화.

    데모 전용 엔드포인트다. 운영/일반 사용자 흐름이 아니며, 루트 지침의
    "저장 전 사용자 승인" 대상과 무관한 시연용 시스템 데이터를 넣는다.
    """
    return {"seeded": seed_if_empty()}


@router.post("/mock/run/{scenario}", response_model=RunResponse)
def mock_run(scenario: str) -> RunResponse:
    """Mock 시나리오 입력을 /run 으로 흘려보내는 데모 트리거."""
    try:
        payload = get_scenario(scenario)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"알 수 없는 시나리오: {scenario}. 가능: {sorted(SAMPLE_SCENARIOS)}",
        )
    return run(RunRequest.model_validate(payload))
