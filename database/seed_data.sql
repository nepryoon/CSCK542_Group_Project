INSERT INTO departments VALUES
('D001', 'Computer Science', 'Faculty of Science and Engineering',
 'Artificial intelligence, databases, cybersecurity'),
('D002', 'Business Analytics', 'Faculty of Business',
 'Data analytics, decision science, digital business'),
('D003', 'Law', 'Faculty of Humanities and Social Sciences',
 'Technology law, commercial law, regulation'),
('D004', 'Student Services', 'Professional Services',
 'Student administration and welfare');

INSERT INTO programs VALUES
('P001', 'BSc Computer Science', 'Bachelor of Science', 3, 'D001',
 'Full time undergraduate programme'),
('P002', 'MSc Data Science and AI', 'Master of Science', 2, 'D001',
 'Postgraduate taught programme'),
('P003', 'BSc Business Analytics', 'Bachelor of Science', 3, 'D002',
 'Undergraduate business analytics programme'),
('P004', 'LLB Law and Technology', 'Bachelor of Laws', 3, 'D003',
 'Law programme with technology focus');

INSERT INTO lecturers VALUES
('L001', 'John', 'Smith', 'john.smith@university.edu', '0207000001',
 'D001', 3, 'Databases and distributed systems'),
('L002', 'Emily', 'Clark', 'emily.clark@university.edu', '0207000002',
 'D001', 2, 'Artificial intelligence and machine learning'),
('L003', 'Michael', 'Brown', 'michael.brown@university.edu',
 '0207000003', 'D002', 2, 'Business analytics and forecasting'),
('L004', 'Sarah', 'Wilson', 'sarah.wilson@university.edu',
 '0207000004', 'D003', 1, 'Technology law and data protection'),
('L005', 'David', 'Nguyen', 'david.nguyen@university.edu',
 '0207000005', 'D001', 2, 'Cybersecurity and cloud computing');

INSERT INTO students VALUES
('S001', 'Alice', 'Taylor', '2003-05-12',
 'alice.taylor@student.edu', '070000001', 'P001', 3,
 'Not graduated', 'L001'),
('S002', 'Ben', 'Johnson', '2004-01-22',
 'ben.johnson@student.edu', '070000002', 'P001', 2,
 'Not graduated', 'L002'),
('S003', 'Chloe', 'Martin', '2002-09-15',
 'chloe.martin@student.edu', '070000003', 'P001', 3,
 'Not graduated', 'L001'),
('S004', 'Daniel', 'Lee', '2001-11-03',
 'daniel.lee@student.edu', '070000004', 'P002', 2,
 'Not graduated', 'L002'),
('S005', 'Emma', 'Davis', '2003-03-27',
 'emma.davis@student.edu', '070000005', 'P003', 3,
 'Not graduated', 'L003'),
('S006', 'Farah', 'Khan', '2004-07-09',
 'farah.khan@student.edu', '070000006', 'P003', 1,
 'Not graduated', 'L003'),
('S007', 'George', 'Miller', '2002-12-18',
 'george.miller@student.edu', '070000007', 'P004', 3,
 'Not graduated', 'L004'),
('S008', 'Hannah', 'White', '2005-02-02',
 'hannah.white@student.edu', '070000008', 'P001', 1,
 'Not graduated', 'L005'),
('S009', 'Ibrahim', 'Ali', '2003-08-20',
 'ibrahim.ali@student.edu', '070000009', 'P002', 2,
 'Not graduated', 'L002'),
('S010', 'Julia', 'Green', '2004-10-11',
 'julia.green@student.edu', '070000010', 'P003', 2,
 'Not graduated', 'L003');

INSERT INTO non_academic_staff VALUES
('N001', 'Olivia', 'Hall', 'Admissions Officer', 'D004',
 'Full time', 'Permanent contract', 35000, 'Mark Hall 070001111'),
('N002', 'Peter', 'Young', 'Department Administrator', 'D001',
 'Full time', 'Permanent contract', 38000, 'Laura Young 070002222'),
('N003', 'Grace', 'King', 'Finance Officer', 'D002',
 'Part time', 'Fixed term contract', 28000, 'Tom King 070003333'),
('N004', 'Noah', 'Scott', 'Student Welfare Officer', 'D004',
 'Full time', 'Permanent contract', 36000, 'Eva Scott 070004444');

INSERT INTO courses VALUES
('DB101', 'Database Systems',
 'Introduction to relational database design and SQL', 'D001',
 'Undergraduate', 15, 'Monday 10:00', 'Lecture slides and lab sheets'),
('AI201', 'Artificial Intelligence',
 'Core AI concepts and machine learning applications', 'D001',
 'Undergraduate', 15, 'Tuesday 14:00', 'Notebook exercises'),
('CY301', 'Cybersecurity Fundamentals',
 'Security principles and risk management', 'D001',
 'Undergraduate', 15, 'Wednesday 09:00', 'Case studies'),
('BA101', 'Business Analytics',
 'Data analysis for business decision making', 'D002',
 'Undergraduate', 15, 'Thursday 11:00', 'Analytics workbook'),
('LAW201', 'Technology Law',
 'Legal issues in digital technology and data governance', 'D003',
 'Undergraduate', 15, 'Friday 13:00', 'Reading list'),
