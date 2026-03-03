"""
Application-wide configuration constants.
Sensitive values (API keys) must be provided via environment variables or st.secrets.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AppConfig:
    APP_NAME: str = "NextHire"
    VERSION: str = "1.0.0"

    # File upload limits
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_CV_TYPES: tuple = ("application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    ALLOWED_EXTENSIONS: tuple = (".pdf", ".docx")

    # Job search defaults
    DEFAULT_RESULTS_COUNT: int = 20
    MAX_RESULTS_COUNT: int = 50

    # Probability engine weights
    SEMANTIC_WEIGHT: float = 0.60
    DIFFICULTY_WEIGHT: float = 0.25
    FRESHNESS_WEIGHT: float = 0.15

    # Database
    DB_PATH: str = "data/nexthire.db"

    # API - read from environment, never hardcoded
    ADZUNA_APP_ID: str = field(default_factory=lambda: os.environ.get("ADZUNA_APP_ID", ""))
    ADZUNA_APP_KEY: str = field(default_factory=lambda: os.environ.get("ADZUNA_APP_KEY", ""))
    SERPAPI_KEY: str = field(default_factory=lambda: os.environ.get("SERPAPI_KEY", ""))

    # Country codes supported by Adzuna
    SUPPORTED_COUNTRIES: tuple = ("gb", "us", "au", "ca", "de", "fr", "in", "sg", "id")


# Singleton config instance
config = AppConfig()


# Company tier difficulty weights (based on known competitiveness)
COMPANY_TIERS: dict = {
    "tier1": {
        "companies": ["google", "meta", "apple", "amazon", "microsoft", "netflix", "openai",
                      "deepmind", "stripe", "airbnb", "uber", "linkedin", "twitter", "x"],
        "difficulty_penalty": 0.45,
        "label": "FAANG / Top Tech",
    },
    "tier2": {
        "companies": ["shopify", "atlassian", "salesforce", "oracle", "sap", "adobe",
                      "nvidia", "amd", "intel", "ibm", "accenture", "deloitte", "mckinsey"],
        "difficulty_penalty": 0.30,
        "label": "Large Enterprise",
    },
    "tier3": {
        "companies": [],  # everything else: startups, SMEs
        "difficulty_penalty": 0.15,
        "label": "Startup / SME",
    },
}

WORK_MODES: List[str] = ["Remote", "Hybrid", "On-site"]
CONTRACT_TYPES: List[str] = ["Full-time", "Contract", "Internship", "Part-time"]
