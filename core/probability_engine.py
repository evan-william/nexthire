"""
Probability Engine: combines semantic match, company difficulty,
and posting freshness into a single acceptance probability score.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from config.settings import COMPANY_TIERS, config
from core.semantic_matcher import compute_match_score

logger = logging.getLogger(__name__)


def _get_company_difficulty(company_name: str) -> tuple[float, str]:
    """
    Return (difficulty_penalty, tier_label) for a given company name.
    Matches by case-insensitive substring.
    """
    name_lower = (company_name or "").lower()
    for tier_key, tier_data in COMPANY_TIERS.items():
        for known_company in tier_data["companies"]:
            if known_company in name_lower:
                return tier_data["difficulty_penalty"], tier_data["label"]
    # Default to tier3 (startup/SME)
    return COMPANY_TIERS["tier3"]["difficulty_penalty"], COMPANY_TIERS["tier3"]["label"]


def _freshness_score(posted_date_str: Optional[str]) -> float:
    """
    Score recency of a job posting. Returns float in [0, 1].
    Jobs posted today = 1.0; older than 30 days = 0.1.
    """
    if not posted_date_str:
        return 0.5

    try:
        # Try ISO format from APIs
        posted = datetime.fromisoformat(posted_date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_old = (now - posted).days
        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.85
        elif days_old <= 14:
            return 0.65
        elif days_old <= 30:
            return 0.40
        else:
            return 0.10
    except (ValueError, TypeError):
        return 0.5


def calculate_probability(
    cv_text: str,
    job: Dict,
) -> Dict:
    """
    Computes a probability score for one job posting.

    Returns the job dict enriched with:
      - match_score: raw semantic similarity [0,1]
      - difficulty_penalty: company difficulty weight
      - freshness_score: posting recency score
      - probability: final blended score [0,1]
      - probability_pct: percentage string for display
      - tier_label: human-readable company tier
    """
    description = job.get("description", "") or ""
    company = job.get("company", "") or ""

    # Core scoring components
    match_score = compute_match_score(cv_text, description) if description else 0.0
    difficulty_penalty, tier_label = _get_company_difficulty(company)
    fresh = _freshness_score(job.get("created", None))

    # Weighted combination
    w_semantic = config.SEMANTIC_WEIGHT
    w_difficulty = config.DIFFICULTY_WEIGHT
    w_freshness = config.FRESHNESS_WEIGHT

    raw_score = (
        match_score * w_semantic
        + (1.0 - difficulty_penalty) * w_difficulty
        + fresh * w_freshness
    )

    # Normalize and apply a slight sigmoid stretch for better UX spread
    probability = float(min(max(raw_score, 0.0), 1.0))

    return {
        **job,
        "match_score": round(match_score, 3),
        "difficulty_penalty": round(difficulty_penalty, 3),
        "freshness_score": round(fresh, 3),
        "probability": round(probability, 3),
        "probability_pct": f"{probability * 100:.1f}%",
        "tier_label": tier_label,
    }


def rank_jobs(cv_text: str, jobs: List[Dict]) -> List[Dict]:
    """
    Score and rank all job postings by probability (descending).
    Skips jobs with empty descriptions but still returns them at the bottom.
    """
    if not jobs:
        return []

    scored = []
    for job in jobs:
        try:
            scored.append(calculate_probability(cv_text, job))
        except Exception as exc:
            logger.warning("Scoring failed for job %s: %s", job.get("id"), exc)
            # Append with defaults so the job still shows up
            scored.append({**job, "probability": 0.0, "probability_pct": "N/A", "tier_label": "Unknown"})

    scored.sort(key=lambda j: j.get("probability", 0.0), reverse=True)
    return scored
