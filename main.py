import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from queries import (
    find_students_by_course_and_lecturer,
    find_final_year_students_above_grade,
    find_students_without_registration,
    get_advisor_contact,
    search_lecturers_by_expertise,
    list_courses_by_department,
    list_staff_by_department,
    list_publications_by_year,
    rank_lecturers_by_supervision,
    find_students_by_advisor,
)
from database import build_where, run_query

app = FastAPI(title="University Record Management System")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# --- Page routes ---

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/students")
def students_page():
    return FileResponse(BASE_DIR / "static" / "students.html")


@app.get("/lecturers")
def lecturers_page():
    return FileResponse(BASE_DIR / "static" / "lecturers.html")


@app.get("/queries")
def queries_page():
    return FileResponse(BASE_DIR / "static" / "queries.html")


@app.get("/research")
def research_page():
    return FileResponse(BASE_DIR / "static" / "research.html")


@app.get("/courses")
def courses_page():
    return FileResponse(BASE_DIR / "static" / "courses.html")


@app.get("/departments")
def departments_page():
    return FileResponse(BASE_DIR / "static" / "departments.html")


# --- Dashboard API ---

@app.get("/api/dashboard")
def dashboard():
    # Separate queries per entity keep each count readable and let us add
    # new metrics later without touching a single monolithic aggregation.
    students = run_query(
        "SELECT COUNT(*) AS count FROM students"
    ).iloc[0]["count"]
    lecturers = run_query(
        "SELECT COUNT(*) AS count FROM lecturers"
    ).iloc[0]["count"]
    courses = run_query(
        "SELECT COUNT(*) AS count FROM courses"
    ).iloc[0]["count"]
    departments = run_query(
        "SELECT COUNT(*) AS count FROM departments"
    ).iloc[0]["count"]
    programs = run_query(
        "SELECT COUNT(*) AS count FROM programs"
    ).iloc[0]["count"]
    research = run_query(
        "SELECT COUNT(*) AS count FROM research_projects"
    ).iloc[0]["count"]
    return {
        "students": int(students),
        "lecturers": int(lecturers),
        "courses": int(courses),
        "departments": int(departments),
        "programs": int(programs),
        "research_projects": int(research),
    }


# --- Students API ---

@app.get("/api/students")
def get_students(search: str = "", status: str = ""):
    # build WHERE clauses dynamically so every combination of filters
    # runs a single focused query rather than fetching everything and slicing
    conditions = []
    params: list = []

    if search:
        conditions.append(
            "(LOWER(s.first_name || ' ' || s.last_name) LIKE LOWER(?)"
            " OR LOWER(s.student_id) LIKE LOWER(?)"
            " OR LOWER(s.email) LIKE LOWER(?))"
        )
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]

    if status:
        conditions.append("s.graduation_status = ?")
        params.append(status)

    where, where_params = build_where(conditions, params)

    df = run_query(
        f"""
        SELECT s.student_id,
               s.first_name || ' ' || s.last_name AS name,
               s.email, s.phone, p.program_name, s.year_of_study,
               s.graduation_status,
               l.first_name || ' ' || l.last_name AS advisor,
               s.advisor_lecturer_id
        FROM students s
        JOIN programs p ON s.program_id = p.program_id
        LEFT JOIN lecturers l
            ON s.advisor_lecturer_id = l.lecturer_id
        {where}
        ORDER BY s.student_id
        """,
        where_params,
    )
    return df.to_dict(orient="records")


