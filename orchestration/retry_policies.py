from config.settings import get_settings


def can_retry(state: dict) -> bool:
    return state.get("retry_count", 0) < get_settings().max_graph_retries
