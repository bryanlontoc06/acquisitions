# security.py
import os
from typing import Any, List

from arcjet import Mode, arcjet, detect_bot, fixed_window
from fastapi import HTTPException, Request, status

arcjet_key = os.getenv("ARCJET_KEY")
assert arcjet_key is not None

rules: List[Any] = [
    detect_bot(mode=Mode.LIVE, allow=["CATEGORY:SEARCH_ENGINE", "CURL"]),
    fixed_window(
        mode=Mode.LIVE,
        max=5,  # Allow 5 requests per window
        window=10,
        characteristics=["ip.src"],
    ),
]

# Initialize the client once
aj = arcjet(key=arcjet_key, rules=rules)


async def verify_arcjet(request: Request):
    print("DEBUG: verify_arcjet function called!")
    decision = await aj.protect(request)
    print(f"DEBUG: Decision: {decision.conclusion}")

    if decision.is_denied():
        reason = decision.reason_v2

        print(f"Access denied: {reason.type}")
        # 1. Check if it's a Rate Limit using the 'type' attribute
        if reason.type == "RATE_LIMIT":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        # 2. Check if it's a Bot using the 'type' attribute
        if reason.type == "BOT":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bots are not allowed here.",
            )

        # Default fallback for other deny reasons (Shield, etc.)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request block by security policy.",
        )

    return decision
