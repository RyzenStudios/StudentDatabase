from flask import Flask, render_template, request, session, redirect, url_for
import cx_Oracle


app = Flask(__name__)
app.secret_key = 'your_secret_key' 


oracle_connection_str = "maeltaib/12310153@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(Host=oracle.scs.ryerson.ca)(Port=1521))(CONNECT_DATA=(SID=orcl)))"

def get_db_connection():
    """Connect to Oracle DB"""
    try:
        connection = cx_Oracle.connect(oracle_connection_str)
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))  
    else:
        return redirect(url_for('login'))  

@app.route('/login')
def login():
    session['user'] = 'user1' 
    return redirect(url_for('dashboard'))  

@app.route('/dashboard')
def dashboard():
    """Display the dashboard with data fetched from Oracle DB."""
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    connection = get_db_connection()
    if connection is None:
        return "Database connection failed."
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM STUDENT")  
    rows = cursor.fetchall()
    connection.close()
    
    return render_template('dashboard.html', username=session['user'], data=rows)


@app.route('/view_table/<table_name>', methods=['GET'])
def view_table(table_name):
    columns = []
    data = []

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name} WHERE ROWNUM = 1")  
        columns = [desc[0] for desc in cursor.description]

        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

    except Exception as e:
        result = f"Error: {e}"
    
    finally:
        cursor.close()
        connection.close()

    return render_template('dashboard.html', data=data, columns=columns, table_name=table_name, result="")


