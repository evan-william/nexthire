#!/usr/bin/env bash
# Run the full test suite with coverage reporting.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==> Running NextHire test suite"
echo "    Project root: $PROJECT_ROOT"
echo ""

# Ensure dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "==> Installing test dependencies..."
    pip install -r requirements.txt --quiet
fi

# Run pytest with coverage
python -m pytest tests/ \
    --tb=short \
    --cov=core \
    --cov=data \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    -v \
    "$@"

echo ""
echo "==> Coverage report saved to htmlcov/index.html"
