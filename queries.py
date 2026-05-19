import pandas as pd

from database import run_query


def find_students_by_course_and_lecturer(
    course_code: str,
    lecturer_id: str,
    semester: str,
) -> pd.DataFrame:
    """Return students enrolled in a course under a specific lecturer."""
    # Semester is matched on both enrolments and teaching_assignments so that
    # a lecturer who taught the same course in a different term is not
    # incorrectly associated with the current cohort.
    query = """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            c.course_code,
            c.course_name,
            l.first_name || ' ' || l.last_name AS lecturer_name,
            e.semester
        FROM students AS s
        INNER JOIN enrolments AS e
            ON s.student_id = e.student_id
        INNER JOIN courses AS c
            ON e.course_code = c.course_code
        INNER JOIN teaching_assignments AS ta
            ON c.course_code = ta.course_code
            AND e.semester = ta.semester
        INNER JOIN lecturers AS l
            ON ta.lecturer_id = l.lecturer_id
        WHERE c.course_code = ?
            AND l.lecturer_id = ?
            AND e.semester = ?
        ORDER BY student_name;
    """
    return run_query(query, (course_code, lecturer_id, semester))


def find_final_year_students_above_grade(
    minimum_average: float,
) -> pd.DataFrame:
    """Return final-year students whose average grade exceeds the threshold."""
    # year_of_study = duration_years detects final-year status without
    # hard-coding 3 or 4, so the query works for programs of any length.
    query = """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            p.program_name,
            s.year_of_study,
            p.duration_years,
            ROUND(AVG(g.grade), 2) AS average_grade
        FROM students AS s
        INNER JOIN programs AS p
            ON s.program_id = p.program_id
        INNER JOIN grades AS g
            ON s.student_id = g.student_id
        WHERE s.year_of_study = p.duration_years
        GROUP BY
            s.student_id,
            student_name,
            p.program_name,
            s.year_of_study,
            p.duration_years
        HAVING AVG(g.grade) > ?
        ORDER BY average_grade DESC;
    """
    return run_query(query, (minimum_average,))


def find_students_without_registration(semester: str) -> pd.DataFrame:
    """Find students who have no enrolments for a given semester.

    Uses a correlated NOT EXISTS sub-query, which expresses the anti-join
    semantics directly: return each student for whom no matching enrolment
    row exists in the target semester.  This is more readable than the
    equivalent LEFT JOIN … WHERE IS NULL pattern and is the idiomatic SQL
    choice when the intent is to assert the absence of a related row.
    """
    query = """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            p.program_name,
            s.year_of_study,
            s.email
        FROM students AS s
        INNER JOIN programs AS p
            ON s.program_id = p.program_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM enrolments AS e
            WHERE e.student_id = s.student_id
              AND e.semester = ?
        )
        ORDER BY student_name;
    """
    return run_query(query, (semester,))


def get_advisor_contact(student_id: str) -> pd.DataFrame:
    """Retrieve the faculty advisor's contact details for a student."""
    query = """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            l.lecturer_id AS advisor_id,
            l.first_name || ' ' || l.last_name AS advisor_name,
            l.email AS advisor_email,
            l.phone AS advisor_phone,
            d.department_name AS advisor_department
        FROM students AS s
        INNER JOIN lecturers AS l
            ON s.advisor_lecturer_id = l.lecturer_id
        INNER JOIN departments AS d
            ON l.department_id = d.department_id
        WHERE s.student_id = ?;
    """
    return run_query(query, (student_id,))


def search_lecturers_by_expertise(expertise_keyword: str) -> pd.DataFrame:
    """Search lecturers whose expertise area contains the keyword."""
    # LOWER on both sides makes the search case-insensitive without a collation
    query = """
        SELECT
            l.lecturer_id,
            l.first_name || ' ' || l.last_name AS lecturer_name,
            d.department_name,
            le.expertise_area,
            l.email
        FROM lecturers AS l
        INNER JOIN lecturer_expertise AS le
            ON l.lecturer_id = le.lecturer_id
        INNER JOIN departments AS d
            ON l.department_id = d.department_id
        WHERE LOWER(le.expertise_area) LIKE LOWER(?)
        ORDER BY lecturer_name;
    """
    keyword = f"%{expertise_keyword}%"
    return run_query(query, (keyword,))


