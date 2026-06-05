from typing import Any, TypedDict

# 팀 합의 필요: 각 단계 담당자가 사용하는 필드를 여기에 추가한다.
class AgentState(TypedDict, total=False):
    draft: dict[str, Any]            # 2단계 → 3단계로 넘어오는 초안
    confirmed_output: dict[str, Any] # 사용자 컨펌 결과 (3단계 입력)
    final_output: dict[str, Any]     # 3단계 → 최종 출력
