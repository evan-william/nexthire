"""Tests for core.probability_engine"""

import pytest
from unittest.mock import patch

from core.probability_engine import (
    _get_company_difficulty,
    _freshness_score,
    calculate_probability,
    rank_jobs,
)


# ── _get_company_difficulty ───────────────────────────────────────────────────

def test_tier1_company_gets_high_penalty():
    penalty, label = _get_company_difficulty("Google LLC")
    assert penalty == 0.45
    assert "FAANG" in label or "Top" in label


def test_tier2_company_gets_medium_penalty():
    penalty, label = _get_company_difficulty("Shopify Inc")
    assert penalty == 0.30


def test_unknown_company_defaults_to_tier3():
    penalty, label = _get_company_difficulty("LocalStartupXYZ")
    assert penalty == 0.15
    assert "Startup" in label or "SME" in label


def test_empty_company_name():
    penalty, label = _get_company_difficulty("")
    assert penalty == 0.15


# ── _freshness_score ──────────────────────────────────────────────────────────

def test_freshness_today_returns_high():
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).isoformat()
    score = _freshness_score(today)
    assert score >= 0.85


def test_freshness_old_date_returns_low():
    score = _freshness_score("2022-01-01T00:00:00+00:00")
    assert score == 0.10


def test_freshness_none_returns_midpoint():
    score = _freshness_score(None)
    assert score == 0.5


def test_freshness_invalid_string_returns_midpoint():
    score = _freshness_score("not-a-date")
    assert score == 0.5


# ── calculate_probability ─────────────────────────────────────────────────────

SAMPLE_JOB = {
    "id": "1",
    "title": "Python Developer",
    "company": "LocalStartup",
    "description": "We need a Python developer with experience in Django and REST APIs.",
    "created": None,
    "url": "https://example.com",
}

SAMPLE_CV = """
Python developer with 3 years of experience building REST APIs with Django and FastAPI.
Proficient in SQL, Docker, and cloud deployments. Strong background in test-driven development.
"""


def test_calculate_probability_returns_dict_with_required_fields():
    result = calculate_probability(SAMPLE_CV, SAMPLE_JOB)
    for field in ("probability", "probability_pct", "match_score", "tier_label"):
        assert field in result


def test_calculate_probability_range():
    result = calculate_probability(SAMPLE_CV, SAMPLE_JOB)
    assert 0.0 <= result["probability"] <= 1.0


def test_calculate_probability_relevant_cv_scores_higher():
    irrelevant_cv = "I am a chef with 10 years of experience in French cuisine."
    relevant_result = calculate_probability(SAMPLE_CV, SAMPLE_JOB)
    irrelevant_result = calculate_probability(irrelevant_cv, SAMPLE_JOB)
    assert relevant_result["probability"] >= irrelevant_result["probability"]


def test_calculate_probability_faang_lower_than_startup():
    google_job = {**SAMPLE_JOB, "company": "Google"}
    startup_job = {**SAMPLE_JOB, "company": "LocalStartupXYZ"}
    google_result = calculate_probability(SAMPLE_CV, google_job)
    startup_result = calculate_probability(SAMPLE_CV, startup_job)
    assert startup_result["probability"] >= google_result["probability"]


# ── rank_jobs ─────────────────────────────────────────────────────────────────

def test_rank_jobs_empty_returns_empty():
    assert rank_jobs(SAMPLE_CV, []) == []


def test_rank_jobs_sorted_descending():
    jobs = [
        {**SAMPLE_JOB, "id": "a", "company": "Google", "description": ""},
        {**SAMPLE_JOB, "id": "b", "company": "LocalStartup"},
    ]
    ranked = rank_jobs(SAMPLE_CV, jobs)
    probs = [j["probability"] for j in ranked]
    assert probs == sorted(probs, reverse=True)


def test_rank_jobs_preserves_all_jobs():
    jobs = [{**SAMPLE_JOB, "id": str(i)} for i in range(5)]
    ranked = rank_jobs(SAMPLE_CV, jobs)
    assert len(ranked) == 5
