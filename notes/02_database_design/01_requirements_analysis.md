## Requirements Analysis and Example

Requirements analysis is an important step in database design. It helps define the scope and functionality of the database system.

## Requirements Analysis Process

### Identify Stakeholders

- Identify the individuals and groups participating in the project, including users, developers, and management.
- Engage stakeholders in discussions to collect their needs and expectations.

### Understand the Business Domain

- Develop a comprehensive understanding of the organization's processes, goals, and limitations.
- Identify the crucial data entities, relationships, and attributes that need to be represented in the database.

### Define the Scope

- Clearly define the boundaries of the database system, including its intended purpose and functionality.
- Identify any limitations, such as budget, timeline, or technology requirements.

### Collect and Document Requirements

- Gather and document functional requirements, such as data storage, data retrieval, and data manipulation operations.
- Gather and document non-functional requirements, such as performance, scalability, security, and maintainability.

### Prioritize Requirements

- Rank requirements based on their significance to the project and the stakeholders.
- Identify any conflicting requirements and collaborate with stakeholders to resolve them.

### Validate and Verify Requirements

- Review the requirements with stakeholders to ensure they accurately represent their needs and expectations.
- Verify the feasibility and consistency of the requirements with the project scope and constraints.

## Key Considerations in Requirements Analysis

### Data Model

- Select an appropriate data model based on the organization's data structure, relationships, and access patterns.

### Scalability

- Consider the system's capacity to handle increasing data volumes and user loads.
- Evaluate the necessity for horizontal or vertical scaling.

### Performance

- Assess the performance requirements for read and write operations, latency, and throughput.
- Identify potential bottlenecks and optimization strategies.

### Data Integrity and Consistency

- Determine the level of data integrity and consistency required by the application.
- Establish rules and constraints to maintain data integrity, such as primary keys, foreign keys, and constraints.

### Security and Compliance

- Evaluate the security requirements, including access control, encryption, and auditing.
- Identify any regulatory or industry compliance requirements that may impact the database design.

### Integration and Interoperability

- Consider the need for integration with other systems or data sources.
- Identify any data migration or conversion requirements.

## Example: University Database

### Identify Stakeholders

- University administrators
- Professors
- Students
- IT department

### Understand the Business Domain

- University processes include course registration, student enrollment, and grading.
- Key data entities: students, courses, professors, and enrollments.

### Define the Scope

- The database will store and manage information about students, courses, and enrollments.
- Constraints: limited budget, implementation within 6 months, using open-source technologies.

### Collect and Document Requirements

#### Functional Requirements:

- Store student information (name, student ID, contact details, program).
- Store course information (course ID, name, description, professor, schedule).
- Store enrollment information (student, course, semester, grade).
- Retrieve a list of courses offered in a semester.
- Retrieve a list of students enrolled in a specific course.
- Update student contact details.
- Update course details.
- Record grades for enrolled students.

#### Non-functional Requirements:

- Performance: Response time for queries should not exceed 2 seconds.
- Scalability: The database should handle up to 10,000 students and 1,000 courses.
- Security: Only authorized users can access and modify data.
- Maintainability: The database should be easy to update and maintain.

### E. Prioritize Requirements

- Essential: Storing and retrieving student, course, and enrollment information.
- Important: Updating student and course details, recording grades.
- Desirable: Fast response times, scalability, security, and maintainability.

### F. Validate and Verify Requirements

- Review the requirements with stakeholders to ensure they meet their needs.
- Verify that the requirements are feasible within the project scope and constraints.

1. Students

| student_id (PK) | name        | contact_details | program      |
|-----------------|-------------|-----------------|--------------|
| 1               | John Doe    | 123-456-7890    | Computer Science |
| 2               | Jane Smith  | 234-567-8901    | Mathematics     |
| 3               | Alice Brown | 345-678-9012    | Physics         |

2. Courses

| course_id (PK) | name          | description | professor_id (FK) | schedule   |
|---------------|---------------|-------------|-------------------|------------|
| CS101         | Programming I | Intro to programming | 1            | MWF 10:00-11:00 |
| MA101         | Calculus I    | Intro to calculus    | 2            | TTh 14:00-15:30 |
| PH101         | Physics I     | Intro to physics     | 3            | MWF 13:00-14:00 |

3. Professors

| professor_id (PK) | name          | department   |
|-------------------|---------------|--------------|
| 1                 | Dr. Alan Turing  | Computer Science |
| 2                 | Dr. Isaac Newton | Mathematics     |
| 3                 | Dr. Albert Einstein | Physics         |

4. Enrollments

| enrollment_id (PK) | student_id (FK) | course_id (FK) | semester   | grade |
|--------------------|-----------------|---------------|------------|-------|
| 1                  | 1               | CS101         | Fall 2022  | A     |
| 2                  | 1               | MA101         | Fall 2022  | B+    |
| 3                  | 2               | MA101         | Fall 2022  | A-    |

In this example, we have four tables: Students, Courses, Professors, and Enrollments. The primary keys (PK) and foreign keys (FK) are indicated in parentheses. The tables are related as follows:

- The student_id in the Enrollments table is a foreign key that refers to the student_id primary key in the Students table.
- The course_id in the Enrollments table is a foreign key that refers to the course_id primary key in the Courses table.
- The professor_id in the Courses table is a foreign key that refers to the professor_id primary key in the Professors table.
