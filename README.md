This project is a Streamlit-based web app that uses a Genetic Algorithm to automatically generate conflict-free class timetables. It ensures constraints such as subject limits, room availability, and staff conflicts are strictly followed.

Features
Upload custom Excel files: Course, Staff, Students, and Room data.

Generate a conflict-free class timetable using AI.

Automatically avoid:
Room clashes
Staff schedule conflicts
Over-allocation of subjects
Back-to-back duplicate subjects
Export the generated timetable to a PDF.

Required Excel Files
You must upload 4 Excel files to generate the timetable. Below are the required formats and column suggestions:

1. Course.xlsx
Purpose: Contains subject and course mapping info.
Suggested Columns:
Class: e.g., MCA1A, MCA2B

Subject Code: e.g., CS101
Subject Name: e.g., Data Structures
Faculty: e.g., Dr. A Kumar
Type: Theory or Lab
Max Hours/Week: e.g., 4

2. Staff.xlsx
Purpose: Contains staff details.
Suggested Columns:
Faculty Name: e.g., Dr. A Kumar
Department: e.g., Computer Science
Max Load: e.g., 16 hours/week

3. Students.xlsx
Purpose: Class list and student distribution.
Suggested Columns:
Class: e.g., MCA1A
Student Count: e.g., 40

4. Room.xlsx
Purpose: List of available rooms and lab facilities.
Suggested Columns:
Room Number: e.g., CS101
Type: Theory or Lab
Capacity: e.g., 60

