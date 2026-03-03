"""Tests for core.semantic_matcher"""

import pytest
from core.semantic_matcher import (
    _clean_text,
    tfidf_similarity,
    compute_match_score,
    extract_skills,
)


def test_clean_text_strips_html():
    result = _clean_text("<b>Hello</b> World")
    assert "<b>" not in result
    assert "hello" in result


def test_clean_text_lowercases():
    assert _clean_text("Python Django REST") == "python django rest"


def test_clean_text_collapses_whitespace():
    result = _clean_text("hello   world")
    assert "  " not in result


def test_tfidf_identical_texts():
    text = "python developer django rest api postgresql"
    score = tfidf_similarity(text, text)
    assert score == pytest.approx(1.0, abs=0.01)


def test_tfidf_empty_cv():
    score = tfidf_similarity("", "some job description")
    assert score == 0.0


def test_tfidf_empty_job():
    score = tfidf_similarity("some cv content", "")
    assert score == 0.0


def test_tfidf_relevant_higher_than_irrelevant():
    cv = "Python developer experienced in Django, REST APIs, and PostgreSQL."
    relevant_job = "Looking for Python Django developer with REST API skills."
    irrelevant_job = "Chef needed for Italian restaurant with 5 years experience."
    assert tfidf_similarity(cv, relevant_job) > tfidf_similarity(cv, irrelevant_job)


def test_compute_match_score_returns_float_in_range():
    score = compute_match_score("some cv text", "some job description")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_extract_skills_finds_known_technologies():
    cv = "Experienced in Python, React, Docker, and PostgreSQL."
    skills = extract_skills(cv)
    assert "python" in skills
    assert "react" in skills
    assert "docker" in skills
    assert "postgresql" in skills


def test_extract_skills_empty_text():
    skills = extract_skills("")
    assert skills == []


def test_extract_skills_no_false_positives():
    cv = "I enjoy cooking and painting watercolors on weekends."
    skills = extract_skills(cv)
    # None of our tech skills should appear in a non-tech CV
    assert len(skills) == 0
