"""
Integration tests for all FastAPI endpoints defined in main.py.

The TestClient runs the full ASGI stack (routing, validation, serialisation).
The database is substituted with an in-memory SQLite instance via the
api_client fixture in conftest.py so no production DB is touched.
"""

import pytest


# ---------------------------------------------------------------------------
# Page routes - must return 200 and HTML content-type
# ---------------------------------------------------------------------------

class TestPageRoutes:
    ROUTES = ["/", "/students", "/lecturers", "/queries",
              "/research", "/courses", "/departments"]

    def test_all_pages_return_200(self, api_client):
        for route in self.ROUTES:
            resp = api_client.get(route)
            assert resp.status_code == 200, f"Expected 200 for {route}"

    def test_all_pages_return_html(self, api_client):
        for route in self.ROUTES:
            resp = api_client.get(route)
            assert "text/html" in resp.headers["content-type"], route


# ---------------------------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------------------------

class TestDashboardAPI:
    def test_status_200(self, api_client):
        assert api_client.get("/api/dashboard").status_code == 200

    def test_response_is_json(self, api_client):
        resp = api_client.get("/api/dashboard")
        data = resp.json()
        assert isinstance(data, dict)

    def test_all_keys_present(self, api_client):
        data = api_client.get("/api/dashboard").json()
        for key in ("students", "lecturers", "courses",
                    "departments", "programs", "research_projects"):
            assert key in data, f"Missing key: {key}"

    def test_counts_are_positive_integers(self, api_client):
        data = api_client.get("/api/dashboard").json()
        for key, val in data.items():
            assert isinstance(val, int) and val >= 0, f"{key}={val}"

    def test_student_count_matches_seed(self, api_client):
        assert api_client.get("/api/dashboard").json()["students"] == 10

    def test_lecturer_count_matches_seed(self, api_client):
        assert api_client.get("/api/dashboard").json()["lecturers"] == 5

    def test_department_count_matches_seed(self, api_client):
        assert api_client.get("/api/dashboard").json()["departments"] == 4


# ---------------------------------------------------------------------------
# Students API
# ---------------------------------------------------------------------------

class TestStudentsAPI:
    def test_list_all_returns_10(self, api_client):
        data = api_client.get("/api/students").json()
        assert len(data) == 10

    def test_each_record_has_required_fields(self, api_client):
        data = api_client.get("/api/students").json()
        for record in data:
            for field in ("student_id", "name", "email", "program_name",
                          "year_of_study", "graduation_status"):
                assert field in record

    def test_search_by_name(self, api_client):
        data = api_client.get("/api/students?search=alice").json()
        assert len(data) == 1
        assert data[0]["student_id"] == "S001"

    def test_search_by_email(self, api_client):
        data = api_client.get("/api/students?search=ben.johnson").json()
        assert len(data) >= 1
        ids = [r["student_id"] for r in data]
        assert "S002" in ids

    def test_search_by_student_id(self, api_client):
        data = api_client.get("/api/students?search=S003").json()
        ids = [r["student_id"] for r in data]
        assert "S003" in ids

    def test_search_no_match_returns_empty(self, api_client):
        data = api_client.get("/api/students?search=ZZZNOTEXIST").json()
        assert data == []

    def test_filter_by_status(self, api_client):
        data = api_client.get("/api/students?status=Not+graduated").json()
        assert all(r["graduation_status"] == "Not graduated" for r in data)

    def test_filter_nonexistent_status_returns_empty(self, api_client):
        data = api_client.get("/api/students?status=Alien").json()
        assert data == []

    def test_combined_search_and_status(self, api_client):
        data = api_client.get(
            "/api/students?search=alice&status=Not+graduated"
        ).json()
        assert len(data) == 1

    def test_student_courses(self, api_client):
        data = api_client.get("/api/students/S001/courses").json()
        codes = [r["course_code"] for r in data]
        assert "DB101" in codes and "AI201" in codes

    def test_student_courses_fields(self, api_client):
        data = api_client.get("/api/students/S001/courses").json()
        for record in data:
            for field in ("course_code", "course_name", "credits", "semester"):
                assert field in record

    def test_unknown_student_courses_returns_404(self, api_client):
        resp = api_client.get("/api/students/S999/courses")
        assert resp.status_code == 404

    def test_student_disciplinary(self, api_client):
        data = api_client.get("/api/students/S002/disciplinary").json()
        assert len(data) >= 1
        assert data[0]["description"] is not None

    def test_student_no_disciplinary(self, api_client):
        data = api_client.get("/api/students/S001/disciplinary").json()
        assert data == []

    def test_student_organisations(self, api_client):
        data = api_client.get("/api/students/S001/organisations").json()
        names = [r["organisation_name"] for r in data]
        assert "Data Science Society" in names

    def test_student_no_organisations(self, api_client):
        data = api_client.get("/api/students/S010/organisations").json()
        assert data == []


