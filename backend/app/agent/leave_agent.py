import json
from datetime import date
from ..policies.policy_loader import get_policy_text
import re
from datetime import datetime
from datetime import timedelta

# Step 1: LLM extracts structured info from free text
def parse_leave_request(raw_text: str, llm_client) -> dict:
    prompt = f"""Extract leave request details from this employee message.

Return ONLY valid JSON in this exact shape:
{{
    "start_date": "YYYY-MM-DD" or null,
    "days_requested": integer or null,
    "clear": true/false
}}

Rules:
- Extract the number of leave days.
- Extract the starting date if explicitly or naturally provided.
- Understand absolute dates such as:
  - October 5
  - October 5th
  - 5 October
  - 2026-10-05
- Understand relative dates such as:
  - today
  - tomorrow
  - Monday
  - next Monday
  - Tuesday, Wednesday, etc.
- Resolve relative dates using today's date.
- If the number of days is unclear, return null.
- If the start date is unclear, return null.
- Do not invent missing information.

Message: "{raw_text}"
"""

    # ---------------------------------------------------------
    # 1. Try Gemini first
    # ---------------------------------------------------------
    try:
        response = llm_client.complete(prompt)
        parsed = json.loads(response)

        if isinstance(parsed, dict):
            return {
                "start_date": parsed.get("start_date"),
                "days_requested": parsed.get("days_requested"),
                "clear": parsed.get("clear", False),
            }

    except Exception:
        # Gemini can fail because of quota, network, API errors, etc.
        # The deterministic fallback below will handle common requests.
        pass

    # ---------------------------------------------------------
    # 2. Deterministic fallback parser
    # ---------------------------------------------------------
    text = raw_text.lower().strip()
    today = date.today()

    # ---------- Extract number of days ----------
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
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
    }

    days_requested = None

    numeric_match = re.search(
        r"\b(\d+)\s*(?:day|days)\b",
        text
    )

    if numeric_match:
        days_requested = int(numeric_match.group(1))
    else:
        for word, number in number_words.items():
            if re.search(rf"\b{word}\s*(?:day|days)\b", text):
                days_requested = number
                break

    # ---------- Extract start date ----------
    start_date = None

    # 1. YYYY-MM-DD
    iso_match = re.search(
        r"\b(\d{4}-\d{2}-\d{2})\b",
        text
    )

    if iso_match:
        try:
            parsed_date = datetime.strptime(
                iso_match.group(1),
                "%Y-%m-%d"
            ).date()

            start_date = parsed_date.isoformat()
        except ValueError:
            pass

    # 2. Month Day
    if start_date is None:
        month_day_match = re.search(
            r"\b("
            r"january|february|march|april|may|june|july|"
            r"august|september|october|november|december"
            r")\s+(\d{1,2})(?:st|nd|rd|th)?"
            r"(?:,?\s+(\d{4}))?\b",
            text,
        )

        if month_day_match:
            month = month_day_match.group(1)
            day = month_day_match.group(2)
            year = month_day_match.group(3) or str(today.year)

            try:
                parsed_date = datetime.strptime(
                    f"{month} {day} {year}",
                    "%B %d %Y",
                ).date()

                start_date = parsed_date.isoformat()
            except ValueError:
                pass

    # 3. Day Month
    if start_date is None:
        day_month_match = re.search(
            r"\b(\d{1,2})(?:st|nd|rd|th)?\s+"
            r"(january|february|march|april|may|june|july|"
            r"august|september|october|november|december)"
            r"(?:,?\s+(\d{4}))?\b",
            text,
        )

        if day_month_match:
            day = day_month_match.group(1)
            month = day_month_match.group(2)
            year = day_month_match.group(3) or str(today.year)

            try:
                parsed_date = datetime.strptime(
                    f"{day} {month} {year}",
                    "%d %B %Y",
                ).date()

                start_date = parsed_date.isoformat()
            except ValueError:
                pass

    # 4. Today
    if start_date is None and re.search(r"\btoday\b", text):
        start_date = today.isoformat()

    # 5. Tomorrow
    if start_date is None and re.search(r"\btomorrow\b", text):
        start_date = (
            today + timedelta(days=1)
        ).isoformat()

    # 6. Yesterday — technically parseable, but leave requests
    # for past dates should later be rejected by policy.
    if start_date is None and re.search(r"\byesterday\b", text):
        start_date = (
            today - timedelta(days=1)
        ).isoformat()

    # 7. "next Monday", "next Tuesday", etc.
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    weekday_pattern = (
        r"\b(?:next\s+)?"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    )

    weekday_match = re.search(weekday_pattern, text)

    if start_date is None and weekday_match:
        weekday_name = weekday_match.group(1)
        target_weekday = weekdays[weekday_name]

        days_ahead = (
            target_weekday - today.weekday()
        ) % 7

        # "next Monday" should mean the upcoming Monday.
        # If today itself is Monday, next Monday = 7 days away.
        if "next" in weekday_match.group(0) and days_ahead == 0:
            days_ahead = 7

        start_date = (
            today + timedelta(days=days_ahead)
        ).isoformat()

    return {
        "start_date": start_date,
        "days_requested": days_requested,
        "clear": (
            days_requested is not None
            and start_date is not None
        ),
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
    start_date = parsed.get("start_date")
    days_requested = parsed.get("days_requested")

    if start_date:
        formatted_date = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).strftime("%B %d, %Y")

        parse_detail = (
            f"Leave requested for {days_requested} days "
            f"starting {formatted_date}"
        )
    else:
        parse_detail = (
            f"Leave requested for {days_requested} days "
            f"(start date not specified)"
        )

    trace.append({
        "step": "parse_request",
        "detail": parse_detail,
    })

    if (
        parsed.get("days_requested") is None
        or parsed.get("start_date") is None
    ):
        trace.append({"step": "policy_check", "detail": "R5: start date or number of days is missing, clarification required"})
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