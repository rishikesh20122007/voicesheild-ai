from typing import Dict, List, Tuple


# Risk level thresholds (0-100 scale)
RISK_THRESHOLDS = {
    "LOW": (0, 25),
    "MEDIUM": (26, 50),
    "HIGH": (51, 75),
    "CRITICAL": (76, 100),
}

# Configurable weights -- how much each component contributes to the
# final score. Kept as named constants so they're easy to tune later.
VOICE_RISK_WEIGHT = 0.65      # AI probability contributes up to 65 points
CONTEXT_RISK_WEIGHT = 1.0     # context_risk_points already capped at 30
HISTORICAL_RISK_MAX = 5       # small bump for repeated risky behavior (future use)


def get_risk_level(score: float) -> str:
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "CRITICAL" if score > 100 else "LOW"


def calculate_risk_score(
    ai_probability: float,
    context_risk_points: float,
    historical_risk_points: float = 0.0,
) -> Tuple[float, str]:
    """
    Combine voice AI-probability, contextual indicators, and historical
    risk signals into a single 0-100 impersonation risk score.

    Final Risk Score = Voice Risk + Contextual Risk + Historical Risk
    (normalized/clamped to 0-100)

    Args:
        ai_probability: 0.0-1.0, from the voice detector
        context_risk_points: 0-30, from analyze_context()
        historical_risk_points: 0-HISTORICAL_RISK_MAX, reserved for future
            use (e.g. repeated high-risk scans from the same user/number)

    Returns:
        (risk_score, risk_level)
    """
    voice_risk = ai_probability * 100 * VOICE_RISK_WEIGHT
    context_risk = context_risk_points * CONTEXT_RISK_WEIGHT
    historical_risk = min(historical_risk_points, HISTORICAL_RISK_MAX)

    raw_score = voice_risk + context_risk + historical_risk
    final_score = max(0.0, min(100.0, raw_score))

    risk_level = get_risk_level(final_score)

    return round(final_score, 1), risk_level


def get_risk_breakdown(
    ai_probability: float,
    context_risk_points: float,
    historical_risk_points: float = 0.0,
) -> Dict:
    """
    Same calculation as calculate_risk_score, but returns a transparent
    breakdown of each component -- useful for displaying "why" a score
    was assigned in the frontend, and for debugging/tuning weights.
    """
    voice_risk = round(ai_probability * 100 * VOICE_RISK_WEIGHT, 1)
    context_risk = round(context_risk_points * CONTEXT_RISK_WEIGHT, 1)
    historical_risk = round(min(historical_risk_points, HISTORICAL_RISK_MAX), 1)

    final_score, risk_level = calculate_risk_score(
        ai_probability, context_risk_points, historical_risk_points
    )

    return {
        "voice_risk_contribution": voice_risk,
        "context_risk_contribution": context_risk,
        "historical_risk_contribution": historical_risk,
        "final_risk_score": final_score,
        "risk_level": risk_level,
    }