"""
Semantic Matcher: scores how well a CV matches a job description.
Uses TF-IDF + cosine similarity as the primary signal.
Optionally upgrades to sentence-transformers if available.
"""

import logging
import re
from functools import lru_cache
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Lowercase, strip HTML tags, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\w\s]", " ", text.lower())
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tfidf_similarity(cv_text: str, job_text: str) -> float:
    """
    Compute cosine similarity between CV and job description using TF-IDF.
    Returns a float in [0, 1].
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    cv_clean = _clean_text(cv_text)
    job_clean = _clean_text(job_text)

    if not cv_clean or not job_clean:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            stop_words="english",
            min_df=1,
        )
        matrix = vectorizer.fit_transform([cv_clean, job_clean])
        score = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(np.clip(score, 0.0, 1.0))
    except Exception as exc:
        logger.warning("TF-IDF similarity failed: %s", exc)
        return 0.0


def _try_sentence_transformer_similarity(cv_text: str, job_text: str) -> Optional[float]:
    """
    Upgrade path: use sentence-transformers if installed.
    Falls back gracefully to None so the caller can use TF-IDF instead.
    """
    try:
        from sentence_transformers import SentenceTransformer, util

        model = _load_sentence_model()
        if model is None:
            return None

        cv_vec = model.encode(cv_text[:512], convert_to_tensor=True)
        job_vec = model.encode(job_text[:512], convert_to_tensor=True)
        score = util.cos_sim(cv_vec, job_vec).item()
        return float(np.clip(score, 0.0, 1.0))
    except ImportError:
        return None
    except Exception as exc:
        logger.warning("Sentence transformer failed: %s", exc)
        return None


@lru_cache(maxsize=1)
def _load_sentence_model():
    """Load the sentence transformer model once and cache it."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def compute_match_score(cv_text: str, job_description: str) -> float:
    """
    Main scoring function. Tries sentence-transformers first, falls back to TF-IDF.
    Returns a float in [0, 1].
    """
    semantic_score = _try_sentence_transformer_similarity(cv_text, job_description)
    if semantic_score is not None:
        return semantic_score
    return tfidf_similarity(cv_text, job_description)


def extract_skills(text: str) -> List[str]:
    """
    Extract a rough list of technical skills from text for display purposes.
    Matches against a curated keyword list.
    """
    SKILL_PATTERNS = [
        "python", "javascript", "typescript", "java", "go", "rust", "c++", "c#",
        "react", "vue", "angular", "node", "django", "fastapi", "flask", "spring",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "docker", "kubernetes", "terraform", "aws", "gcp", "azure", "ci/cd",
        "machine learning", "deep learning", "nlp", "data science", "pandas",
        "pytorch", "tensorflow", "scikit-learn", "spark", "kafka",
        "rest api", "graphql", "microservices", "agile", "scrum",
    ]
    text_lower = text.lower()
    return [skill for skill in SKILL_PATTERNS if skill in text_lower]
