"""분석 노드 (6-1) - 현재 mock.

6-1(비정형 텍스트 -> 분해/분류/추출)은 아직 미구현이다. 이 노드는 그래프 내 6-1의
자리를 잡아두는 placeholder로, 입력으로 받은 항목(mock 또는 6-1 산출)을 그대로 통과시킨다.
실제 6-1(LLM 기반)이 구현되면 raw_input 을 받아 items 를 생성하도록 교체한다.
"""

from app.logging_config import get_logger

logger = get_logger("node.analysis")


def analysis_node(state: dict) -> dict:
    items = state.get("items", [])
    raw_input = state.get("raw_input")
    if raw_input and not items:
        # 6-1 미구현: 비정형 텍스트만 들어오면 아직 분해할 수 없다.
        logger.warning(
            "6-1(mock): raw_input 이 들어왔으나 6-1 분석 미구현 -> 빈 items"
        )
        return {"items": []}
    logger.info("6-1(mock): %d 항목 입력 통과", len(items))
    return {"items": items}
