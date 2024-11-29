The Student Database Management System is a project designed 
to effectively manage student records in a structured and efficient way.

Course Enrollment Database

Add New Records: Add new student information, including personal details and academic data.
Update Existing Records: Modify details of a student’s record without duplicating entries.
Delete Records: Remove student records efficiently to maintain database accuracy.
Search Records: Retrieve specific student information using filters like name, ID, or academic performance.


Steps:

git clone https://github.com/RyzenStudios/StudentDatabase.git
cd StudentDatabase

py -m pip install flask cx_Oracle

py app.py


This will start a local development server, and the app will be at http://127.0.0.1:5000/