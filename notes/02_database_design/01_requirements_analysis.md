## Database Requirements Analysis

Database requirements analysis is a crucial phase in the database design process. It defines the scope and features of the database, ensuring that it meets the needs of its users and supports the objectives of the business.

## Database Requirements Analysis Process

### Stakeholder Identification
- Recognize all individuals and groups involved in the project, including end users, developers, and management.
- Engage these stakeholders in conversations to understand their requirements and expectations.

### Business Domain Understanding
- Establish an in-depth understanding of the organization's operations, goals, and constraints.
- Identify essential data entities, their relationships, and attributes that the database needs to represent.

### Scope Definition
- Explicitly determine the range and functionality of the database system.
- Recognize constraints such as budget, timeline, or specific technology requirements.

### Requirement Collection and Documentation
- Assemble and document functional requirements like data storage, data retrieval, and data manipulation needs.
- Gather and detail non-functional requirements such as performance, scalability, security, and maintainability.

### Requirement Prioritization
- Organize requirements based on their importance to the project and stakeholders.
- Recognize any contradicting requirements and work with stakeholders to reconcile them.

### Requirement Validation and Verification
- Revisit the requirements with stakeholders to ensure they correctly capture their needs and expectations.
- Authenticate the feasibility and consistency of the requirements within the defined project scope and constraints.

## Considerations During Database Requirements Analysis

### Data Model Selection
- Choose a fitting data model that aligns with the organization's data structure, relationships, and access patterns.

### Scalability Considerations
- Plan for the system's ability to manage increased data volumes and user loads.
- Ascertain the need for horizontal (more machines) or vertical scaling (more power on the same machine).

### Performance Requirements
- Define performance metrics for read and write operations, latency, and throughput.
- Identify possible performance issues and develop strategies for optimization.

### Data Integrity and Consistency
- Identify the level of data integrity and consistency the application requires.
- Implement rules and constraints to preserve data integrity, such as primary keys, foreign keys, and unique, check, and not null constraints.

### Security and Compliance Measures
- Evaluate the database's security needs, including user access control, data encryption, and auditing.
- Determine any regulatory or industry compliance standards that could influence the database design.

### Integration and Interoperability
- Consider the necessity for integration with existing systems or data sources.
- Identify any requirements related to data migration or conversion.

## Example: University Database System

### Stakeholder Identification

- University Administration
- Faculty Members
- Students
- IT Department

### Business Domain Understanding

- Processes in a university context include course registration, student enrollment, and grade management.
- Primary data entities: Students, Courses, Professors, and Course Enrollments.

### Scope Definition

- The database is tasked with storing and managing vital data about students, courses, and course enrollments.
- Constraints: Operating within a limited budget, the system must be implemented within a 6-month timeline, and must exclusively utilize open-source technologies.

### Requirements Collection and Documentation

#### Functional Requirements:

- Maintain a record of student details (name, student ID, contact details, enrolled program).
- Store details about courses (course ID, name, description, assigned professor, schedule).
- Keep track of enrollment details (student, enrolled course, semester, grade).
- Enable retrieval of a list of courses offered in a specific semester.
- Support retrieval of a list of students enrolled in a particular course.
- Facilitate updates to student contact details.
- Enable modifications to course details.
- Record grading information for students enrolled in courses.

#### Non-functional Requirements:

- Performance: Query response times should not exceed 2 seconds.
- Scalability: The system should efficiently handle up to 10,000 students and 1,000 courses.
- Security: Ensure data access and modification only by authorized personnel.
- Maintainability: The system should be designed for easy updates and maintenance.

### Requirements Prioritization

- Essential: Storing and retrieving core data related to students, courses, and enrollments.
- Important: Facilitating updates to student and course details, and recording of grades.
- Desirable: Achieving fast response times, scalability, strong security, and maintainability.

### Requirements Validation and Verification

- Discuss and confirm requirements with stakeholders to ensure they meet their needs and expectations.
- Ensure that the listed requirements can be realistically implemented within the defined project scope and constraints.

#### Example Data Tables:

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

In this database model, four tables have been designed: 'Students', 'Courses', 'Professors', and 'Enrollments'. Primary keys (PK) and foreign keys (FK) are indicated in the brackets. The tables are related as follows:

- The 'student_id' in the 'Enrollments' table refers to the 'student_id' primary key in the 'Students' table (foreign key).
- The 'course_id' in the 'Enrollments' table links to the 'course_id' primary key in the 'Courses' table (foreign key).
- The 'professor_id' in the 'Courses' table associates with the 'professor_id' primary key in the 'Professors' table (foreign key).