@app.route('/execute', methods=['GET', 'POST'])
def execute():
    result = ""
    table_name = request.form.get('table_name')  
    if request.method == 'POST':
        option = request.form['option']
        connection = get_db_connection()
        cursor = connection.cursor()

        if option == 'drop':
            try:
                cursor.execute(f"DROP TABLE {table_name} CASCADE CONSTRAINTS")
                result = f"{table_name} table dropped successfully!"
            except Exception as e:
                result = f"Error: {e}"


        elif option == 'custom_query':
                    query_input = request.form.get('query_input')
                    try:
                        cursor.execute(query_input)  
                        rows = cursor.fetchall()
                        
                        result = "<table border='1'><tr>"
                        columns = [description[0] for description in cursor.description]
                        result += "".join([f"<th>{col}</th>" for col in columns])
                        result += "</tr>"
                        
                        for row in rows:
                            result += "<tr>"
                            result += "".join([f"<td>{str(cell)}</td>" for cell in row])
                            result += "</tr>"
                        
                        result += "</table>"
                    except Exception as e:
                        result = f"Error: {e}"


        elif option == 'create':
            if table_name == "DEPARTMENT":
                cursor.execute('''CREATE TABLE DEPARTMENT (
                                    DEPARTMENT_NAME VARCHAR2(100) PRIMARY KEY, 
                                    DEPARTMENT_HEAD VARCHAR2 (100) NOT NULL)''')
            elif table_name == "STUDENT":
                cursor.execute('''CREATE TABLE STUDENT (
                                    STUDENT_ID NUMBER PRIMARY KEY,
                                    NAME VARCHAR2(100) NOT NULL,                     
                                    PHONE VARCHAR2(15) NOT NULL UNIQUE,          
                                    EMAIL VARCHAR2(100) NOT NULL UNIQUE,                 
                                    TRANSCRIPT VARCHAR2(500) DEFAULT 'Not available' )''')
            elif table_name == "PROFESSOR":
                cursor.execute('''CREATE TABLE PROFESSOR (
                                    PROF_ID NUMBER PRIMARY KEY,
                                    NAME VARCHAR2(100) NOT NULL,
                                    PHONE VARCHAR2(15) UNIQUE NOT NULL,
                                    EMAIL VARCHAR2(100) UNIQUE NOT NULL,
                                    DEPARTMENT_NAME VARCHAR2(100) NOT NULL,
                                    FOREIGN KEY (DEPARTMENT_NAME) REFERENCES
                                    DEPARTMENT(DEPARTMENT_NAME))''')
                
            elif table_name == "COURSES":
                cursor.execute('''CREATE TABLE COURSES (
                                    COURSE_ID VARCHAR2(7) PRIMARY KEY, 
                                    COURSE_NAME VARCHAR2(100) NOT NULL, 
                                    DEPARTMENT_NAME VARCHAR2(100) NOT NULL,     
                                    FOREIGN KEY (DEPARTMENT_NAME) REFERENCES DEPARTMENT(DEPARTMENT_NAME))''')
            elif table_name == "SECTION":
                cursor.execute('''CREATE TABLE SECTION (
                                    SECTION_ID NUMBER PRIMARY KEY,
                                    COURSE_ID VARCHAR2(7) NOT NULL,
                                    PROF_ID NUMBER NOT NULL,
                                    SECTION_TIME VARCHAR2(20) NOT NULL CHECK (REGEXP_LIKE(SECTION_TIME, '^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$')),
                                    SEMESTER VARCHAR2(10) NOT NULL,
                                    FOREIGN KEY (COURSE_ID) REFERENCES COURSES(COURSE_ID),
                                    FOREIGN KEY (PROF_ID) REFERENCES PROFESSOR(PROF_ID))''')
            elif table_name == "PREREQUISITE":
                cursor.execute('''CREATE TABLE PREREQUISITE (
                                    COURSE_ID VARCHAR2(7) PRIMARY KEY,
                                    PREREQUISITE_COURSE VARCHAR2 (7),
                                    FOREIGN KEY (COURSE_ID) REFERENCES COURSES(COURSE_ID),
                                    FOREIGN KEY (PREREQUISITE_COURSE) REFERENCES
                                    COURSES(COURSE_ID) 
                                )''')
            elif table_name == "ENROLLMENT":
                cursor.execute('''CREATE TABLE ENROLLMENT (
                                    STUDENT_ID NUMBER REFERENCES STUDENT(STUDENT_ID),
                                    SECTION_ID NUMBER REFERENCES SECTION(SECTION_ID),
                                    PRIMARY KEY (STUDENT_ID, SECTION_ID))''')


            result = f"{table_name} table created successfully!"

        elif option == 'populate':
            try:
                if table_name == "DEPARTMENT":
                    cursor.execute("INSERT INTO DEPARTMENT (DEPARTMENT_NAME, DEPARTMENT_HEAD) VALUES ('Computer Science', 'Dr. Abdolreza Abhari')")
                    cursor.execute("INSERT INTO DEPARTMENT (DEPARTMENT_NAME, DEPARTMENT_HEAD) VALUES ('Arts', 'Dr. Amy Peng')")
                    cursor.execute("INSERT INTO DEPARTMENT (DEPARTMENT_NAME, DEPARTMENT_HEAD) VALUES ('The Creative School', 'Charles Falzon')")
                    cursor.execute("INSERT INTO DEPARTMENT (DEPARTMENT_NAME, DEPARTMENT_HEAD) VALUES ('Ted Rogers School of Management', 'Dr. Cynthia Holmes')")
                
                elif table_name == "COURSES":
                    cursor.execute("INSERT INTO COURSES (COURSE_ID, COURSE_NAME, DEPARTMENT_NAME) VALUES ('CPS510', 'Database Systems I', 'Computer Science')")
                    cursor.execute("INSERT INTO COURSES (COURSE_ID, COURSE_NAME, DEPARTMENT_NAME) VALUES ('CPS530', 'Web Systems Development', 'Computer Science')")
                    cursor.execute("INSERT INTO COURSES (COURSE_ID, COURSE_NAME, DEPARTMENT_NAME) VALUES ('CRM100', 'Introduction to Canadian Criminal Justice', 'Arts')")
                    cursor.execute("INSERT INTO COURSES (COURSE_ID, COURSE_NAME, DEPARTMENT_NAME) VALUES ('FDL150', 'Fashion Project Management', 'The Creative School')")

                
                elif table_name == "STUDENT":
                    cursor.execute("INSERT INTO STUDENT (STUDENT_ID, NAME, PHONE, EMAIL) VALUES (501180153, 'Mohamed Eltaib', '647-333-3333', 'maeltaib@torontomu.ca')")
                    cursor.execute("INSERT INTO STUDENT (STUDENT_ID, NAME, PHONE, EMAIL) VALUES (500981017, 'Mohamed Shrief', '647-222-1234', 'mshrief@torontomu.ca')")
                    cursor.execute("INSERT INTO STUDENT (STUDENT_ID, NAME, PHONE, EMAIL) VALUES (501034707, 'Muhammad Muaz', '416-123-3563', 'mmuaz@torontomu.ca')")
                    cursor.execute("INSERT INTO STUDENT (STUDENT_ID, NAME, PHONE, EMAIL) VALUES (501024557, 'Albert Brown', '416-001-0000', 'abrown@torontomu.ca')")
                    cursor.execute("INSERT INTO STUDENT (STUDENT_ID, NAME, PHONE, EMAIL) VALUES (5010245223, 'Gerome Leon', '416-121-0000', 'gleon@torontomu.ca')")

                elif table_name == "PROFESSOR":
                    cursor.execute("INSERT INTO PROFESSOR (PROF_ID, NAME, PHONE, EMAIL, DEPARTMENT_NAME) VALUES (50113, 'Dr. Soheila Bashardoust Tajali', '416-434-4343', 'stajali@torontomu.ca', 'Computer Science')")
                    cursor.execute("INSERT INTO PROFESSOR (PROF_ID, NAME, PHONE, EMAIL, DEPARTMENT_NAME) VALUES (50557, 'Dr. Phil Jones', '416-101-6852', 'pjones@torontomu.ca', 'Arts')")
                    cursor.execute("INSERT INTO PROFESSOR (PROF_ID, NAME, PHONE, EMAIL, DEPARTMENT_NAME) VALUES (59349, 'Dr. Alex Ufkes', '416-646-3551', 'aufkes@torontomu.ca', 'Computer Science')")
                    cursor.execute("INSERT INTO PROFESSOR (PROF_ID, NAME, PHONE, EMAIL, DEPARTMENT_NAME) VALUES (50568, 'Dr. Linda Smith', '647-774-6213', 'lsmith@torontomu.ca', 'The Creative School')")
                
                elif table_name == "SECTION":
                    cursor.execute("INSERT INTO SECTION (SECTION_ID, COURSE_ID, PROF_ID, SECTION_TIME, SEMESTER) VALUES (11, 'CPS510', 50113, '09:00 AM', 'Fall 2024')")
                    cursor.execute("INSERT INTO SECTION (SECTION_ID, COURSE_ID, PROF_ID, SECTION_TIME, SEMESTER) VALUES (12, 'CPS510', 50113, '12:00 PM', 'Fall 2024')")
                    cursor.execute("INSERT INTO SECTION (SECTION_ID, COURSE_ID, PROF_ID, SECTION_TIME, SEMESTER) VALUES (21, 'CPS530', 59349, '11:00 AM', 'Fall 2024')")
                    cursor.execute("INSERT INTO SECTION (SECTION_ID, COURSE_ID, PROF_ID, SECTION_TIME, SEMESTER) VALUES (31, 'CRM100', 50557, '01:00 PM', 'Wint 2025')")
                    cursor.execute("INSERT INTO SECTION (SECTION_ID, COURSE_ID, PROF_ID, SECTION_TIME, SEMESTER) VALUES (41, 'FDL150', 50568, '03:00 PM', 'Wint 2025')")
                
                elif table_name == "PREREQUISITE":
                    cursor.execute("INSERT INTO PREREQUISITE (COURSE_ID, PREREQUISITE_COURSE) VALUES ('CPS530', 'CPS510')")
                    cursor.execute("INSERT INTO PREREQUISITE (COURSE_ID, PREREQUISITE_COURSE) VALUES ('FDL150', NULL)")
                    cursor.execute("INSERT INTO PREREQUISITE (COURSE_ID, PREREQUISITE_COURSE) VALUES ('CRM100', NULL)")

                elif table_name == "ENROLLMENT":
                    cursor.execute("INSERT INTO ENROLLMENT (STUDENT_ID, SECTION_ID) VALUES (501180153, 11)")
                    cursor.execute("INSERT INTO ENROLLMENT (STUDENT_ID, SECTION_ID) VALUES (500981017, 12)")
                    cursor.execute("INSERT INTO ENROLLMENT (STUDENT_ID, SECTION_ID) VALUES (501034707, 11)")
                    cursor.execute("INSERT INTO ENROLLMENT (STUDENT_ID, SECTION_ID) VALUES (501024557, 31)")

                connection.commit()
                result = f"{table_name} table populated successfully!"
            except Exception as e:
                connection.rollback()
                result = f"Error populating {table_name}: {e}"


        elif option == 'custom_query':
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                result = "<table border='1'><tr>"
                
                columns = [description[0] for description in cursor.description]
                
                result += "".join([f"<th>{col}</th>" for col in columns])
                result += "</tr>"
                
                for row in rows:
                    result += "<tr>"
                    result += "".join([f"<td>{str(cell)}</td>" for cell in row])
                    result += "</tr>"
                
                result += "</table>"
            except Exception as e:
                result = f"Error: {e}"


        elif option == 'exit':
            result = "Exiting application."

        cursor.close()
        connection.close()

    return render_template('dashboard.html', result=result, table_name=table_name)


if __name__ == '__main__':
    app.run(debug=True)
