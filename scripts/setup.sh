#!/usr/bin/env bash
# First-time setup: creates virtual environment and installs dependencies.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "==> Setting up NextHire development environment"

# Python version check
PYTHON_MIN="3.9"
PYTHON_BIN=$(command -v python3 || command -v python)
PYTHON_VERSION=$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

echo "    Python: $PYTHON_VERSION (minimum: $PYTHON_MIN)"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at .venv/"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo "==> Virtual environment already exists, skipping creation"
fi

# Activate and install
source "$VENV_DIR/bin/activate"
echo "==> Installing dependencies from requirements.txt..."
pip install --upgrade pip --quiet
pip install -r "$PROJECT_ROOT/requirements.txt"

# Create required directories
mkdir -p "$PROJECT_ROOT/data"

# Copy env template if not present
if [ ! -f "$PROJECT_ROOT/.env" ] && [ -f "$PROJECT_ROOT/.env.example" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "==> Copied .env.example → .env. Fill in your API keys."
fi

echo ""
echo "==> Setup complete."
echo "    Activate env: source .venv/bin/activate"
echo "    Run app:      streamlit run app.py"
echo "    Run tests:    bash scripts/run_tests.sh"
