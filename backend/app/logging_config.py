"""Agent 분기/단계 로깅 설정 (시연 영상용).

레벨 사용 기준 (개인 작업 지침):
- DEBUG:   노드 내부 상세
- INFO:    분기/단계 전환
- WARNING: confidence 낮음, Pending 처리, 충돌 감지
- ERROR:   Tool 실패

`agent` 네임스페이스 하위 로거(agent.node.*, agent.conflict 등)를 사용한다.
"""

import logging
import os

_CONFIGURED = False
_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: int | str | None = None) -> logging.Logger:
    """agent 로거를 1회 설정하고 돌려준다 (멱등).

    레벨은 인자 > 환경변수 ACTION_ROUTER_LOG_LEVEL > INFO 순으로 결정.
    """
    global _CONFIGURED
    agent_logger = logging.getLogger("agent")

    if level is None:
        level = os.environ.get("ACTION_ROUTER_LOG_LEVEL", "INFO")
    # 표준 레벨명은 대문자만 유효하다. env/인자로 'debug' 같은 소문자가 와도
    # setLevel 이 ValueError 로 부팅을 깨뜨리지 않도록 정규화한다.
    if isinstance(level, str):
        level = level.upper()
    agent_logger.setLevel(level)

    if not _CONFIGURED:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        agent_logger.addHandler(handler)
        agent_logger.propagate = False
        _CONFIGURED = True

    return agent_logger


def get_logger(name: str) -> logging.Logger:
    """`agent.<name>` 로거를 돌려준다."""
    return logging.getLogger(f"agent.{name}")
