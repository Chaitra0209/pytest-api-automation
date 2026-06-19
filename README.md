# pytest-api-automation

![Pytest](https://github.com/YOUR_USERNAME/pytest-api-automation/actions/workflows/tests.yml/badge.svg)

A Python-based API test automation framework built with **pytest** and **requests**, demonstrating QA engineering best practices including fixtures, parametrized tests, markers, and CI/CD integration via GitHub Actions.

---

## Project Structure

```
pytest-api-automation/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI pipeline
├── tests/
│   ├── __init__.py
│   ├── test_auth.py           # Auth endpoint tests
│   ├── test_bookings_get.py   # GET booking tests
│   ├── test_bookings_post.py  # POST booking tests  (Day 2)
│   ├── test_bookings_put.py   # PUT/PATCH tests      (Day 3)
│   └── test_bookings_delete.py# DELETE tests         (Day 3)
├── utils/
│   ├── __init__.py
│   └── api_client.py          # Reusable HTTP client
├── test_data/                 # Static JSON payloads (Day 2)
├── reports/                   # Auto-generated HTML reports
├── conftest.py                # Global fixtures (session, auth, payloads)
├── pytest.ini                 # pytest config and markers
├── requirements.txt           # Dependencies
└── README.md
```

---

## API Under Test

**Restful-Booker** — a free, public REST API built for QA practice.  
Docs: https://restful-booker.herokuapp.com/apidoc/index.html

| Endpoint | Methods | Description |
|---|---|---|
| `/auth` | POST | Generate auth token |
| `/booking` | GET, POST | List all / create bookings |
| `/booking/{id}` | GET, PUT, PATCH, DELETE | Single booking operations |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Language |
| pytest | Test framework |
| requests | HTTP client |
| pytest-html | HTML test reports |
| GitHub Actions | CI/CD pipeline |

---

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/pytest-api-automation.git
cd pytest-api-automation

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run smoke tests only
pytest -m smoke

# Run regression suite
pytest -m regression

# Run a specific file
pytest tests/test_auth.py

# Run a specific test
pytest tests/test_auth.py::test_auth_with_valid_credentials_returns_token

# Run with verbose output
pytest -v

# Run and open HTML report
pytest --html=reports/report.html --self-contained-html
```

---

## Key Concepts Demonstrated

- **Fixtures with yield** — setup and teardown in one function (`conftest.py`)
- **Session-scoped fixtures** — auth token created once, reused across all tests
- **Parametrized tests** — `@pytest.mark.parametrize` for data-driven testing
- **Custom markers** — `@pytest.mark.smoke` / `@pytest.mark.regression`
- **Dependency injection** — fixtures injected by name into test functions
- **API client abstraction** — `utils/api_client.py` (like Page Object for APIs)
- **CI/CD** — GitHub Actions runs tests automatically on every push

---

## Daily Progress

| Day | Focus | Tests Added |
|---|---|---|
| Day 1 | Auth + GET tests, fixtures, markers, CI setup | 12 |
| Day 2 | POST tests, parametrize, test data files | — |
| Day 3 | PUT / PATCH / DELETE tests, negative cases | — |
| Day 4 | Allure reporting, refactor, final polish | — |

---

*Built as a personal upskilling project — June 2026*  
*Author: Chaitra Anand | [LinkedIn](https://linkedin.com/in/chaitra-anand-68497a42)*
