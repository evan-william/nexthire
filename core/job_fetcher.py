"""
Job Fetcher: retrieves job listings from Adzuna API and caches results in SQLite.
Falls back to cached data if API is unavailable or not configured.
"""

import logging
import time
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import requests

from config.settings import config
from data.database import JobDatabase

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 0.5  # between paginated requests


def _build_adzuna_url(
    country: str,
    keywords: str,
    location: str,
    page: int,
    results_per_page: int,
) -> str:
    base = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = (
        f"?app_id={config.ADZUNA_APP_ID}"
        f"&app_key={config.ADZUNA_APP_KEY}"
        f"&results_per_page={results_per_page}"
        f"&what={quote_plus(keywords)}"
        f"&content-type=application/json"
    )
    if location:
        params += f"&where={quote_plus(location)}"
    return base + params


def _normalize_adzuna_job(raw: Dict) -> Dict:
    """Map Adzuna response fields to our internal schema."""
    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "company": raw.get("company", {}).get("display_name", ""),
        "location": raw.get("location", {}).get("display_name", ""),
        "description": raw.get("description", ""),
        "url": raw.get("redirect_url", ""),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "created": raw.get("created"),
        "contract_type": raw.get("contract_type", ""),
        "source": "adzuna",
    }


def fetch_from_adzuna(
    keywords: str,
    location: str = "",
    country: str = "us",
    max_results: int = 20,
) -> List[Dict]:
    """
    Fetch jobs from Adzuna API. Returns normalized list.
    Raises ValueError if API credentials are missing.
    """
    if not config.ADZUNA_APP_ID or not config.ADZUNA_APP_KEY:
        raise ValueError("Adzuna API credentials not configured.")

    jobs = []
    per_page = min(max_results, 50)
    url = _build_adzuna_url(country, keywords, location, 1, per_page)

    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        raw_jobs = data.get("results", [])
        jobs = [_normalize_adzuna_job(j) for j in raw_jobs]
    except requests.exceptions.Timeout:
        logger.error("Adzuna API timed out.")
        raise ConnectionError("Job API request timed out. Try again shortly.")
    except requests.exceptions.HTTPError as exc:
        logger.error("Adzuna API HTTP error: %s", exc)
        raise ConnectionError(f"Job API returned an error: {exc.response.status_code}")
    except requests.exceptions.RequestException as exc:
        logger.error("Adzuna API request failed: %s", exc)
        raise ConnectionError("Could not reach the job search API.")

    return jobs


def fetch_jobs(
    keywords: str,
    location: str = "",
    country: str = "us",
    contract_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict]:
    """
    Public entry point. Attempts API first, then falls back to cached DB results.
    Applies contract_type and work_mode filters post-fetch.
    """
    db = JobDatabase(config.DB_PATH)
    jobs: List[Dict] = []

    # Build search query from keywords + work mode preference
    query = keywords
    if work_mode and work_mode.lower() == "remote":
        query += " remote"

    # Attempt live API fetch
    try:
        jobs = fetch_from_adzuna(query, location, country, max_results)
        if jobs:
            db.upsert_jobs(jobs)
            logger.info("Fetched %d jobs from Adzuna API.", len(jobs))
    except (ValueError, ConnectionError) as exc:
        logger.warning("API unavailable, using DB cache: %s", exc)
        jobs = db.search_jobs(query, location, limit=max_results)

    # Post-filter by contract type
    if contract_type and contract_type.lower() != "all":
        ct_lower = contract_type.lower()
        jobs = [
            j for j in jobs
            if ct_lower in (j.get("contract_type") or "").lower()
            or ct_lower in (j.get("title") or "").lower()
            or ct_lower in (j.get("description") or "").lower()
        ]

    return jobs[:max_results]
