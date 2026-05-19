# University Record Management System

## Project Description

A university record management system built with FastAPI, SQLite, and plain HTML/Tailwind CSS. The system stores and queries information about students, lecturers, departments, programmes, courses, grades, non-academic staff, research projects, and publications.

## Technologies

| Area | Technology |
|---|---|
| Database | SQLite |
| Backend | Python / FastAPI |
| Frontend | HTML + Tailwind CSS (CDN) + Vanilla JS |
| Data layer | pandas + sqlite3 |
| Testing | pytest + httpx |
| Version control | Git / GitHub |

## Project Structure

```
CSCK542_Group_Project/
├── main.py               ← FastAPI app (routes + static file serving)
├── database.py           ← SQLite connection and query runner
├── queries.py            ← 10 parameterised query functions
├── build_database.py     ← Creates and seeds university.db
├── requirements.txt      ← Runtime dependencies
├── requirements-test.txt ← Runtime + test dependencies
├── pytest.ini            ← pytest configuration
├── README.md
├── database/
│   ├── schema.sql        ← Table definitions (19 tables)
│   ├── seed_data.sql     ← Sample data (70+ records)
│   └── university.db     ← SQLite database file
├── static/
│   ├── index.html        ← Dashboard
│   ├── students.html     ← Student management
│   ├── lecturers.html    ← Lecturer management
│   ├── courses.html      ← Course browser
│   ├── departments.html  ← Department browser
│   ├── research.html     ← Research project browser
│   └── queries.html      ← Query runner (all 10 queries)
├── tests/
│   ├── conftest.py       ← Shared fixtures (in-memory DB, API client)
│   ├── test_database.py  ← Unit tests for database.py
│   ├── test_queries.py   ← Unit tests for all 10 query functions
│   ├── test_api.py       ← Integration tests for every API endpoint
│   ├── test_schema.py    ← Schema integrity and FK constraint tests
│   └── test_e2e.py       ← End-to-end tests against the real database
├── diagrams/
│   └── erd.png           ← Entity relationship diagram
├── screenshots/          ← Query execution screenshots
└── report/               ← Project report
```

## How to Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the database

```bash
python build_database.py
```

### 4. Start the web application

```bash
python main.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Pages

| URL | Description |
|---|---|
| `/` | Dashboard: live counts for students, lecturers, courses, departments, programmes, research projects |
| `/students` | Searchable student table with enrolled courses, grades, disciplinary records, and organisations per student |
| `/lecturers` | Lecturer cards filterable by name, department or expertise, with teaching assignments, qualifications and committees |
| `/courses` | Course browser filterable by department and level, with enrolments and assigned lecturers |
| `/departments` | Department overview with programmes and non-academic staff |
| `/research` | Research project browser filterable by title, PI or outcome, with members and publications |
| `/queries` | Interactive query runner for all 10 database queries |

## Available Queries

| # | Query | Parameters |
|---|---|---|
| 1 | Students enrolled in a course taught by a specific lecturer | course code, lecturer ID, semester |
| 2 | Final-year students with average grade above a threshold | minimum average (%) |
| 3 | Students not registered for any course in a semester | semester |
| 4 | Advisor contact information for a student | student ID |
| 5 | Lecturers matching an expertise keyword | keyword |
| 6 | Courses offered by a department | department ID |
| 7 | Non-academic staff in a department | department ID |
| 8 | Lecturer publications in a given year | year |
| 9 | Lecturers ranked by number of student supervisions | *(none)* |
| 10 | Students assigned to a specific advisor | lecturer ID |

## Database Design

The schema uses 19 tables covering all university entities. Many-to-many relationships are handled through junction tables (`enrolments`, `teaching_assignments`, `research_project_members`). Multi-valued attributes such as expertise areas, qualifications, and publications are stored in separate normalised tables.

See `diagrams/erd.png` for the full entity relationship diagram.

## Testing

The project has a full pytest test suite covering four layers:

| Layer | File | Tests | What is covered |
|---|---|---|---|
| Unit - database | `test_database.py` | 12 | `get_connection` and `run_query`: return types, row factory, parameterisation, error handling |
| Unit - queries | `test_queries.py` | 68 | All 10 named query functions: correct columns, correct rows from seed data, ordering, empty-result edge cases, case-insensitive search |
| Integration - API | `test_api.py` | 88 | Every FastAPI route and endpoint: status codes, JSON shape, search/filter parameters, 422 validation on bad input |
| Schema integrity | `test_schema.py` | 48 | All 19 tables exist; primary-key uniqueness; NOT NULL constraints; all foreign-key relationships enforced; AUTOINCREMENT; exact seed row counts |
| End-to-end | `test_e2e.py` | 40 | Full HTTP → SQLite → JSON chain against the real database: dashboard counts, all 10 queries with expected values, cross-entity data consistency |

**Total: 256 tests, all passing.**

### Running the tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run the full suite
python -m pytest

# Run a specific layer
python -m pytest tests/test_schema.py    # schema integrity
python -m pytest tests/test_api.py      # API integration
python -m pytest tests/test_e2e.py      # end-to-end

# With coverage report
python -m pytest --cov=. --cov-report=term-missing
```

All tests use an isolated in-memory SQLite database built from the real schema and seed files, so the production `university.db` is never modified during testing. The end-to-end tests are the only ones that read from the real file, and they do so read-only.

## Notes

- All data is dummy/sample data for demonstration purposes.
- The database can be rebuilt at any time by running `python build_database.py`.
- Sample IDs: students `S001`–`S010`, lecturers `L001`–`L005`, departments `D001`–`D004`.
- Default semester used in queries: `2026S1`.