# ---------------------------------------------------------------------------
# Lecturers API
# ---------------------------------------------------------------------------

class TestLecturersAPI:
    def test_list_all_returns_5(self, api_client):
        data = api_client.get("/api/lecturers").json()
        assert len(data) == 5

    def test_each_record_has_required_fields(self, api_client):
        data = api_client.get("/api/lecturers").json()
        for record in data:
            for field in ("lecturer_id", "name", "email",
                          "department_name", "course_load"):
                assert field in record

    def test_search_by_name(self, api_client):
        data = api_client.get("/api/lecturers?search=smith").json()
        assert any(r["lecturer_id"] == "L001" for r in data)

    def test_search_by_expertise(self, api_client):
        data = api_client.get("/api/lecturers?search=cybersecurity").json()
        assert any(r["lecturer_id"] == "L005" for r in data)

    def test_filter_by_department(self, api_client):
        data = api_client.get(
            "/api/lecturers?department=Computer+Science"
        ).json()
        assert all(r["department_name"] == "Computer Science" for r in data)
        assert len(data) == 3  # L001, L002, L005

    def test_unknown_department_returns_empty(self, api_client):
        data = api_client.get("/api/lecturers?department=Hogwarts").json()
        assert data == []

    def test_lecturer_courses(self, api_client):
        data = api_client.get("/api/lecturers/L001/courses").json()
        codes = [r["course_code"] for r in data]
        assert "DB101" in codes

    def test_lecturer_courses_fields(self, api_client):
        data = api_client.get("/api/lecturers/L001/courses").json()
        for record in data:
            for field in ("course_code", "course_name", "credits", "semester"):
                assert field in record

    def test_lecturer_qualifications(self, api_client):
        data = api_client.get("/api/lecturers/L001/qualifications").json()
        assert len(data) >= 1
        assert data[0]["qualification"] is not None

    def test_lecturer_qualifications_fields(self, api_client):
        data = api_client.get("/api/lecturers/L002/qualifications").json()
        for record in data:
            for field in ("qualification", "awarding_institution", "award_year"):
                assert field in record

    def test_lecturer_committees(self, api_client):
        data = api_client.get("/api/lecturers/L001/committees").json()
        names = [r["committee_name"] for r in data]
        assert "Teaching Quality Committee" in names

    def test_lecturer_no_committees(self, api_client):
        # L003 has no committee in seed data
        data = api_client.get("/api/lecturers/L003/committees").json()
        assert data == []

    def test_lecturer_advisees(self, api_client):
        data = api_client.get("/api/lecturers/L001/students").json()
        ids = [r["student_id"] for r in data]
        assert set(ids) == {"S001", "S003"}

    def test_unknown_lecturer_advisees_empty(self, api_client):
        data = api_client.get("/api/lecturers/L999/students").json()
        assert data == []

    def test_l001_has_three_research_interests(self, api_client):
        data = api_client.get("/api/lecturers").json()
        l001 = next((r for r in data if r["lecturer_id"] == "L001"), None)
        assert l001 is not None
        # research_interests is a comma-separated string from GROUP_CONCAT
        interests = l001["research_interests"]
        assert interests is not None
        interest_list = [i.strip() for i in interests.split(",") if i.strip()]
        assert len(interest_list) == 3


# ---------------------------------------------------------------------------
# Research API
# ---------------------------------------------------------------------------