@app.get("/api/students/{student_id}/courses")
def get_student_courses(student_id: str):
    # grade is in a separate table so a LEFT JOIN keeps courses that
    # haven't been graded yet visible in the UI
    df = run_query(
        """
        SELECT c.course_code, c.course_name, c.credits, e.semester, g.grade
        FROM enrolments e
        JOIN courses c ON e.course_code = c.course_code
        LEFT JOIN grades g ON g.student_id = e.student_id
            AND g.course_code = e.course_code AND g.semester = e.semester
        WHERE e.student_id = ?
        ORDER BY e.semester, c.course_code
        """,
        (student_id,),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No courses found for student {student_id}")
    return df.to_dict(orient="records")


@app.get("/api/students/{student_id}/disciplinary")
def get_student_disciplinary(student_id: str):
    df = run_query(
        """
        SELECT record_date, description, outcome
        FROM disciplinary_records
        WHERE student_id = ?
        ORDER BY record_date DESC
        """,
        (student_id,),
    )
    # disciplinary records are optional, so an empty result is valid
    return df.to_dict(orient="records")


@app.get("/api/students/{student_id}/organisations")
def get_student_organisations(student_id: str):
    df = run_query(
        """
        SELECT so.organisation_name, so.description, som.role
        FROM student_org_memberships som
        JOIN student_organisations so
            ON som.organisation_id = so.organisation_id
        WHERE som.student_id = ?
        ORDER BY so.organisation_name
        """,
        (student_id,),
    )
    # org memberships are optional, so an empty result is valid
    return df.to_dict(orient="records")


# --- Lecturers API ---

@app.get("/api/lecturers")
def get_lecturers(search: str = "", department: str = ""):
    # GROUP_CONCAT aggregates multiple expertise rows into a single
    # comma-separated value so the front end only receives one row per lecturer
    conditions = []
    params: list = []

    if search:
        conditions.append(
            "(LOWER(l.first_name || ' ' || l.last_name) LIKE LOWER(?)"
            " OR LOWER(le.expertise_area) LIKE LOWER(?))"
        )
        params += [f"%{search}%", f"%{search}%"]

    if department:
        conditions.append("d.department_name = ?")
        params.append(department)

    where, where_params = build_where(conditions, params)

    df = run_query(
        f"""
        SELECT l.lecturer_id,
               l.first_name || ' ' || l.last_name AS name,
               l.email, l.phone, d.department_name,
               l.course_load,
               GROUP_CONCAT(DISTINCT le.expertise_area) AS expertise,
               GROUP_CONCAT(DISTINCT lri.research_interest)
                   AS research_interests
        FROM lecturers l
        JOIN departments d ON l.department_id = d.department_id
        LEFT JOIN lecturer_expertise le
            ON l.lecturer_id = le.lecturer_id
        LEFT JOIN lecturer_research_interests lri
            ON l.lecturer_id = lri.lecturer_id
        {where}
        GROUP BY l.lecturer_id
        ORDER BY l.lecturer_id
        """,
        where_params,
    )
    return df.to_dict(orient="records")


@app.get("/api/lecturers/{lecturer_id}/courses")
def get_lecturer_courses(lecturer_id: str):
    df = run_query(
        """
        SELECT c.course_code, c.course_name, c.credits,
               c.course_level, ta.semester
        FROM teaching_assignments ta
        JOIN courses c ON ta.course_code = c.course_code
        WHERE ta.lecturer_id = ?
        ORDER BY ta.semester, c.course_code
        """,
        (lecturer_id,),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No courses found for lecturer {lecturer_id}")
    return df.to_dict(orient="records")


@app.get("/api/lecturers/{lecturer_id}/qualifications")
def get_lecturer_qualifications(lecturer_id: str):
    df = run_query(
        """
        SELECT qualification, awarding_institution, award_year
        FROM lecturer_qualifications
        WHERE lecturer_id = ?
        ORDER BY award_year DESC
        """,
        (lecturer_id,),
    )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No qualifications found for lecturer {lecturer_id}",
        )
    return df.to_dict(orient="records")


@app.get("/api/lecturers/{lecturer_id}/committees")
def get_lecturer_committees(lecturer_id: str):
    df = run_query(
        """
        SELECT c.committee_name, c.description, cm.role
        FROM committee_memberships cm
        JOIN committees c ON cm.committee_id = c.committee_id
        WHERE cm.lecturer_id = ?
        ORDER BY c.committee_name
        """,
        (lecturer_id,),
    )
    # committee memberships are optional, so an empty result is valid
    return df.to_dict(orient="records")


@app.get("/api/lecturers/{lecturer_id}/students")
def get_lecturer_advisees(lecturer_id: str):
    df = run_query(
        """
        SELECT s.student_id,
               s.first_name || ' ' || s.last_name AS student_name,
               p.program_name, s.year_of_study
        FROM students s
        JOIN programs p ON s.program_id = p.program_id
        WHERE s.advisor_lecturer_id = ?
        ORDER BY student_name
        """,
        (lecturer_id,),
    )
    # a lecturer may have no advisees yet, so an empty result is valid
    return df.to_dict(orient="records")


# --- Research API ---

@app.get("/api/research")
def get_research_projects(search: str = "", outcome: str = ""):
    # Conditional COUNT avoids two self-joins or subqueries: a single pass
    # over research_project_members produces both student and lecturer totals.
    conditions = []
    params: list = []

    if search:
        conditions.append(
            "(LOWER(rp.project_title) LIKE LOWER(?)"
            " OR LOWER(l.first_name || ' ' || l.last_name) LIKE LOWER(?)"
            " OR LOWER(d.department_name) LIKE LOWER(?)"
            " OR EXISTS ("
            "     SELECT 1 FROM research_project_funding_sources fs2"
            "     WHERE fs2.project_id = rp.project_id"
            "     AND LOWER(fs2.funding_source) LIKE LOWER(?)"
            " ))"
        )
        params += [f"%{search}%"] * 4

    if outcome:
        conditions.append("rp.outcome = ?")
        params.append(outcome)

    where, where_params = build_where(conditions, params)

    df = run_query(
        f"""
        SELECT rp.project_id, rp.project_title,
               GROUP_CONCAT(DISTINCT fs.funding_source) AS funding_source,
               rp.outcome,
               l.first_name || ' ' || l.last_name AS principal_investigator,
               d.department_name,
               COUNT(
                   DISTINCT CASE
                       WHEN rpm.student_id IS NOT NULL THEN rpm.member_id
                   END
               ) AS student_count,
               COUNT(
                   DISTINCT CASE
                       WHEN rpm.lecturer_id IS NOT NULL THEN rpm.member_id
                   END
               ) AS lecturer_count
        FROM research_projects rp
        JOIN lecturers l
            ON rp.principal_investigator_id = l.lecturer_id
        JOIN departments d ON l.department_id = d.department_id
        LEFT JOIN research_project_members rpm
            ON rp.project_id = rpm.project_id
        LEFT JOIN research_project_funding_sources fs
            ON rp.project_id = fs.project_id
        {where}
        GROUP BY rp.project_id
        ORDER BY rp.project_id
        """,
        where_params,
    )
    return df.to_dict(orient="records")


@app.get("/api/research/{project_id}/members")
def get_project_members(project_id: str):
    # research_project_members stores both lecturers and students in one table;
    # CASE resolves names from whichever foreign key is populated for each row.
    df = run_query(
        """
        SELECT rpm.role,
               CASE
                 WHEN rpm.lecturer_id IS NOT NULL
                   THEN l.first_name || ' ' || l.last_name
                 ELSE s.first_name || ' ' || s.last_name
               END AS member_name,
               CASE
                 WHEN rpm.lecturer_id IS NOT NULL THEN 'Lecturer'
                 ELSE 'Student'
               END AS member_type
        FROM research_project_members rpm
        LEFT JOIN lecturers l ON rpm.lecturer_id = l.lecturer_id
        LEFT JOIN students s ON rpm.student_id = s.student_id
        WHERE rpm.project_id = ?
        ORDER BY rpm.role
        """,
        (project_id,),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No members found for project {project_id}")
    return df.to_dict(orient="records")


@app.get("/api/research/{project_id}/publications")
def get_project_publications(project_id: str):
    df = run_query(
        """
        SELECT p.title, p.publication_year, p.publication_type,
               l.first_name || ' ' || l.last_name AS author
        FROM publications p
        JOIN lecturers l ON p.lecturer_id = l.lecturer_id
        WHERE p.project_id = ?
        ORDER BY p.publication_year DESC
        """,
        (project_id,),
    )
    # a project may have no publications yet, so an empty result is valid
    return df.to_dict(orient="records")


# --- Query API ---
# Each endpoint maps directly to a named query function so the
# front-end can call them by number without knowing the SQL details.

@app.get("/api/query/1")
def query1(course_code: str, lecturer_id: str, semester: str):
    df = find_students_by_course_and_lecturer(
        course_code, lecturer_id, semester
    )
    return df.to_dict(orient="records")


@app.get("/api/query/2")
def query2(minimum_average: float = 70.0):
    df = find_final_year_students_above_grade(minimum_average)
    return df.to_dict(orient="records")


@app.get("/api/query/3")
def query3(semester: str):
    df = find_students_without_registration(semester)
    return df.to_dict(orient="records")


@app.get("/api/query/4")
def query4(student_id: str):
    df = get_advisor_contact(student_id)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No advisor found for student {student_id}")
    return df.to_dict(orient="records")


@app.get("/api/query/5")
def query5(keyword: str):
    df = search_lecturers_by_expertise(keyword)
    return df.to_dict(orient="records")


@app.get("/api/query/6")
def query6(department_id: str):
    df = list_courses_by_department(department_id)
    return df.to_dict(orient="records")


@app.get("/api/query/7")
def query7(department_id: str):
    df = list_staff_by_department(department_id)
    return df.to_dict(orient="records")


@app.get("/api/query/8")
def query8(year: int):
    df = list_publications_by_year(year)
    return df.to_dict(orient="records")


@app.get("/api/query/9")
def query9():
    df = rank_lecturers_by_supervision()
    return df.to_dict(orient="records")


@app.get("/api/query/10")
def query10(lecturer_id: str):
    df = find_students_by_advisor(lecturer_id)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No students found for advisor {lecturer_id}")
    return df.to_dict(orient="records")


# --- Courses API ---

@app.get("/api/courses")
def get_courses(search: str = "", department: str = "", level: str = ""):
    conditions = []
    params: list = []

    if search:
        conditions.append(
            "(LOWER(c.course_code) LIKE LOWER(?)"
            " OR LOWER(c.course_name) LIKE LOWER(?))"
        )
        params += [f"%{search}%", f"%{search}%"]

    if department:
        conditions.append("d.department_name = ?")
        params.append(department)

    if level:
        conditions.append("c.course_level = ?")
        params.append(level)

    where, where_params = build_where(conditions, params)

    df = run_query(
        f"""
        SELECT c.course_code, c.course_name, c.description,
               c.course_level, c.credits, c.schedule, c.materials,
               d.department_name,
               COUNT(DISTINCT e.student_id) AS enrolled
        FROM courses c
        JOIN departments d ON c.department_id = d.department_id
        LEFT JOIN enrolments e ON c.course_code = e.course_code
        {where}
        GROUP BY c.course_code
        ORDER BY c.course_code
        """,
        where_params,
    )
    return df.to_dict(orient="records")


@app.get("/api/courses/{course_code}/enrolments")
def get_course_enrolments(course_code: str):
    df = run_query(
        """
        SELECT e.student_id,
               s.first_name || ' ' || s.last_name AS student_name,
               e.semester, g.grade
        FROM enrolments e
        JOIN students s ON e.student_id = s.student_id
        LEFT JOIN grades g ON g.student_id = e.student_id
            AND g.course_code = e.course_code AND g.semester = e.semester
        WHERE e.course_code = ?
        ORDER BY e.semester, student_name
        """,
        (course_code,),
    )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No enrolments found for course {course_code}",
        )
    return df.to_dict(orient="records")


@app.get("/api/courses/{course_code}/lecturers")
def get_course_lecturers(course_code: str):
    df = run_query(
        """
        SELECT ta.lecturer_id,
               l.first_name || ' ' || l.last_name AS lecturer_name,
               ta.semester
        FROM teaching_assignments ta
        JOIN lecturers l ON ta.lecturer_id = l.lecturer_id
        WHERE ta.course_code = ?
        ORDER BY ta.semester, lecturer_name
        """,
        (course_code,),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No lecturers found for course {course_code}")
    return df.to_dict(orient="records")


# --- Departments API ---

@app.get("/api/departments")
def get_departments(search: str = ""):
    conditions = []
    params: list = []

    if search:
        conditions.append(
            "(LOWER(d.department_name) LIKE LOWER(?)"
            " OR LOWER(d.faculty) LIKE LOWER(?))"
        )
        params += [f"%{search}%", f"%{search}%"]

    where, where_params = build_where(conditions, params)

    df = run_query(
        f"""
        SELECT d.department_id, d.department_name, d.faculty,
               (
                   SELECT COALESCE(json_group_array(dra2.research_area), '[]')
                   FROM department_research_areas dra2
                   WHERE dra2.department_id = d.department_id
               ) AS research_areas,
               COUNT(DISTINCT p.program_id) AS program_count,
               COUNT(DISTINCT l.lecturer_id) AS lecturer_count,
               COUNT(DISTINCT nas.staff_id) AS staff_count
        FROM departments d
        LEFT JOIN programs p ON p.department_id = d.department_id
        LEFT JOIN lecturers l ON l.department_id = d.department_id
        LEFT JOIN non_academic_staff nas ON nas.department_id = d.department_id
        {where}
        GROUP BY d.department_id
        ORDER BY d.department_name
        """,
        where_params,
    )
    records = df.to_dict(orient="records")
    for record in records:
        raw_areas = record.get("research_areas")
        if isinstance(raw_areas, str):
            try:
                parsed = json.loads(raw_areas)
            except json.JSONDecodeError:
                parsed = []
            record["research_areas"] = [
                area for area in parsed if isinstance(area, str) and area
            ]
        elif raw_areas is None:
            record["research_areas"] = []
    return records


@app.get("/api/departments/{department_id}/programs")
def get_department_programs(department_id: str):
    df = run_query(
        """
        SELECT program_id, program_name, degree_awarded,
               duration_years, enrolment_details
        FROM programs
        WHERE department_id = ?
        ORDER BY program_name
        """,
        (department_id,),
    )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No programs found for department {department_id}",
        )
    return df.to_dict(orient="records")


@app.get("/api/departments/{department_id}/staff")
def get_department_staff(department_id: str):
    df = run_query(
        """
        SELECT staff_id,
               first_name || ' ' || last_name AS staff_name,
               job_title, employment_type
        FROM non_academic_staff
        WHERE department_id = ?
        ORDER BY staff_name
        """,
        (department_id,),
    )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No staff found for department {department_id}",
        )
    return df.to_dict(orient="records")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
