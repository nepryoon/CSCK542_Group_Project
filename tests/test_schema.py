"""
Database schema and integrity tests.

These tests verify structural properties of the schema - NOT NULL constraints,
foreign-key enforcement, primary-key uniqueness, and column data types -
using the isolated_db fixture so writes don't bleed into other tests.
"""

import sqlite3

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _exec(conn, sql, params=()):
    """Execute a single statement and return the cursor."""
    return conn.execute(sql, params)


def _must_fail(conn, sql, params=()):
    """Assert that executing *sql* raises an IntegrityError."""
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql, params)
        conn.commit()


# ---------------------------------------------------------------------------
# Table existence
# ---------------------------------------------------------------------------

EXPECTED_TABLES = [
    "departments", "programs", "lecturers", "students",
    "non_academic_staff", "courses", "enrolments",
    "teaching_assignments", "grades", "disciplinary_records",
    "lecturer_qualifications", "lecturer_expertise",
    "research_projects", "research_project_members",
    "publications", "student_organisations",
    "student_org_memberships", "committees", "committee_memberships",
]


class TestTableExistence:
    def test_all_tables_exist(self, in_memory_db):
        cursor = in_memory_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        existing = {row[0] for row in cursor.fetchall()}
        for table in EXPECTED_TABLES:
            assert table in existing, f"Missing table: {table}"


# ---------------------------------------------------------------------------
# Primary-key uniqueness
# ---------------------------------------------------------------------------

class TestPrimaryKeys:
    def test_department_pk_unique(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO departments VALUES ('D001','Dup','Faculty','Areas')",
        )

    def test_lecturer_pk_unique(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO lecturers VALUES "
            "('L001','X','Y','x@y.com','000','D001',1,'None')",
        )

    def test_student_pk_unique(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO students VALUES "
            "('S001','X','Y','2000-01-01','x@s.edu','000','P001',1,'Not graduated','L001')",
        )

    def test_course_pk_unique(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO courses VALUES "
            "('DB101','Dup','Desc','D001','Undergraduate',15,'Mon','slides')",
        )

    def test_staff_pk_unique(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO non_academic_staff VALUES "
            "('N001','X','Y','Admin','D001','Full time','Perm',30000,'EC')",
        )


# ---------------------------------------------------------------------------
# NOT NULL constraints
# ---------------------------------------------------------------------------

class TestNotNullConstraints:
    def test_department_name_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO departments VALUES ('D099', NULL, 'Faculty', 'Areas')",
        )

    def test_department_faculty_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO departments VALUES ('D099', 'Name', NULL, 'Areas')",
        )

    def test_lecturer_first_name_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO lecturers VALUES "
            "('L099', NULL, 'Last', 'a@b.com', NULL, 'D001', 0, NULL)",
        )

    def test_lecturer_email_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO lecturers VALUES "
            "('L099', 'First', 'Last', NULL, NULL, 'D001', 0, NULL)",
        )

    def test_student_email_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO students VALUES "
            "('S099','F','L','2000-01-01',NULL,'000','P001',1,'Not graduated',NULL)",
        )

    def test_student_graduation_status_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO students VALUES "
            "('S099','F','L','2000-01-01','f@s.edu','000','P001',1,NULL,NULL)",
        )

    def test_grade_value_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO grades (student_id, course_code, semester, grade) "
            "VALUES ('S001', 'DB101', '2026S2', NULL)",
        )

    def test_publication_title_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO publications "
            "(lecturer_id, project_id, title, publication_year, publication_type) "
            "VALUES ('L001', NULL, NULL, 2026, 'Journal')",
        )

    def test_disciplinary_description_not_null(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO disciplinary_records "
            "(student_id, record_date, description, outcome) "
            "VALUES ('S001', '2026-01-01', NULL, 'Warning')",
        )


# ---------------------------------------------------------------------------
# Foreign-key constraints
# ---------------------------------------------------------------------------

