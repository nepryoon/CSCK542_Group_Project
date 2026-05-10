import streamlit as st

from queries import (
    find_final_year_students_above_grade,
    find_students_by_course_and_lecturer,
    find_students_without_registration,
    get_advisor_contact,
    list_courses_by_department,
    list_publications_by_year,
    list_staff_by_department,
    search_lecturers_by_expertise,
)


st.set_page_config(
    page_title="University Record Management System",
    layout="wide",
)


def show_result(dataframe) -> None:
    """Display query results in the Streamlit app."""
    if dataframe.empty:
        st.warning("No records found.")
    else:
        st.dataframe(dataframe, width="stretch")


st.title("University Record Management System")
st.write(
    "This prototype allows users to query a university record "
    "management database."
)

query_option = st.sidebar.selectbox(
    "Select a query",
    [
        "1. Students by course and lecturer",
        "2. Final-year students with average grade above threshold",
        "3. Students without course registration",
        "4. Advisor contact for a student",
        "5. Lecturers by expertise",
        "6. Courses taught by department lecturers",
        "7. Non-academic staff by department",
        "8. Publications by year",
    ],
)

st.sidebar.write("Default semester: 2026S1")

if query_option == "1. Students by course and lecturer":
    st.header("Students Enrolled in a Course Taught by a Lecturer")

    course_code = st.text_input("Course code", value="DB101")
    lecturer_id = st.text_input("Lecturer ID", value="L001")
    semester = st.text_input("Semester", value="2026S1")

    if st.button("Run Query"):
        result = find_students_by_course_and_lecturer(
            course_code,
            lecturer_id,
            semester,
        )
        show_result(result)

elif query_option == "2. Final-year students with average grade above threshold":
    st.header("Final-Year Students with High Average Grades")

    minimum_average = st.number_input(
        "Minimum average grade",
        min_value=0.0,
        max_value=100.0,
        value=70.0,
    )

    if st.button("Run Query"):
        result = find_final_year_students_above_grade(minimum_average)
        show_result(result)

elif query_option == "3. Students without course registration":
    st.header("Students Without Course Registration")

    semester = st.text_input("Semester", value="2026S1")

    if st.button("Run Query"):
        result = find_students_without_registration(semester)
        show_result(result)

elif query_option == "4. Advisor contact for a student":
    st.header("Faculty Advisor Contact Information")

    student_id = st.text_input("Student ID", value="S001")

    if st.button("Run Query"):
        result = get_advisor_contact(student_id)
        show_result(result)

elif query_option == "5. Lecturers by expertise":
    st.header("Search Lecturers by Expertise")

    expertise_keyword = st.text_input(
    "Expertise keyword",
    value="Machine Learning",
)

    if st.button("Run Query"):
        result = search_lecturers_by_expertise(expertise_keyword)
        show_result(result)

elif query_option == "6. Courses taught by department lecturers":
    st.header("Courses Taught by Lecturers in a Department")

    department_id = st.text_input("Department ID", value="D001")

    if st.button("Run Query"):
        result = list_courses_by_department(department_id)
        show_result(result)

elif query_option == "7. Non-academic staff by department":
    st.header("Non-Academic Staff by Department")

    department_id = st.text_input("Department ID", value="D004")

    if st.button("Run Query"):
        result = list_staff_by_department(department_id)
        show_result(result)

elif query_option == "8. Publications by year":
    st.header("Lecturer Publications by Year")

    publication_year = st.number_input(
        "Publication year",
        min_value=2000,
        max_value=2030,
        value=2026,
    )

    if st.button("Run Query"):
        result = list_publications_by_year(publication_year)
        show_result(result)
