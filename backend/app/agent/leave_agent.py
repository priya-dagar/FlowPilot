import json
from datetime import date
from ..policies.policy_loader import get_policy_text
import re
from datetime import datetime

# Step 1: LLM extracts structured info from free text
def parse_leave_request(raw_text: str, llm_client) -> dict:
    prompt = f"""Extract leave request details from this employee message.

Return ONLY valid JSON in this exact shape:
{{"start_date": "YYYY-MM-DD" or null, "days_requested": integer or null, "clear": true/false}}

Rules:
- Extract the number of leave days.
- Extract the starting date if explicitly provided.
- Convert dates to YYYY-MM-DD.
- If the number of days is unclear, return null.
- Do not invent missing information.

Message: "{raw_text}"
"""

    # Try the real LLM first
    try:
        response = llm_client.complete(prompt)
        parsed = json.loads(response)

        if isinstance(parsed, dict):
            return parsed

    except Exception:
        # Gemini may be unavailable because of quota/network/API issues.
        # Fall back to deterministic local extraction.
        pass

    # Local fallback
    text = raw_text.lower()

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    days_requested = None

    # Numeric form: "4 days"
    match = re.search(r"\b(\d+)\s+days?\b", text)

    if match:
        days_requested = int(match.group(1))
    else:
        # Word form: "four days"
        for word, number in number_words.items():
            if re.search(rf"\b{word}\s+days?\b", text):
                days_requested = number
                break

    # Try common date formats
    start_date = None

    date_patterns = [
        r"\b(\d{4}-\d{2}-\d{2})\b",
        r"\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?\b",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, raw_text)

        if not match:
            continue

        try:
            if len(match.groups()) == 1:
                start_date = datetime.strptime(
                    match.group(1), "%Y-%m-%d"
                ).date().isoformat()
            else:
                month = match.group(1)
                day = match.group(2)
                year = match.group(3) or str(date.today().year)

                start_date = datetime.strptime(
                    f"{month} {day} {year}",
                    "%B %d %Y"
                ).date().isoformat()

            break

        except ValueError:
            try:
                month = match.group(1)
                day = match.group(2)
                year = match.group(3) or str(date.today().year)

                start_date = datetime.strptime(
                    f"{month} {day} {year}",
                    "%b %d %Y"
                ).date().isoformat()

                break

            except ValueError:
                pass

    return {
        "start_date": start_date,
        "days_requested": days_requested,
        "clear": days_requested is not None,
    }

# Step 2: Policy check (rule-based, using policy text as reference)
def check_policy(days_requested: int) -> dict:
    if days_requested is None:
        return {"decision": "unclear", "reason": "R5: days not specified"}
    if days_requested >= 3:
        return {"decision": "approval_required", "reason": "R3: 3+ days needs manager approval"}
    return {"decision": "auto_eligible", "reason": "R2: 1-2 days, no approval needed if balance ok"}

# Step 3: Balance check
def check_balance(leave_balance: int, days_requested: int) -> dict:
    if days_requested > leave_balance:
        return {"decision": "rejected", "reason": f"R4: requested {days_requested} exceeds balance {leave_balance}"}
    return {"decision": "ok", "reason": "sufficient balance"}

# Step 4: Orchestrator — ties it together, this is what the route will call
def run_leave_agent(raw_text: str, employee_balance: int, llm_client) -> dict:
    trace = []

    parsed = parse_leave_request(raw_text, llm_client)
    trace.append({
        "step": "parse_request",
        "detail": (
            f"Leave requested for {parsed.get('days_requested')} days "
            f"starting {datetime.strptime(parsed.get('start_date'), '%Y-%m-%d').strftime('%B %d, %Y')}"
        )
    })

    if parsed.get("days_requested") is None:
        trace.append({"step": "policy_check", "detail": "R5: ambiguous request, flagged"})
        return {"status": "needs_clarification", "trace": trace, "parsed": parsed}

    days = parsed["days_requested"]

    policy_result = check_policy(days)
    trace.append({"step": "policy_check", "detail": policy_result["reason"]})

    balance_result = check_balance(employee_balance, days)
    trace.append({"step": "balance_check", "detail": balance_result["reason"]})

    if balance_result["decision"] == "rejected":
        final_status = "rejected"
    elif policy_result["decision"] == "approval_required":
        final_status = "pending_approval"
    else:
        final_status = "approved"

    trace.append({"step": "final_decision", "detail": f"status={final_status}"})

    return {"status": final_status, "trace": trace, "parsed": parsed}