class TestResearchAPI:
    def test_list_all_returns_3(self, api_client):
        data = api_client.get("/api/research").json()
        assert len(data) == 3

    def test_each_record_has_required_fields(self, api_client):
        data = api_client.get("/api/research").json()
        for record in data:
            for field in ("project_id", "project_title", "principal_investigator",
                          "funding_source", "outcome"):
                assert field in record

    def test_search_by_title(self, api_client):
        data = api_client.get("/api/research?search=cloud").json()
        assert any(r["project_id"] == "R002" for r in data)

    def test_search_by_pi_name(self, api_client):
        data = api_client.get("/api/research?search=clark").json()
        assert any(r["project_id"] == "R001" for r in data)

    def test_search_by_funding_source(self, api_client):
        data = api_client.get("/api/research?search=UKRI").json()
        r001 = next((r for r in data if r["project_id"] == "R001"), None)
        assert r001 is not None
        assert "UKRI" in r001["funding_source"]

    def test_filter_by_outcome(self, api_client):
        data = api_client.get("/api/research?outcome=Ongoing").json()
        assert all(r["outcome"] == "Ongoing" for r in data)

    def test_unknown_outcome_empty(self, api_client):
        data = api_client.get("/api/research?outcome=Abandoned").json()
        assert data == []

    def test_project_members(self, api_client):
        data = api_client.get("/api/research/R001/members").json()
        types = {r["member_type"] for r in data}
        assert "Student" in types

    def test_project_members_fields(self, api_client):
        data = api_client.get("/api/research/R001/members").json()
        for record in data:
            for field in ("role", "member_name", "member_type"):
                assert field in record

    def test_project_publications(self, api_client):
        data = api_client.get("/api/research/R001/publications").json()
        assert len(data) >= 1

    def test_project_publications_fields(self, api_client):
        data = api_client.get("/api/research/R002/publications").json()
        for record in data:
            for field in ("title", "publication_year", "publication_type", "author"):
                assert field in record

    def test_r001_has_two_funding_sources(self, api_client):
        data = api_client.get("/api/research").json()
        r001 = next((r for r in data if r["project_id"] == "R001"), None)
        assert r001 is not None
        # funding_source is a comma-separated string from GROUP_CONCAT
        sources = r001["funding_source"]
        assert sources is not None
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        assert len(source_list) == 2


# ---------------------------------------------------------------------------
# Courses API
# ---------------------------------------------------------------------------

class TestCoursesAPI:
    def test_list_all_returns_6(self, api_client):
        data = api_client.get("/api/courses").json()
        assert len(data) == 6

    def test_each_record_has_required_fields(self, api_client):
        data = api_client.get("/api/courses").json()
        for record in data:
            for field in ("course_code", "course_name", "credits",
                          "course_level", "department_name", "enrolled"):
                assert field in record

    def test_search_by_code(self, api_client):
        data = api_client.get("/api/courses?search=DB101").json()
        assert len(data) == 1
        assert data[0]["course_code"] == "DB101"

    def test_search_by_name(self, api_client):
        data = api_client.get("/api/courses?search=artificial").json()
        assert any(r["course_code"] == "AI201" for r in data)

    def test_filter_by_department(self, api_client):
        data = api_client.get("/api/courses?department=Computer+Science").json()
        for r in data:
            assert r["department_name"] == "Computer Science"

    def test_filter_by_level(self, api_client):
        data = api_client.get("/api/courses?level=Postgraduate").json()
        assert all(r["course_level"] == "Postgraduate" for r in data)
        assert len(data) == 1  # only DS501 in seed

    def test_enrolled_count_is_integer(self, api_client):
        data = api_client.get("/api/courses").json()
        for r in data:
            assert isinstance(r["enrolled"], int)

    def test_course_enrolments(self, api_client):
        data = api_client.get("/api/courses/DB101/enrolments").json()
        ids = [r["student_id"] for r in data]
        assert set(ids) == {"S001", "S002", "S003"}

    def test_course_enrolments_fields(self, api_client):
        data = api_client.get("/api/courses/DB101/enrolments").json()
        for record in data:
            for field in ("student_id", "student_name", "semester"):
                assert field in record

    def test_course_lecturers(self, api_client):
        data = api_client.get("/api/courses/DB101/lecturers").json()
        ids = [r["lecturer_id"] for r in data]
        assert "L001" in ids

    def test_unknown_course_enrolments_empty(self, api_client):
        resp = api_client.get("/api/courses/FAKE999/enrolments")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Departments API
# ---------------------------------------------------------------------------

