from typing import List, Optional


def fetch_logs(request_id: Optional[str]) -> List[str]:
    # In real implementation, query Elasticsearch/Loki by request_id or time window.
    if not request_id:
        return []
    # return a small fake context
    return [
        f"[INFO] request_id={request_id} start processing",
        f"[ERROR] request_id={request_id} database timeout after 30s",
        f"[INFO] request_id={request_id} end processing",
    ]
