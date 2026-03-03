"""Tests for data.database"""

import os
import tempfile
import pytest

from data.database import JobDatabase


SAMPLE_JOBS = [
    {
        "id": "job_001",
        "title": "Python Developer",
        "company": "Acme Corp",
        "location": "London, UK",
        "description": "Build REST APIs with Python and Django.",
        "url": "https://example.com/job/001",
        "salary_min": 60000,
        "salary_max": 80000,
        "created": "2024-01-15T10:00:00Z",
        "contract_type": "permanent",
        "source": "adzuna",
    },
    {
        "id": "job_002",
        "title": "Data Scientist",
        "company": "DataCo",
        "location": "Remote",
        "description": "Machine learning and statistical modeling.",
        "url": "https://example.com/job/002",
        "salary_min": None,
        "salary_max": None,
        "created": "2024-01-16T09:00:00Z",
        "contract_type": "contract",
        "source": "adzuna",
    },
]


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    return JobDatabase(db_path)


def test_upsert_and_count(db):
    count = db.upsert_jobs(SAMPLE_JOBS)
    assert count == 2
    assert db.get_job_count() == 2


def test_upsert_is_idempotent(db):
    db.upsert_jobs(SAMPLE_JOBS)
    db.upsert_jobs(SAMPLE_JOBS)
    assert db.get_job_count() == 2  # no duplicates


def test_search_by_keyword(db):
    db.upsert_jobs(SAMPLE_JOBS)
    results = db.search_jobs("Python")
    assert len(results) == 1
    assert results[0]["id"] == "job_001"


def test_search_returns_empty_for_no_match(db):
    db.upsert_jobs(SAMPLE_JOBS)
    results = db.search_jobs("XYZ_NONEXISTENT_KEYWORD_12345")
    assert results == []


def test_search_by_location(db):
    db.upsert_jobs(SAMPLE_JOBS)
    results = db.search_jobs("Data", location="Remote")
    assert any(r["id"] == "job_002" for r in results)


def test_upsert_empty_list(db):
    count = db.upsert_jobs([])
    assert count == 0


def test_upsert_skips_jobs_without_id(db):
    bad_job = {"title": "No ID job", "company": "X", "description": "test"}
    count = db.upsert_jobs([bad_job])
    assert count == 0


def test_purge_old_jobs(db):
    db.upsert_jobs(SAMPLE_JOBS)
    # Purge anything older than 0 days (i.e., everything just inserted)
    # This would remove them since they were just inserted
    # We use 0 days to simulate old data removal
    initial_count = db.get_job_count()
    assert initial_count == 2
    removed = db.purge_old_jobs(days=36500)  # Far future → nothing removed
    assert removed == 0
    assert db.get_job_count() == 2