class TestDepartmentsAPI:
    def test_list_all_returns_4(self, api_client):
        data = api_client.get("/api/departments").json()
        assert len(data) == 4

    def test_each_record_has_required_fields(self, api_client):
        data = api_client.get("/api/departments").json()
        for record in data:
            for field in ("department_id", "department_name", "faculty",
                          "program_count", "lecturer_count", "staff_count"):
                assert field in record

    def test_search_by_name(self, api_client):
        data = api_client.get("/api/departments?search=Computer").json()
        assert any(r["department_id"] == "D001" for r in data)

    def test_search_by_faculty(self, api_client):
        data = api_client.get(
            "/api/departments?search=Faculty+of+Business"
        ).json()
        assert any(r["department_id"] == "D002" for r in data)

    def test_no_match_returns_empty(self, api_client):
        data = api_client.get("/api/departments?search=ZZZZ").json()
        assert data == []

    def test_research_areas_are_returned_as_array(self, api_client):
        data = api_client.get("/api/departments").json()
        for record in data:
            assert isinstance(record["research_areas"], list)

    def test_d001_has_three_research_areas(self, api_client):
        data = api_client.get("/api/departments").json()
        d001 = next((r for r in data if r["department_id"] == "D001"), None)
        assert d001 is not None
        assert len(d001["research_areas"]) == 3

    def test_department_programs(self, api_client):
        data = api_client.get("/api/departments/D001/programs").json()
        names = [r["program_name"] for r in data]
        assert "BSc Computer Science" in names

    def test_department_programs_fields(self, api_client):
        data = api_client.get("/api/departments/D001/programs").json()
        for record in data:
            for field in ("program_id", "program_name", "degree_awarded",
                          "duration_years"):
                assert field in record

    def test_department_staff(self, api_client):
        data = api_client.get("/api/departments/D004/staff").json()
        ids = [r["staff_id"] for r in data]
        assert set(ids) == {"N001", "N004"}

    def test_unknown_department_programs_empty(self, api_client):
        resp = api_client.get("/api/departments/D999/programs")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Named Query API endpoints (/api/query/1 … /api/query/10)
# ---------------------------------------------------------------------------

class TestQueryEndpoints:
    def test_query1_returns_list(self, api_client):
        resp = api_client.get(
            "/api/query/1?course_code=DB101&lecturer_id=L001&semester=2026S1"
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query1_missing_param_422(self, api_client):
        resp = api_client.get("/api/query/1?course_code=DB101&lecturer_id=L001")
        assert resp.status_code == 422

    def test_query2_returns_list(self, api_client):
        resp = api_client.get("/api/query/2?minimum_average=70")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query2_default_threshold(self, api_client):
        # omit minimum_average - should default to 70.0 per main.py
        resp = api_client.get("/api/query/2")
        assert resp.status_code == 200

    def test_query2_invalid_type_422(self, api_client):
        resp = api_client.get("/api/query/2?minimum_average=not_a_float")
        assert resp.status_code == 422

    def test_query3_returns_list(self, api_client):
        resp = api_client.get("/api/query/3?semester=2026S1")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query3_missing_semester_422(self, api_client):
        resp = api_client.get("/api/query/3")
        assert resp.status_code == 422

    def test_query4_returns_list(self, api_client):
        resp = api_client.get("/api/query/4?student_id=S001")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

    def test_query4_missing_param_422(self, api_client):
        resp = api_client.get("/api/query/4")
        assert resp.status_code == 422

    def test_query5_returns_list(self, api_client):
        resp = api_client.get("/api/query/5?keyword=databases")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query5_missing_keyword_422(self, api_client):
        resp = api_client.get("/api/query/5")
        assert resp.status_code == 422

    def test_query6_returns_list(self, api_client):
        resp = api_client.get("/api/query/6?department_id=D001")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query7_returns_list(self, api_client):
        resp = api_client.get("/api/query/7?department_id=D004")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query8_returns_list(self, api_client):
        resp = api_client.get("/api/query/8?year=2026")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query8_invalid_year_422(self, api_client):
        resp = api_client.get("/api/query/8?year=not_a_year")
        assert resp.status_code == 422

    def test_query9_returns_list(self, api_client):
        resp = api_client.get("/api/query/9")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query10_returns_list(self, api_client):
        resp = api_client.get("/api/query/10?lecturer_id=L001")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_query10_missing_param_422(self, api_client):
        resp = api_client.get("/api/query/10")
        assert resp.status_code == 422

    def test_undefined_query_route_404(self, api_client):
        resp = api_client.get("/api/query/99")
        assert resp.status_code == 404