def list_courses_by_department(department_id: str) -> pd.DataFrame:
    """Return all courses taught by lecturers in a department."""
    # DISTINCT is required because a course taught across multiple semesters
    # produces one row per teaching_assignment; without it, the same
    # (course, lecturer) pair would appear once per term.
    query = """
        SELECT DISTINCT
            d.department_name,
            c.course_code,
            c.course_name,
            c.course_level,
            c.credits,
            l.first_name || ' ' || l.last_name AS lecturer_name,
            ta.semester
        FROM departments AS d
        INNER JOIN lecturers AS l
            ON d.department_id = l.department_id
        INNER JOIN teaching_assignments AS ta
            ON l.lecturer_id = ta.lecturer_id
        INNER JOIN courses AS c
            ON ta.course_code = c.course_code
        WHERE d.department_id = ?
        ORDER BY c.course_code;
    """
    return run_query(query, (department_id,))


def list_staff_by_department(department_id: str) -> pd.DataFrame:
    """Find non-academic staff employed in a specific department."""
    query = """
        SELECT
            ns.staff_id,
            ns.first_name || ' ' || ns.last_name AS staff_name,
            ns.job_title,
            d.department_name,
            ns.employment_type,
            ns.salary_information
        FROM non_academic_staff AS ns
        INNER JOIN departments AS d
            ON ns.department_id = d.department_id
        WHERE d.department_id = ?
        ORDER BY staff_name;
    """
    return run_query(query, (department_id,))


def list_publications_by_year(publication_year: int) -> pd.DataFrame:
    """Report all lecturer publications for a given calendar year."""
    # LEFT JOIN on research_projects so publications not tied to a project
    # still appear in the results
    query = """
        SELECT
            p.title,
            p.publication_year,
            p.publication_type,
            l.first_name || ' ' || l.last_name AS lecturer_name,
            d.department_name,
            rp.project_title
        FROM publications AS p
        INNER JOIN lecturers AS l
            ON p.lecturer_id = l.lecturer_id
        INNER JOIN departments AS d
            ON l.department_id = d.department_id
        LEFT JOIN research_projects AS rp
            ON p.project_id = rp.project_id
        WHERE p.publication_year = ?
        ORDER BY lecturer_name;
    """
    return run_query(query, (publication_year,))


def rank_lecturers_by_supervision() -> pd.DataFrame:
    """Rank lecturers by the number of distinct student researchers on shared projects.

    A student counts towards a lecturer's total when both appear as members of
    the same research project (joined via project_id).  The self-join on
    research_project_members uses two aliases: lect for the lecturer's own
    membership rows and stud for student rows on the same project.
    """
    # Self-join on research_project_members via project_id: lect finds the
    # lecturer's project memberships; stud finds student members of those same
    # projects.  COUNT(DISTINCT) avoids double-counting if a student holds
    # multiple roles on one project.
    query = """
        SELECT
            l.lecturer_id,
            l.first_name || ' ' || l.last_name AS lecturer_name,
            d.department_name,
            COUNT(DISTINCT stud.student_id) AS student_supervisions
        FROM lecturers AS l
        INNER JOIN departments AS d
            ON l.department_id = d.department_id
        LEFT JOIN research_project_members AS lect
            ON lect.lecturer_id = l.lecturer_id
        LEFT JOIN research_project_members AS stud
            ON stud.project_id = lect.project_id
            AND stud.student_id IS NOT NULL
        GROUP BY l.lecturer_id, lecturer_name, d.department_name
        ORDER BY student_supervisions DESC, l.lecturer_id;
    """
    return run_query(query)


def find_students_by_advisor(lecturer_id: str) -> pd.DataFrame:
    """Retrieve all students currently assigned to a specific advisor."""
    query = """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            s.email,
            p.program_name,
            s.year_of_study,
            s.graduation_status
        FROM students AS s
        INNER JOIN programs AS p
            ON s.program_id = p.program_id
        WHERE s.advisor_lecturer_id = ?
        ORDER BY student_name;
    """
    return run_query(query, (lecturer_id,))
