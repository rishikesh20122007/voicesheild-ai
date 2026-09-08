from typing import Dict, List


# Configurable recommendation text per risk level. Kept as a simple
# dict so it's easy to edit wording or add localized versions later
# without touching the logic that selects them.

RECOMMENDATIONS: Dict[str, str] = {
    "LOW": (
        "Voice appears relatively safe, but continue normal verification. "
        "No unusual acoustic or contextual indicators were detected."
    ),
    "MEDIUM": (
        "Proceed carefully and independently verify the caller. "
        "Some indicators were detected that warrant extra caution."
    ),
    "HIGH": (
        "Potential voice impersonation detected. Do not share OTP, "
        "passwords, or sensitive information. Verify the identity through "
        "an independent communication channel before proceeding."
    ),
    "CRITICAL": (
        "High probability of AI-generated or impersonated voice. "
        "Stop sensitive actions and independently verify the person's "
        "identity through a separate, trusted channel immediately."
    ),
}

# Specific action items shown alongside the recommendation, based on
# risk level. These are suggestions only -- the system never performs
# irreversible actions automatically.

PREVENTION_ACTIONS: Dict[str, List[str]] = {
    "LOW": [
        "Continue the conversation normally.",
        "Stay generally aware of unusual requests.",
    ],
    "MEDIUM": [
        "Ask a question only the real person would know the answer to.",
        "Call back on a known, verified number if anything feels off.",
    ],
    "HIGH": [
        "Do not share OTPs, passwords, or account details.",
        "Hang up and call back using a verified, independent number.",
        "Do not proceed with any payment or transfer.",
    ],
    "CRITICAL": [
        "Do NOT share any sensitive information.",
        "Do NOT proceed with any payment, transfer, or account action.",
        "End the call/interaction and verify independently.",
        "Consider reporting the incident if a scam is confirmed.",
    ],
}


def get_prevention_response(risk_level: str) -> Dict:
    """
    Given a risk level (LOW/MEDIUM/HIGH/CRITICAL), return the
    recommendation text and specific prevention actions to display.
    """
    risk_level = risk_level.upper()

    recommendation = RECOMMENDATIONS.get(
        risk_level, "Unable to determine risk level. Proceed with caution."
    )
    actions = PREVENTION_ACTIONS.get(risk_level, [])

    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "actions": actions,
    }