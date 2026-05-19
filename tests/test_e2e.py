"""
End-to-end tests: full HTTP request → SQLite → JSON response chain.

These tests do NOT patch the database layer; they use the real
university.db file on disk via a live TestClient. They confirm that the
whole stack (FastAPI routing, query SQL, pandas serialisation) works together
against the actual production data file, matching specific values from
the seed data.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def live_client():
    """TestClient backed by the real on-disk database (read-only access)."""
    from main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# Dashboard counts reflect what is actually in university.db
# ---------------------------------------------------------------------------

class TestE2EDashboard:
    def test_students_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["students"] == 10

    def test_lecturers_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["lecturers"] == 5

    def test_courses_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["courses"] == 6

    def test_departments_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["departments"] == 4

    def test_programs_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["programs"] == 4

    def test_research_projects_count(self, live_client):
        data = live_client.get("/api/dashboard").json()
        assert data["research_projects"] == 3


# ---------------------------------------------------------------------------
# Query 1 - students in DB101 taught by L001 in 2026S1
# ---------------------------------------------------------------------------

class TestE2EQuery1:
    def test_correct_student_ids(self, live_client):
        data = live_client.get(
            "/api/query/1?course_code=DB101&lecturer_id=L001&semester=2026S1"
        ).json()
        ids = {r["student_id"] for r in data}
        assert ids == {"S001", "S002", "S003"}

    def test_lecturer_name_is_john_smith(self, live_client):
        data = live_client.get(
            "/api/query/1?course_code=DB101&lecturer_id=L001&semester=2026S1"
        ).json()
        assert all(r["lecturer_name"] == "John Smith" for r in data)

    def test_wrong_lecturer_returns_empty(self, live_client):
        data = live_client.get(
            "/api/query/1?course_code=DB101&lecturer_id=L002&semester=2026S1"
        ).json()
        assert data == []


# ---------------------------------------------------------------------------
# Query 2 - final-year students above 70 %
# ---------------------------------------------------------------------------

class TestE2EQuery2:
    def test_all_returned_are_final_year(self, live_client):
        data = live_client.get("/api/query/2?minimum_average=70").json()
        for r in data:
            assert r["year_of_study"] == r["duration_years"]

    def test_all_returned_exceed_threshold(self, live_client):
        data = live_client.get("/api/query/2?minimum_average=70").json()
        for r in data:
            assert r["average_grade"] > 70

    def test_s001_alice_is_in_results(self, live_client):
        data = live_client.get("/api/query/2?minimum_average=70").json()
        ids = [r["student_id"] for r in data]
        assert "S001" in ids

    def test_s002_not_in_results_not_final_year(self, live_client):
        # S002 is year 2 of 3
        data = live_client.get("/api/query/2?minimum_average=0").json()
        ids = [r["student_id"] for r in data]
        assert "S002" not in ids


# ---------------------------------------------------------------------------
# Query 3 - students without registration in 2026S1
# ---------------------------------------------------------------------------

class TestE2EQuery3:
    def test_s010_julia_green_in_results(self, live_client):
        data = live_client.get("/api/query/3?semester=2026S1").json()
        ids = [r["student_id"] for r in data]
        assert "S010" in ids

    def test_enrolled_students_excluded(self, live_client):
        data = live_client.get("/api/query/3?semester=2026S1").json()
        ids = {r["student_id"] for r in data}
        for enrolled_id in ("S001", "S002", "S003", "S004", "S005",
                             "S006", "S007", "S008", "S009"):
            assert enrolled_id not in ids


# ---------------------------------------------------------------------------
# Query 4 - advisor contact for S001
# ---------------------------------------------------------------------------

class TestE2EQuery4:
    def test_advisor_is_john_smith(self, live_client):
        data = live_client.get("/api/query/4?student_id=S001").json()
        assert data[0]["advisor_name"] == "John Smith"

    def test_advisor_email_correct(self, live_client):
        data = live_client.get("/api/query/4?student_id=S001").json()
        assert data[0]["advisor_email"] == "john.smith@university.edu"

    def test_advisor_department_correct(self, live_client):
        data = live_client.get("/api/query/4?student_id=S001").json()
        assert data[0]["advisor_department"] == "Computer Science"


# ---------------------------------------------------------------------------
# Query 5 - lecturers by expertise
# ---------------------------------------------------------------------------

class TestE2EQuery5:
    def test_databases_returns_l001(self, live_client):
        data = live_client.get("/api/query/5?keyword=databases").json()
        ids = [r["lecturer_id"] for r in data]
        assert "L001" in ids

    def test_cybersecurity_returns_l005(self, live_client):
        data = live_client.get("/api/query/5?keyword=cybersecurity").json()
        ids = [r["lecturer_id"] for r in data]
        assert "L005" in ids

    def test_nonexistent_expertise_returns_empty(self, live_client):
        data = live_client.get("/api/query/5?keyword=alchemy").json()
        assert data == []


# ---------------------------------------------------------------------------
# Query 6 - courses by department D001
# ---------------------------------------------------------------------------

class TestE2EQuery6:
    def test_db101_in_d001_courses(self, live_client):
        data = live_client.get("/api/query/6?department_id=D001").json()
        codes = [r["course_code"] for r in data]
        assert "DB101" in codes

    def test_d001_excludes_ba101(self, live_client):
        data = live_client.get("/api/query/6?department_id=D001").json()
        codes = [r["course_code"] for r in data]
        assert "BA101" not in codes

    def test_d003_returns_law201(self, live_client):
        data = live_client.get("/api/query/6?department_id=D003").json()
        codes = [r["course_code"] for r in data]
        assert "LAW201" in codes


# ---------------------------------------------------------------------------
# Query 7 - staff by department
# ---------------------------------------------------------------------------

class TestE2EQuery7:
    def test_d004_returns_n001_and_n004(self, live_client):
        data = live_client.get("/api/query/7?department_id=D004").json()
        ids = {r["staff_id"] for r in data}
        assert ids == {"N001", "N004"}

    def test_d001_returns_n002(self, live_client):
        data = live_client.get("/api/query/7?department_id=D001").json()
        ids = [r["staff_id"] for r in data]
        assert "N002" in ids


# ---------------------------------------------------------------------------
# Query 8 - publications by year
# ---------------------------------------------------------------------------

class TestE2EQuery8:
    def test_2026_has_three_publications(self, live_client):
        data = live_client.get("/api/query/8?year=2026").json()
        assert len(data) == 3

    def test_2025_has_one_publication(self, live_client):
        data = live_client.get("/api/query/8?year=2025").json()
        assert len(data) == 1
        assert "Forecasting" in data[0]["title"]

    def test_all_years_match(self, live_client):
        data = live_client.get("/api/query/8?year=2026").json()
        assert all(r["publication_year"] == 2026 for r in data)


# ---------------------------------------------------------------------------
# Query 9 - lecturers ranked by supervision
# ---------------------------------------------------------------------------

class TestE2EQuery9:
    def test_first_entry_has_required_fields(self, live_client):
        data = live_client.get("/api/query/9").json()
        assert "lecturer_id" in data[0]
        assert "student_supervisions" in data[0]

    def test_all_five_lecturers_present(self, live_client):
        data = live_client.get("/api/query/9").json()
        assert len(data) == 5

    def test_descending_order(self, live_client):
        data = live_client.get("/api/query/9").json()
        counts = [r["student_supervisions"] for r in data]
        assert counts == sorted(counts, reverse=True)


# ---------------------------------------------------------------------------
# Query 10 - students by advisor
# ---------------------------------------------------------------------------

class TestE2EQuery10:
    def test_l001_advisees_are_s001_and_s003(self, live_client):
        data = live_client.get("/api/query/10?lecturer_id=L001").json()
        ids = {r["student_id"] for r in data}
        assert ids == {"S001", "S003"}

    def test_l002_has_three_advisees(self, live_client):
        data = live_client.get("/api/query/10?lecturer_id=L002").json()
        assert len(data) == 3

    def test_unknown_advisor_returns_empty(self, live_client):
        resp = live_client.get("/api/query/10?lecturer_id=L999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Cross-entity data consistency checks
# ---------------------------------------------------------------------------

class TestE2EDataConsistency:
    def test_student_advisor_matches_lecturers_endpoint(self, live_client):
        """Advisor listed on a student record must exist as a real lecturer."""
        students = live_client.get("/api/students").json()
        lecturer_ids = {
            r["lecturer_id"]
            for r in live_client.get("/api/lecturers").json()
        }
        for s in students:
            if s["advisor_lecturer_id"]:
                assert s["advisor_lecturer_id"] in lecturer_ids, (
                    f"Student {s['student_id']} references unknown advisor "
                    f"{s['advisor_lecturer_id']}"
                )

    def test_course_department_matches_departments_endpoint(self, live_client):
        """Every course's department must appear in /api/departments."""
        courses = live_client.get("/api/courses").json()
        dept_names = {
            r["department_name"]
            for r in live_client.get("/api/departments").json()
        }
        for c in courses:
            assert c["department_name"] in dept_names

    def test_enrolment_grades_are_valid_percentages(self, live_client):
        """All stored grades must be in 0–100 range."""
        students = live_client.get("/api/students").json()
        for s in students:
            resp = live_client.get(
                f"/api/students/{s['student_id']}/courses"
            )
            if resp.status_code != 200:
                continue
            for c in resp.json():
                grade = c.get("grade")
                if grade is not None:
                    assert 0 <= grade <= 100, (
                        f"Grade {grade} out of range for "
                        f"student {s['student_id']}"
                    )

    def test_research_pi_is_a_known_lecturer(self, live_client):
        """principal_investigator field on each project must be a real name."""
        projects = live_client.get("/api/research").json()
        lecturer_names = {
            r["name"]
            for r in live_client.get("/api/lecturers").json()
        }
        for p in projects:
            assert p["principal_investigator"] in lecturer_names

    def test_all_published_years_are_plausible(self, live_client):
        """Publication years must be between 2000 and 2030."""
        for year in (2025, 2026):
            pubs = live_client.get(f"/api/query/8?year={year}").json()
            for pub in pubs:
                assert 2000 <= pub["publication_year"] <= 2030