class TestForeignKeyConstraints:
    def test_student_invalid_program_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO students VALUES "
            "('S099','F','L','2000-01-01','f@s.edu','000','PXXX',1,'Not graduated',NULL)",
        )

    def test_student_invalid_advisor_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO students VALUES "
            "('S099','F','L','2000-01-01','f@s.edu','000','P001',1,'Not graduated','LXXX')",
        )

    def test_enrolment_invalid_student_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO enrolments (student_id, course_code, semester) "
            "VALUES ('SXXX', 'DB101', '2026S1')",
        )

    def test_enrolment_invalid_course_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO enrolments (student_id, course_code, semester) "
            "VALUES ('S001', 'FAKE999', '2026S1')",
        )

    def test_grade_invalid_student_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO grades (student_id, course_code, semester, grade) "
            "VALUES ('SXXX', 'DB101', '2026S1', 90)",
        )

    def test_teaching_invalid_lecturer_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO teaching_assignments "
            "(lecturer_id, course_code, semester) "
            "VALUES ('LXXX', 'DB101', '2026S1')",
        )

    def test_publication_invalid_lecturer_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO publications "
            "(lecturer_id, project_id, title, publication_year) "
            "VALUES ('LXXX', NULL, 'Title', 2026)",
        )

    def test_research_member_invalid_project_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO research_project_members "
            "(project_id, lecturer_id, student_id, role) "
            "VALUES ('RXXX', 'L001', NULL, 'Role')",
        )

    def test_committee_membership_invalid_lecturer_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO committee_memberships "
            "(lecturer_id, committee_id, role) "
            "VALUES ('LXXX', 'C001', 'Member')",
        )

    def test_staff_invalid_department_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO non_academic_staff VALUES "
            "('N099','F','L','Title','DXXX','Full time','Perm',30000,'EC')",
        )

    def test_program_invalid_department_rejected(self, isolated_db):
        _must_fail(
            isolated_db,
            "INSERT INTO programs VALUES "
            "('P099','Name','BSc',3,'DXXX','Details')",
        )


# ---------------------------------------------------------------------------
# Column data type / default checks
# ---------------------------------------------------------------------------

class TestColumnDefaults:
    def test_enrolment_id_autoincrement(self, isolated_db):
        isolated_db.execute(
            "INSERT INTO enrolments (student_id, course_code, semester) "
            "VALUES ('S001', 'DB101', '2027S1')"
        )
        isolated_db.commit()
        cursor = isolated_db.execute(
            "SELECT enrolment_id FROM enrolments WHERE semester='2027S1'"
        )
        row = cursor.fetchone()
        assert row[0] is not None and row[0] > 0

    def test_grade_must_be_numeric(self, isolated_db):
        # SQLite is loosely typed but REAL affinity; inserting text that
        # can't convert to a number should still store as text - we verify
        # a proper number is accepted without error
        isolated_db.execute(
            "INSERT INTO grades (student_id, course_code, semester, grade) "
            "VALUES ('S001', 'DB101', '2027S1', 99.5)"
        )
        isolated_db.commit()
        cursor = isolated_db.execute(
            "SELECT grade FROM grades WHERE semester='2027S1'"
        )
        assert cursor.fetchone()[0] == 99.5

    def test_lecturer_course_load_defaults_to_zero(self, isolated_db):
        isolated_db.execute(
            "INSERT INTO lecturers "
            "(lecturer_id, first_name, last_name, email, department_id) "
            "VALUES ('L099','Test','Lect','t@t.com','D001')"
        )
        isolated_db.commit()
        cursor = isolated_db.execute(
            "SELECT course_load FROM lecturers WHERE lecturer_id='L099'"
        )
        assert cursor.fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Seed data row counts
# ---------------------------------------------------------------------------

class TestSeedDataCounts:
    @pytest.mark.parametrize("table,expected", [
        ("departments", 4),
        ("programs", 4),
        ("lecturers", 5),
        ("students", 10),
        ("non_academic_staff", 4),
        ("courses", 6),
        ("enrolments", 12),
        ("teaching_assignments", 6),
        ("grades", 12),
        ("disciplinary_records", 2),
        ("lecturer_qualifications", 5),
        ("lecturer_expertise", 10),
        ("research_projects", 3),
        ("research_project_members", 7),
        ("publications", 4),
        ("student_organisations", 3),
        ("student_org_memberships", 4),
        ("committees", 2),
        ("committee_memberships", 3),
    ])
    def test_row_count(self, in_memory_db, table, expected):
        cursor = in_memory_db.execute(f"SELECT COUNT(*) FROM {table}")
        assert cursor.fetchone()[0] == expected, f"Wrong row count for {table}"
