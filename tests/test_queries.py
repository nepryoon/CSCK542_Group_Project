"""
Unit tests for queries.py - all 10 named query functions.

Each function is tested for:
  - return type (always pd.DataFrame)
  - expected columns in the result
  - correct data is returned for known seed inputs
  - boundary / edge cases (empty results, minimum threshold, etc.)
"""

from unittest.mock import patch

import pandas as pd
import pytest

import queries


# ---------------------------------------------------------------------------
# Helper - patch queries.run_query to use the in-memory DB run_query
# ---------------------------------------------------------------------------

def _patch(db_run_query):
    """Context manager: replace queries.run_query with db_run_query."""
    return patch("queries.run_query", side_effect=db_run_query)


# ---------------------------------------------------------------------------
# Query 1: find_students_by_course_and_lecturer
# ---------------------------------------------------------------------------

class TestFindStudentsByCourseAndLecturer:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.find_students_by_course_and_lecturer(
                "DB101", "L001", "2026S1"
            )
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "DB101", "L001", "2026S1"
            )
        expected = {
            "student_id", "student_name", "course_code",
            "course_name", "lecturer_name", "semester",
        }
        assert expected.issubset(set(df.columns))

    def test_correct_students_returned(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "DB101", "L001", "2026S1"
            )
        # S001 Alice Taylor, S002 Ben Johnson, S003 Chloe Martin enrolled DB101
        assert set(df["student_id"].tolist()) == {"S001", "S002", "S003"}

    def test_wrong_semester_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "DB101", "L001", "2025S2"
            )
        assert len(df) == 0

    def test_wrong_lecturer_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "DB101", "L002", "2026S1"
            )
        assert len(df) == 0

    def test_nonexistent_course_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "FAKE999", "L001", "2026S1"
            )
        assert len(df) == 0

    def test_result_ordered_by_student_name(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_course_and_lecturer(
                "DB101", "L001", "2026S1"
            )
        names = df["student_name"].tolist()
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Query 2: find_final_year_students_above_grade
# ---------------------------------------------------------------------------

class TestFindFinalYearStudentsAboveGrade:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.find_final_year_students_above_grade(70.0)
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_final_year_students_above_grade(70.0)
        for col in ("student_id", "student_name", "program_name", "average_grade"):
            assert col in df.columns

    def test_threshold_70_returns_correct_students(self, db_run_query):
        # Final-year students in seed: S001(avg 79), S003(avg 89.5),
        # S005(avg 79), S007(avg 81) - all above 70
        with _patch(db_run_query):
            df = queries.find_final_year_students_above_grade(70.0)
        ids = set(df["student_id"].tolist())
        assert "S001" in ids
        assert "S003" in ids

    def test_all_grades_above_100_threshold_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_final_year_students_above_grade(100.0)
        assert len(df) == 0

    def test_threshold_0_returns_all_final_year_with_grades(self, db_run_query):
        with _patch(db_run_query):
            df_all = queries.find_final_year_students_above_grade(0.0)
            df_thresh = queries.find_final_year_students_above_grade(70.0)
        assert len(df_all) >= len(df_thresh)

    def test_ordered_by_average_grade_descending(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_final_year_students_above_grade(0.0)
        grades = df["average_grade"].tolist()
        assert grades == sorted(grades, reverse=True)

    def test_non_final_year_students_excluded(self, db_run_query):
        # S002 is year 2 of a 3-year program - must not appear
        with _patch(db_run_query):
            df = queries.find_final_year_students_above_grade(0.0)
        assert "S002" not in df["student_id"].tolist()


# ---------------------------------------------------------------------------
# Query 3: find_students_without_registration
# ---------------------------------------------------------------------------

class TestFindStudentsWithoutRegistration:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.find_students_without_registration("2026S1")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_without_registration("2026S1")
        for col in ("student_id", "student_name", "program_name", "email"):
            assert col in df.columns

    def test_s010_not_enrolled_appears(self, db_run_query):
        # S010 Julia Green has no enrolment row in seed data
        with _patch(db_run_query):
            df = queries.find_students_without_registration("2026S1")
        assert "S010" in df["student_id"].tolist()

    def test_enrolled_students_not_in_result(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_without_registration("2026S1")
        enrolled = {"S001", "S002", "S003", "S004", "S005",
                    "S006", "S007", "S008", "S009"}
        assert enrolled.isdisjoint(set(df["student_id"].tolist()))

    def test_nonexistent_semester_returns_all_students(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_without_registration("1900S1")
        assert len(df) == 10  # all 10 seed students

    def test_ordered_by_student_name(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_without_registration("1900S1")
        names = df["student_name"].tolist()
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Query 4: get_advisor_contact
# ---------------------------------------------------------------------------

class TestGetAdvisorContact:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.get_advisor_contact("S001")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.get_advisor_contact("S001")
        for col in ("advisor_name", "advisor_email", "advisor_phone",
                    "advisor_department"):
            assert col in df.columns

    def test_s001_advisor_is_l001(self, db_run_query):
        with _patch(db_run_query):
            df = queries.get_advisor_contact("S001")
        assert df.iloc[0]["advisor_id"] == "L001"
        assert "Smith" in df.iloc[0]["advisor_name"]

    def test_advisor_email_present(self, db_run_query):
        with _patch(db_run_query):
            df = queries.get_advisor_contact("S001")
        assert "@" in df.iloc[0]["advisor_email"]

    def test_nonexistent_student_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.get_advisor_contact("S999")
        assert len(df) == 0

    def test_returns_single_row(self, db_run_query):
        with _patch(db_run_query):
            df = queries.get_advisor_contact("S003")
        assert len(df) == 1


# ---------------------------------------------------------------------------
# Query 5: search_lecturers_by_expertise
# ---------------------------------------------------------------------------

class TestSearchLecturersByExpertise:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.search_lecturers_by_expertise("databases")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.search_lecturers_by_expertise("databases")
        for col in ("lecturer_id", "lecturer_name", "expertise_area", "email"):
            assert col in df.columns

    def test_case_insensitive_search(self, db_run_query):
        with _patch(db_run_query):
            df_lower = queries.search_lecturers_by_expertise("databases")
            df_upper = queries.search_lecturers_by_expertise("DATABASES")
        assert len(df_lower) == len(df_upper)

    def test_databases_returns_l001(self, db_run_query):
        with _patch(db_run_query):
            df = queries.search_lecturers_by_expertise("Databases")
        assert "L001" in df["lecturer_id"].tolist()

    def test_ai_returns_l002(self, db_run_query):
        with _patch(db_run_query):
            df = queries.search_lecturers_by_expertise("Artificial Intelligence")
        assert "L002" in df["lecturer_id"].tolist()

    def test_partial_keyword_match(self, db_run_query):
        with _patch(db_run_query):
            df = queries.search_lecturers_by_expertise("cyber")
        assert "L005" in df["lecturer_id"].tolist()

    def test_nonexistent_keyword_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.search_lecturers_by_expertise("quantum_knitting")
        assert len(df) == 0


# ---------------------------------------------------------------------------
# Query 6: list_courses_by_department
# ---------------------------------------------------------------------------

class TestListCoursesByDepartment:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.list_courses_by_department("D001")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D001")
        for col in ("department_name", "course_code", "course_name",
                    "course_level", "credits"):
            assert col in df.columns

    def test_d001_includes_db101(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D001")
        assert "DB101" in df["course_code"].tolist()

    def test_d002_includes_ba101(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D002")
        assert "BA101" in df["course_code"].tolist()

    def test_d002_excludes_d001_courses(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D002")
        assert "DB101" not in df["course_code"].tolist()

    def test_nonexistent_department_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D999")
        assert len(df) == 0

    def test_ordered_by_course_code(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_courses_by_department("D001")
        codes = df["course_code"].tolist()
        assert codes == sorted(codes)


# ---------------------------------------------------------------------------
# Query 7: list_staff_by_department
# ---------------------------------------------------------------------------

class TestListStaffByDepartment:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.list_staff_by_department("D004")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D004")
        for col in ("staff_id", "staff_name", "job_title",
                    "department_name", "employment_type"):
            assert col in df.columns

    def test_d004_returns_n001_n004(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D004")
        ids = set(df["staff_id"].tolist())
        assert {"N001", "N004"}.issubset(ids)

    def test_d001_returns_n002(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D001")
        assert "N002" in df["staff_id"].tolist()

    def test_salary_information_present(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D001")
        assert "salary_information" in df.columns

    def test_nonexistent_department_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D999")
        assert len(df) == 0

    def test_ordered_by_staff_name(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_staff_by_department("D004")
        names = df["staff_name"].tolist()
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Query 8: list_publications_by_year
# ---------------------------------------------------------------------------

class TestListPublicationsByYear:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.list_publications_by_year(2026)
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2026)
        for col in ("title", "publication_year", "publication_type",
                    "lecturer_name", "department_name"):
            assert col in df.columns

    def test_2026_returns_three_publications(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2026)
        assert len(df) == 3

    def test_2025_returns_one_publication(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2025)
        assert len(df) == 1

    def test_future_year_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2099)
        assert len(df) == 0

    def test_all_rows_match_requested_year(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2026)
        assert all(df["publication_year"] == 2026)

    def test_ordered_by_lecturer_name(self, db_run_query):
        with _patch(db_run_query):
            df = queries.list_publications_by_year(2026)
        names = df["lecturer_name"].tolist()
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Query 9: rank_lecturers_by_supervision
# ---------------------------------------------------------------------------

class TestRankLecturersBySupervision:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.rank_lecturers_by_supervision()
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        for col in ("lecturer_id", "lecturer_name",
                    "department_name", "student_supervisions"):
            assert col in df.columns

    def test_all_lecturers_returned(self, db_run_query):
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        assert len(df) == 5

    def test_supervision_counts_are_non_negative(self, db_run_query):
        # The query counts rows where a lecturer shares a project_id with a
        # student member.  With the current seed layout (lecturer and student
        # rows are separate) every count is 0 - that is the correct output.
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        assert (df["student_supervisions"] >= 0).all()

    def test_all_lecturers_have_supervision_count_column(self, db_run_query):
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        assert "student_supervisions" in df.columns

    def test_ordered_descending_by_supervisions(self, db_run_query):
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        counts = df["student_supervisions"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_no_params_required(self, db_run_query):
        """rank_lecturers_by_supervision takes no arguments."""
        with _patch(db_run_query):
            queries.rank_lecturers_by_supervision()  # must not raise

    def test_l002_supervises_two_students(self, db_run_query):
        """L002 is PI of R001, which has two student researchers (S004, S009)."""
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        row = df[df["lecturer_id"] == "L002"].iloc[0]
        assert row["student_supervisions"] == 2

    def test_l003_supervises_one_student(self, db_run_query):
        """L003 is PI of R003, which has one student researcher (S005)."""
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        row = df[df["lecturer_id"] == "L003"].iloc[0]
        assert row["student_supervisions"] == 1

    def test_lecturer_not_in_any_project_has_zero(self, db_run_query):
        """L004 is not a member of any research project; count must be 0."""
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        row = df[df["lecturer_id"] == "L004"].iloc[0]
        assert row["student_supervisions"] == 0

    def test_total_supervisions_match_seed_data(self, db_run_query):
        """Sum across all lecturers equals 3 (R001: 2 students via L002,
        R003: 1 student via L003; R002 has no student researchers).
        L001 and L005 both belong to R002 but that project has no students,
        so they contribute 0.  No project has multiple lecturer members AND
        student members, so there is no double-counting in this seed.
        """
        with _patch(db_run_query):
            df = queries.rank_lecturers_by_supervision()
        assert df["student_supervisions"].sum() == 3


# ---------------------------------------------------------------------------
# Query 10: find_students_by_advisor
# ---------------------------------------------------------------------------

class TestFindStudentsByAdvisor:
    def test_returns_dataframe(self, db_run_query):
        with _patch(db_run_query):
            result = queries.find_students_by_advisor("L001")
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L001")
        for col in ("student_id", "student_name", "email",
                    "program_name", "year_of_study", "graduation_status"):
            assert col in df.columns

    def test_l001_advises_s001_and_s003(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L001")
        ids = set(df["student_id"].tolist())
        assert ids == {"S001", "S003"}

    def test_l002_advises_three_students(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L002")
        assert len(df) == 3  # S002, S004, S009

    def test_nonexistent_advisor_returns_empty(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L999")
        assert len(df) == 0

    def test_ordered_by_student_name(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L001")
        names = df["student_name"].tolist()
        assert names == sorted(names)

    def test_graduation_status_present(self, db_run_query):
        with _patch(db_run_query):
            df = queries.find_students_by_advisor("L001")
        assert df["graduation_status"].notna().all()
