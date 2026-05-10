PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS committee_memberships;
DROP TABLE IF EXISTS committees;
DROP TABLE IF EXISTS student_org_memberships;
DROP TABLE IF EXISTS student_organisations;
DROP TABLE IF EXISTS publications;
DROP TABLE IF EXISTS research_project_members;
DROP TABLE IF EXISTS research_projects;
DROP TABLE IF EXISTS lecturer_expertise;
DROP TABLE IF EXISTS lecturer_qualifications;
DROP TABLE IF EXISTS disciplinary_records;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS teaching_assignments;
DROP TABLE IF EXISTS enrolments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS non_academic_staff;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS lecturers;
DROP TABLE IF EXISTS programs;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id TEXT PRIMARY KEY,
    department_name TEXT NOT NULL,
    faculty TEXT NOT NULL,
    research_areas TEXT
);

CREATE TABLE programs (
    program_id TEXT PRIMARY KEY,
    program_name TEXT NOT NULL,
    degree_awarded TEXT NOT NULL,
    duration_years INTEGER NOT NULL,
    department_id TEXT NOT NULL,
    enrolment_details TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE lecturers (
    lecturer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    department_id TEXT NOT NULL,
    course_load INTEGER DEFAULT 0,
    research_interests TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    program_id TEXT NOT NULL,
    year_of_study INTEGER NOT NULL,
    graduation_status TEXT NOT NULL,
    advisor_lecturer_id TEXT,
    FOREIGN KEY (program_id) REFERENCES programs(program_id),
    FOREIGN KEY (advisor_lecturer_id) REFERENCES lecturers(lecturer_id)
);

CREATE TABLE non_academic_staff (
    staff_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    department_id TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    contract_details TEXT,
    salary_information REAL,
    emergency_contact TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE courses (
    course_code TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    description TEXT,
    department_id TEXT NOT NULL,
    course_level TEXT NOT NULL,
    credits INTEGER NOT NULL,
    schedule TEXT,
    materials TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE enrolments (
    enrolment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    semester TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
);

CREATE TABLE teaching_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    semester TEXT NOT NULL,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
);

CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    semester TEXT NOT NULL,
    grade REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
);

CREATE TABLE disciplinary_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    record_date TEXT NOT NULL,
    description TEXT NOT NULL,
    outcome TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE lecturer_qualifications (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id TEXT NOT NULL,
    qualification TEXT NOT NULL,
    awarding_institution TEXT,
    award_year INTEGER,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id)
);

CREATE TABLE lecturer_expertise (
    expertise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id TEXT NOT NULL,
    expertise_area TEXT NOT NULL,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id)
);

CREATE TABLE research_projects (
    project_id TEXT PRIMARY KEY,
    project_title TEXT NOT NULL,
    principal_investigator_id TEXT NOT NULL,
    funding_source TEXT,
    outcome TEXT,
    FOREIGN KEY (principal_investigator_id)
        REFERENCES lecturers(lecturer_id)
);

CREATE TABLE research_project_members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    lecturer_id TEXT,
    student_id TEXT,
    role TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES research_projects(project_id),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE publications (
    publication_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id TEXT NOT NULL,
    project_id TEXT,
    title TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    publication_type TEXT,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id),
    FOREIGN KEY (project_id) REFERENCES research_projects(project_id)
);

CREATE TABLE student_organisations (
    organisation_id TEXT PRIMARY KEY,
    organisation_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE student_org_memberships (
    membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    organisation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (organisation_id)
        REFERENCES student_organisations(organisation_id)
);

CREATE TABLE committees (
    committee_id TEXT PRIMARY KEY,
    committee_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE committee_memberships (
    membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id TEXT NOT NULL,
    committee_id TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id),
    FOREIGN KEY (committee_id) REFERENCES committees(committee_id)
);