('DS501', 'Advanced Data Science',
 'Advanced modelling and data science workflows', 'D001',
 'Postgraduate', 20, 'Monday 16:00', 'Research papers');

INSERT INTO teaching_assignments
(lecturer_id, course_code, semester) VALUES
('L001', 'DB101', '2026S1'),
('L002', 'AI201', '2026S1'),
('L005', 'CY301', '2026S1'),
('L003', 'BA101', '2026S1'),
('L004', 'LAW201', '2026S1'),
('L002', 'DS501', '2026S1');

INSERT INTO enrolments
(student_id, course_code, semester) VALUES
('S001', 'DB101', '2026S1'),
('S001', 'AI201', '2026S1'),
('S002', 'DB101', '2026S1'),
('S002', 'CY301', '2026S1'),
('S003', 'DB101', '2026S1'),
('S003', 'AI201', '2026S1'),
('S004', 'DS501', '2026S1'),
('S005', 'BA101', '2026S1'),
('S006', 'BA101', '2026S1'),
('S007', 'LAW201', '2026S1'),
('S008', 'AI201', '2026S1'),
('S009', 'DS501', '2026S1');

INSERT INTO grades
(student_id, course_code, semester, grade) VALUES
('S001', 'DB101', '2026S1', 82),
('S001', 'AI201', '2026S1', 76),
('S002', 'DB101', '2026S1', 65),
('S002', 'CY301', '2026S1', 69),
('S003', 'DB101', '2026S1', 88),
('S003', 'AI201', '2026S1', 91),
('S004', 'DS501', '2026S1', 74),
('S005', 'BA101', '2026S1', 79),
('S006', 'BA101', '2026S1', 58),
('S007', 'LAW201', '2026S1', 81),
('S008', 'AI201', '2026S1', 72),
('S009', 'DS501', '2026S1', 68);

INSERT INTO disciplinary_records
(student_id, record_date, description, outcome) VALUES
('S002', '2026-03-10', 'Late submission misconduct warning',
 'Formal warning'),
('S006', '2026-04-02', 'Library equipment damage',
 'Restitution completed');

INSERT INTO lecturer_qualifications
(lecturer_id, qualification, awarding_institution, award_year) VALUES
('L001', 'PhD in Computer Science', 'University of Manchester', 2016),
('L002', 'PhD in Artificial Intelligence', 'University of Edinburgh', 2018),
('L003', 'PhD in Business Analytics', 'University of Liverpool', 2017),
('L004', 'PhD in Law', 'University of Leeds', 2015),
('L005', 'PhD in Cybersecurity', 'University of Bristol', 2019);

INSERT INTO lecturer_expertise
(lecturer_id, expertise_area) VALUES
('L001', 'Databases'),
('L001', 'Distributed Systems'),
('L002', 'Artificial Intelligence'),
('L002', 'Machine Learning'),
('L003', 'Business Analytics'),
('L003', 'Forecasting'),
('L004', 'Technology Law'),
('L004', 'Data Protection'),
('L005', 'Cybersecurity'),
('L005', 'Cloud Computing');

INSERT INTO research_projects VALUES
('R001', 'AI Supported Student Analytics', 'L002',
 'UKRI', 'Prototype completed'),
('R002', 'Secure Cloud Database Systems', 'L005',
 'Industry Partner', 'Ongoing'),
('R003', 'Business Forecasting for Universities', 'L003',
 'Internal Grant', 'Final report submitted');

INSERT INTO research_project_members
(project_id, lecturer_id, student_id, role) VALUES
('R001', 'L002', NULL, 'Principal investigator'),
('R001', NULL, 'S004', 'Student researcher'),
('R001', NULL, 'S009', 'Student researcher'),
('R002', 'L005', NULL, 'Principal investigator'),
('R002', 'L001', NULL, 'Co investigator'),
('R003', 'L003', NULL, 'Principal investigator'),
('R003', NULL, 'S005', 'Student researcher');

INSERT INTO publications
(lecturer_id, project_id, title, publication_year, publication_type) VALUES
('L002', 'R001', 'AI Supported Student Analytics in Higher Education',
 2026, 'Journal article'),
('L005', 'R002', 'Secure Cloud Database Systems for Universities',
 2026, 'Conference paper'),
('L003', 'R003', 'Forecasting Student Demand Using Business Analytics',
 2025, 'Journal article'),
('L001', 'R002', 'Relational Database Design for Distributed Systems',
 2026, 'Conference paper');

INSERT INTO student_organisations VALUES
('O001', 'Data Science Society',
 'Student society for analytics and AI'),
('O002', 'Law and Technology Club',
 'Student organisation for digital law topics'),
('O003', 'Cybersecurity Club',
 'Student club for security practice');

INSERT INTO student_org_memberships
(student_id, organisation_id, role) VALUES
('S001', 'O001', 'Member'),
('S003', 'O001', 'Treasurer'),
('S007', 'O002', 'Member'),
('S008', 'O003', 'Member');

INSERT INTO committees VALUES
('C001', 'Teaching Quality Committee',
 'Committee responsible for teaching quality'),
('C002', 'Research Ethics Committee',
 'Committee responsible for ethics review');

INSERT INTO committee_memberships
(lecturer_id, committee_id, role) VALUES
('L001', 'C001', 'Member'),
('L002', 'C002', 'Member'),
('L004', 'C002', 'Chair');
