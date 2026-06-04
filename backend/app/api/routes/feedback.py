from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.feedback.analyzer import detect_diff, determine_pattern_type, generate_candidates
from app.feedback.db import (
    get_candidate_log,
    load_user_preferences,
    save_candidate_log,
    save_user_preference,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class AnalyzeRequest(BaseModel):
    session_id: str
    original: dict[str, Any]
    modified: dict[str, Any]


class Candidate(BaseModel):
    field: str
    original: Any
    preferred: Any


class AnalyzeResponse(BaseModel):
    session_id: str
    log_id: int
    pattern_type: Literal["one_time", "recurring"]
    candidates: list[Candidate]
    final_output: dict[str, Any]


class ConfirmRequest(BaseModel):
    session_id: str
    log_id: int
    action: Literal["save", "dismiss"]
    candidates: list[Candidate]  # 사용자가 앞으로 적용하기로 선택한 후보 (일부만 가능)


class ConfirmResponse(BaseModel):
    session_id: str
    saved: bool
    saved_fields: list[str]       # 저장된 선호 필드 목록 (dismiss 시 빈 리스트)
    final_output: dict[str, Any]  # 최종 수정안 요약


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    diff = detect_diff(body.original, body.modified)
    existing_prefs = load_user_preferences()
    pattern_type = determine_pattern_type(diff, existing_prefs)
    candidates = generate_candidates(diff)

    log_id = save_candidate_log(
        session_id=body.session_id,
        original=body.original,
        modified=body.modified,
        diff=diff,
        pattern_type=pattern_type,
        candidates=candidates,
    )

    return AnalyzeResponse(
        session_id=body.session_id,
        log_id=log_id,
        pattern_type=pattern_type,
        candidates=[Candidate(**c) for c in candidates],
        final_output=body.modified,
    )


@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_preference(body: ConfirmRequest) -> ConfirmResponse:
    log = get_candidate_log(body.log_id)
    final_output = log["modified"] if log else {}

    if body.action == "dismiss" or not body.candidates:
        return ConfirmResponse(
            session_id=body.session_id,
            saved=False,
            saved_fields=[],
            final_output=final_output,
        )

    for candidate in body.candidates:
        save_user_preference(
            field=candidate.field,
            original_pattern=candidate.original,
            preferred=candidate.preferred,
        )

    return ConfirmResponse(
        session_id=body.session_id,
        saved=True,
        saved_fields=[c.field for c in body.candidates],
        final_output=final_output,
    )
