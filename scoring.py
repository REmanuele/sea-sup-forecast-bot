"""Scoring logic for SUP sea conditions."""

from __future__ import annotations


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def score_hour(wind_kmh: float, gust_kmh: float, wave_m: float, rain_prob: float) -> int:
    """Return a 0-100 score. Higher is better for beginner-friendly SUP."""
    score = 100.0

    # Wind is usually the most important factor.
    if wind_kmh > 8:
        score -= (wind_kmh - 8) * 3.0
    if gust_kmh > 15:
        score -= (gust_kmh - 15) * 2.0

    # Small waves are preferable.
    if wave_m > 0.25:
        score -= (wave_m - 0.25) * 90.0

    # Rain probability impacts comfort and safety.
    score -= rain_prob * 0.35

    return int(round(clamp(score)))


def label(score: int) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "acceptable"
    return "not ideal"
