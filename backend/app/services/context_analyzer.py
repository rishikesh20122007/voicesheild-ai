import re
from typing import Dict, List, Optional


# Transparent, rule-based keyword indicators. Designed so an NLP/LLM-based
# analyzer can later replace or augment this without changing the calling
# code -- see `analyze_context()`'s return shape.

URGENCY_PATTERNS = [
    r"\burgent(ly)?\b", r"\bimmediately\b", r"\bright now\b",
    r"\bemergency\b", r"\bhurry\b", r"\bas soon as possible\b", r"\basap\b",
]

OTP_PATTERNS = [
    r"\botp\b", r"\bone[\s-]?time password\b", r"\bverification code\b",
    r"\bsecurity code\b", r"\bpin\b",
]

CONFIDENTIAL_INFO_PATTERNS = [
    r"\bpassword\b", r"\bcvv\b", r"\bcard number\b", r"\baccount number\b",
    r"\bssn\b", r"\baadhaar\b", r"\bpan card\b", r"\bbank details\b",
]

MONEY_REQUEST_PATTERNS = [
    r"\btransfer\b", r"\bsend money\b", r"\bpay(ment)?\b", r"\bwire\b",
    r"\bgift card\b", r"\bdeposit\b",
]

IMPERSONATION_CLAIM_PATTERNS = [
    r"\bthis is your (ceo|boss|manager|father|mother|son|daughter)\b",
    r"\bi am calling from\b", r"\bthis is (the )?bank\b",
    r"\bgovernment official\b", r"\bpolice\b", r"\bincome tax\b",
]


def _matches_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def analyze_context(
    transcript: Optional[str] = None,
    description: Optional[str] = None,
    transaction_amount: Optional[float] = None,
) -> Dict:
    """
    Rule-based analysis of optional contextual text (call transcript,
    user description) and transaction amount, looking for indicators
    commonly associated with impersonation/social engineering scams.

    Returns a dict with:
      - indicators: list of human-readable detected indicator strings
      - context_risk_points: numeric contribution to the overall risk score (0-30)
    """
    combined_text = " ".join(filter(None, [transcript, description])).strip()

    indicators: List[str] = []
    context_risk_points = 0

    if combined_text:
        if _matches_any(combined_text, URGENCY_PATTERNS):
            indicators.append("Suspicious urgency detected")
            context_risk_points += 6

        if _matches_any(combined_text, OTP_PATTERNS):
            indicators.append("OTP/verification code request detected")
            context_risk_points += 10

        if _matches_any(combined_text, CONFIDENTIAL_INFO_PATTERNS):
            indicators.append("Request for confidential information detected")
            context_risk_points += 10

        if _matches_any(combined_text, MONEY_REQUEST_PATTERNS):
            indicators.append("Money transfer request detected")
            context_risk_points += 8

        if _matches_any(combined_text, IMPERSONATION_CLAIM_PATTERNS):
            indicators.append("Impersonation claim detected (e.g. authority/relative)")
            context_risk_points += 8

    if transaction_amount is not None and transaction_amount > 0:
        if transaction_amount >= 100000:
            indicators.append(f"Large transaction amount flagged (₹{transaction_amount:,.0f})")
            context_risk_points += 10
        elif transaction_amount >= 10000:
            indicators.append(f"Moderate transaction amount flagged (₹{transaction_amount:,.0f})")
            context_risk_points += 5

    # Cap contextual contribution so it can't alone push risk to CRITICAL
    context_risk_points = min(context_risk_points, 30)

    return {
        "indicators": indicators,
        "context_risk_points": context_risk_points,
    }