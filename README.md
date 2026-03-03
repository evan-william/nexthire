<div align="center">

<img src="assets/nexthire-banner.jpg" alt="NextHire" width="700"/>

# NextHire

**Predictive job analytics. Find jobs you'll actually get.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-6c63ff?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-green?style=flat-square)](tests/)

[**Live Demo**](https://nexthire-test.streamlit.app/) · [**Report a Bug**](https://github.com/yourusername/nexthire/issues) · [**Request a Feature**](https://github.com/yourusername/nexthire/issues)

</div>

---

## What is NextHire?

NextHire is an open-source predictive career analytics platform. You upload your CV, set your preferences, and the system fetches live job listings — then scores each one against your profile using semantic NLP.

Unlike keyword matchers, NextHire's **Probability Engine** weights each score against real-world company competitiveness data. The result is a curated, ranked list that shows you where to apply first.

---

## How the scoring works

Each job gets a probability score built from three components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic Match | 60% | TF-IDF cosine similarity between your CV and the job description |
| Company Difficulty | 25% | Penalty based on company tier (FAANG vs startup vs SME) |
| Posting Freshness | 15% | Recency of the listing (today = 1.0, 30+ days = 0.1) |

The engine upgrades automatically to sentence-transformers if installed, giving significantly better semantic matching.

---

## Features

- CV upload — PDF and DOCX, parsed entirely in-memory
- Live job search via Adzuna API, cached to local SQLite
- Probability scoring per listing with visual match bars
- Skill detection from CV text for transparency
- Filter and sort results by match chance or skill overlap
- No user data stored after session ends

---

## Quick Start

```bash
git clone https://github.com/yourusername/nexthire.git
cd nexthire

# One-command setup (creates .venv, installs deps)
bash scripts/setup.sh

# Activate and configure API keys
source .venv/bin/activate
cp .env.example .env
# Edit .env and add your Adzuna credentials

# Run
streamlit run app.py
```

**Get a free Adzuna API key** at [developer.adzuna.com](https://developer.adzuna.com) — 250 calls/day on the free tier.

---

## Project Structure

```
nexthire/
├── app.py                      # Entry point, routing
├── config/
│   └── settings.py             # Constants, tier weights, API config
├── core/
│   ├── cv_parser.py            # PDF / DOCX extraction
│   ├── job_fetcher.py          # Adzuna API + DB fallback
│   ├── probability_engine.py   # Scoring and ranking
│   └── semantic_matcher.py     # TF-IDF / sentence-transformers
├── data/
│   └── database.py             # SQLite cache (parameterized queries)
├── ui/
│   ├── styles.py               # CSS design system
│   ├── components.py           # Reusable HTML components
│   └── pages/
│       ├── home.py             # Upload + preferences
│       ├── results.py          # Ranked results + filters
│       └── about.py
├── tests/
│   ├── test_cv_parser.py
│   ├── test_probability_engine.py
│   ├── test_semantic_matcher.py
│   └── test_database.py
└── scripts/
    ├── setup.sh
    └── run_tests.sh
```

---

## Running Tests

```bash
bash scripts/run_tests.sh
```

Coverage report will open in `htmlcov/index.html`. Tests use `pytest` with mocking — no real API calls are made.

---

## Configuration

All sensitive values live in `.env` — never hardcoded:

```bash
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

For Streamlit Cloud deployment, add these under **Settings → Secrets**.

---

## Upgrading to Better Embeddings

Install `sentence-transformers` for significantly better semantic matching:

```bash
pip install sentence-transformers
```

NextHire detects it automatically and switches from TF-IDF to `all-MiniLM-L6-v2` embeddings — no config change needed.

---

## Privacy

- CV text is processed in-memory only and never written to disk
- Only anonymized job metadata is cached in the local SQLite database
- No analytics or telemetry of any kind

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit + custom CSS (Syne, DM Mono) |
| NLP | scikit-learn TF-IDF / sentence-transformers |
| CV Parsing | PyMuPDF, python-docx |
| Job Data | Adzuna API + SQLite cache |
| Testing | pytest + pytest-cov |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new behavior
4. Run `bash scripts/run_tests.sh` and confirm they pass
5. Open a pull request

---

## License

MIT — see [LICENSE](LICENSE).
