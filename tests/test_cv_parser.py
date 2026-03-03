"""Tests for core.cv_parser"""

import io
import pytest
from unittest.mock import MagicMock, patch

from core.cv_parser import validate_file, parse_cv


# ── validate_file ─────────────────────────────────────────────────────────────

def test_validate_rejects_unsupported_extension():
    valid, msg = validate_file(b"data", "resume.txt")
    assert not valid
    assert "not supported" in msg


def test_validate_rejects_oversized_file():
    big_bytes = b"x" * (6 * 1024 * 1024)
    valid, msg = validate_file(big_bytes, "cv.pdf")
    assert not valid
    assert "5 MB" in msg


def test_validate_rejects_empty_file():
    valid, msg = validate_file(b"", "cv.pdf")
    assert not valid
    assert "empty" in msg


def test_validate_accepts_pdf():
    valid, msg = validate_file(b"content", "cv.pdf")
    assert valid
    assert msg == ""


def test_validate_accepts_docx():
    valid, msg = validate_file(b"content", "cv.docx")
    assert valid


def test_validate_case_insensitive_extension():
    valid, _ = validate_file(b"content", "cv.PDF")
    assert valid


# ── parse_cv ──────────────────────────────────────────────────────────────────

def test_parse_cv_raises_on_bad_extension():
    with pytest.raises(ValueError, match="not supported"):
        parse_cv(b"data", "resume.xlsx")


def test_parse_cv_raises_on_empty():
    with pytest.raises(ValueError, match="empty"):
        parse_cv(b"", "cv.pdf")


def test_parse_cv_raises_on_too_short_text():
    with patch("core.cv_parser.extract_text_from_pdf", return_value="short"):
        with pytest.raises(RuntimeError, match="too short"):
            parse_cv(b"fakepdf", "cv.pdf")


def test_parse_cv_returns_text_for_pdf():
    long_text = "Python developer with experience in machine learning. " * 10
    with patch("core.cv_parser.extract_text_from_pdf", return_value=long_text):
        result = parse_cv(b"fakepdf", "cv.pdf")
    assert result == long_text


def test_parse_cv_returns_text_for_docx():
    long_text = "Senior software engineer specializing in backend systems. " * 10
    with patch("core.cv_parser.extract_text_from_docx", return_value=long_text):
        result = parse_cv(b"fakedocx", "cv.docx")
    assert result == long_text
