from typing import Dict


def notify(diagnosis: Dict[str, str]):
    # In production, this would post to Slack/Feishu with richer formatting and actions.
    print("[ChatOps] Notification:", diagnosis)
