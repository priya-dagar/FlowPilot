import json
import os

POLICY_PATH = os.path.join(os.path.dirname(__file__), "leave_policy.json")

def load_leave_policy() -> dict:
    with open(POLICY_PATH, "r") as f:
        return json.load(f)

def get_policy_text() -> str:
    """Flatten policy into plain text for the agent's context."""
    policy = load_leave_policy()
    lines = [f"{r['id']}: {r['text']}" for r in policy["rules"]]
    return "\n".join(lines)