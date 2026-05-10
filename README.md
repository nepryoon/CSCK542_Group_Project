# University Record Management System

## Project Description

This project implements a prototype university record management system.
The system stores information about students, lecturers, departments,
programmes, courses, grades, staff, research projects, and publications.

The database was implemented using SQLite. A Streamlit interface was built
to allow users to execute predefined database queries through Python.

## Technologies Used

- Python
- SQLite
- Streamlit
- pandas

## Project Structure

```text
university_record_system/
├── app.py
├── build_database.py
├── database.py
├── queries.py
├── requirements.txt
├── README.md
├── database/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── university.db
├── diagrams/
│   └── erd.png
├── meeting_minutes/
├── report/
└── video/

How to Run the Project
1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate


2. Install dependencies
pip install -r requirements.txt


3. Build the database
python build_database.py


4. Run the Streamlit application
streamlit run app.py
Available Queries

The application supports the following database queries:

Find students enrolled in a specific course taught by a lecturer.
List final-year students with an average grade above a selected threshold.
Identify students who have not registered for courses in a semester.
Retrieve advisor contact information for a selected student.
Search lecturers by expertise.
List courses taught by lecturers in a department.
Find non-academic staff in a department.
Generate a report on publications by year.
Database Design Summary

The system uses a relational database design. Core entities include students,
lecturers, departments, programmes, courses, staff, research projects, and
publications. Many-to-many relationships are handled through junction tables.
For example, enrolments links students and courses, while teaching_assignments
links lecturers and courses. Multi-valued attributes such as grades, lecturer
expertise areas, qualifications, and publications are stored in separate tables
to avoid storing multiple values in a single database cell.

Notes

The project uses dummy data for demonstration purposes. The database can be
rebuilt at any time by running build_database.py.