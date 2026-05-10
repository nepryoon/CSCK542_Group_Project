import pandas as pd

from database import run_query


def find_students_by_course_and_lecturer(
    course_code: str,
    lecturer_id: str,
    semester: str,
) -> pd.DataFrame:
    """Find students enrolled in a course taught by a lecturer."""
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
    """List final-year students with an average grade above a threshold."""
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
    """Find students who have not registered for any course."""
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
        LEFT JOIN enrolments AS e
            ON s.student_id = e.student_id
            AND e.semester = ?
        WHERE e.enrolment_id IS NULL
        ORDER BY student_name;
    """
    return run_query(query, (semester,))


def get_advisor_contact(student_id: str) -> pd.DataFrame:
    """Retrieve advisor contact information for a student."""
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
    """Search for lecturers with expertise in a research area."""
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
    """List courses taught by lecturers in a specific department."""
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
    """Find non-academic staff employed in a department."""
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
    """Generate a report on lecturer publications in a selected year."""
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
