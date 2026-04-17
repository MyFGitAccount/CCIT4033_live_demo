# university_app/views.py - COMPLETE WORKING VERSION
import re
import sqlite3
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
from datetime import datetime
from .models import *

def get_db_connection():
    """Get database connection with custom pragmas"""
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA recursive_triggers = ON")
    return connection

def execute_sql(sql, params=None):
    """Execute SQL and return results"""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        if sql.strip().upper().startswith('SELECT'):
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        return cursor.rowcount

def dashboard(request):
    """Main dashboard view"""
    stats = {}

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Student WHERE IsDeleted = 0")
        stats['total_students'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Student WHERE Status = 'Active' AND IsDeleted = 0")
        stats['active_students'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Student WHERE AcademicStanding = 'Academic Probation'")
        stats['probation_students'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Teacher WHERE IsDeleted = 0")
        stats['total_teachers'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Course WHERE IsDeleted = 0")
        stats['total_courses'] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM Section s
            JOIN AcademicTerm t ON s.TermID = t.TermID
            WHERE t.IsCurrent = 1 AND s.Status = 'Active'
        """)
        stats['active_sections'] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM Enrollment e
            JOIN Section s ON e.SectionID = s.SectionID
            JOIN AcademicTerm t ON s.TermID = t.TermID
            WHERE t.IsCurrent = 1 AND e.Status = 'Enrolled'
        """)
        stats['current_enrollments'] = cursor.fetchone()[0]

    recent_logs = execute_sql("""
        SELECT LogID, TableName, Action, TriggerName, ChangedBy, ChangedAt
        FROM AuditLog
        ORDER BY ChangedAt DESC
        LIMIT 20
    """)

    top_students = execute_sql("""
        SELECT StudentNumber, FirstName || ' ' || LastName as Name, CumulativeGPA, AcademicStanding
        FROM Student
        WHERE IsDeleted = 0 AND CumulativeGPA > 0
        ORDER BY CumulativeGPA DESC
        LIMIT 10
    """)

    context = {
        'stats': stats,
        'recent_logs': recent_logs,
        'top_students': top_students,
    }
    return render(request, 'dashboard.html', context)

# ============= DATA ENTRY VIEWS =============

def add_student(request):
    """Add a new student"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Student")
                count = cursor.fetchone()[0] + 1
                student_number = f"STU{datetime.now().year}{count:04d}"

            sql = """
                INSERT INTO Student (
                    StudentNumber, FirstName, LastName, Email,
                    Status, IsDeleted
                ) VALUES (?, ?, ?, ?, 'Active', 0)
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    student_number,
                    request.POST.get('first_name'),
                    request.POST.get('last_name'),
                    request.POST.get('email'),
                ])

            messages.success(request, f'Student {student_number} added successfully!')
            return redirect('add_student')
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')

    departments = Department.objects.filter(is_active=True, is_deleted=False)
    return render(request, 'add_student.html', {'departments': departments})

def add_course(request):
    """Add a new course"""
    if request.method == 'POST':
        try:
            sql = """
                INSERT INTO Course (CourseCode, CourseName, Credits, DepartmentID, IsActive, IsDeleted)
                VALUES (?, ?, ?, ?, 1, 0)
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    request.POST.get('course_code'),
                    request.POST.get('course_name'),
                    int(request.POST.get('credits')),
                    int(request.POST.get('department_id')) if request.POST.get('department_id') else 1
                ])

            messages.success(request, 'Course added successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding course: {str(e)}')

    departments = Department.objects.filter(is_active=True, is_deleted=False)
    return render(request, 'add_course.html', {'departments': departments})

def add_section(request):
    """Add a new section"""
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Section")
                count = cursor.fetchone()[0] + 1
                section_code = f"SECT{datetime.now().year}{count:04d}"

            sql = """
                INSERT INTO Section (
                    SectionCode, SectionName, TermID, CourseID, TeacherID,
                    RoomID, Schedule, MaxCapacity, Status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    section_code,
                    request.POST.get('section_name'),
                    int(request.POST.get('term_id')) if request.POST.get('term_id') else 1,
                    int(request.POST.get('course_id')),
                    int(request.POST.get('teacher_id')) if request.POST.get('teacher_id') else None,
                    int(request.POST.get('room_id')) if request.POST.get('room_id') else None,
                    request.POST.get('schedule'),
                    int(request.POST.get('max_capacity', 40))
                ])

            messages.success(request, f'Section {section_code} added successfully!')
            return redirect('add_section')
        except Exception as e:
            messages.error(request, f'Error adding section: {str(e)}')

    courses = Course.objects.filter(is_active=True, is_deleted=False)
    teachers = Teacher.objects.filter(status='Active', is_deleted=False)
    classrooms = Classroom.objects.all()
    terms = AcademicTerm.objects.filter(is_active=True)

    context = {
        'courses': courses,
        'teachers': teachers,
        'classrooms': classrooms,
        'terms': terms,
    }
    return render(request, 'add_section.html', context)

def enroll_student(request):
    """Enroll a student in a section"""
    if request.method == 'POST':
        try:
            sql = """
                INSERT INTO Enrollment (StudentID, SectionID, Status)
                VALUES (?, ?, 'Enrolled')
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    int(request.POST.get('student_id')),
                    int(request.POST.get('section_id'))
                ])

            messages.success(request, 'Student enrolled successfully!')
            return redirect('enroll_student')
        except Exception as e:
            messages.error(request, f'Enrollment failed: {str(e)}')

    students = Student.objects.filter(is_deleted=False, status__in=['Active', 'Academic Probation', 'Academic Warning'])

    sections = execute_sql("""
        SELECT s.SectionID, s.SectionCode, s.SectionName, c.CourseCode, c.CourseName,
               s.MaxCapacity, s.CurrentEnrollment,
               (s.MaxCapacity - s.CurrentEnrollment) as AvailableSeats
        FROM Section s
        JOIN Course c ON s.CourseID = c.CourseID
        JOIN AcademicTerm t ON s.TermID = t.TermID
        WHERE t.IsCurrent = 1 AND s.Status = 'Active'
        ORDER BY AvailableSeats DESC
    """)

    context = {
        'students': students,
        'sections': sections,
    }
    return render(request, 'enroll_student.html', context)

def add_grade(request):
    """Add or update a student's grade"""
    if request.method == 'POST':
        try:
            sql = """
                UPDATE Enrollment
                SET NumericGrade = ?, Status = 'Completed'
                WHERE EnrollmentID = ?
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    float(request.POST.get('numeric_grade')),
                    int(request.POST.get('enrollment_id'))
                ])

            messages.success(request, 'Grade added successfully!')
            return redirect('add_grade')
        except Exception as e:
            messages.error(request, f'Error adding grade: {str(e)}')

    enrollments = execute_sql("""
        SELECT e.EnrollmentID, s.StudentNumber, s.FirstName || ' ' || s.LastName as StudentName,
               c.CourseCode, c.CourseName, sec.SectionCode
        FROM Enrollment e
        JOIN Student s ON e.StudentID = s.StudentID
        JOIN Section sec ON e.SectionID = sec.SectionID
        JOIN Course c ON sec.CourseID = c.CourseID
        WHERE e.Status = 'Enrolled' AND e.NumericGrade IS NULL
        ORDER BY s.StudentNumber
    """)

    context = {'enrollments': enrollments}
    return render(request, 'add_grade.html', context)

def add_fee(request):
    """Add a fee for a student"""
    if request.method == 'POST':
        try:
            sql = """
                INSERT INTO Fee (StudentID, TermID, FeeType, Amount, DueDate, Status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    int(request.POST.get('student_id')),
                    int(request.POST.get('term_id')) if request.POST.get('term_id') else None,
                    request.POST.get('fee_type'),
                    float(request.POST.get('amount')),
                    request.POST.get('due_date')
                ])

            messages.success(request, 'Fee added successfully!')
            return redirect('add_fee')
        except Exception as e:
            messages.error(request, f'Error adding fee: {str(e)}')

    students = Student.objects.filter(is_deleted=False)
    terms = AcademicTerm.objects.filter(is_active=True)

    context = {
        'students': students,
        'terms': terms,
    }
    return render(request, 'add_fee.html', context)

def add_attendance(request):
    """Mark student attendance"""
    if request.method == 'POST':
        try:
            sql = """
                INSERT INTO Attendance (StudentID, SectionID, Date, Status)
                VALUES (?, ?, DATE('now'), ?)
            """

            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    int(request.POST.get('student_id')),
                    int(request.POST.get('section_id')),
                    request.POST.get('status')
                ])

            messages.success(request, 'Attendance recorded successfully!')
            return redirect('add_attendance')
        except Exception as e:
            messages.error(request, f'Error recording attendance: {str(e)}')

    students = Student.objects.filter(is_deleted=False, status__in=['Active', 'Academic Probation'])

    sections = execute_sql("""
        SELECT s.SectionID, s.SectionCode, c.CourseCode, c.CourseName
        FROM Section s
        JOIN Course c ON s.CourseID = c.CourseID
        WHERE s.Status = 'Active'
    """)

    context = {
        'students': students,
        'sections': sections,
    }
    return render(request, 'add_attendance.html', context)

# ============= QUERY VIEWS =============

def query_results(request, query_name):
    """Execute and display predefined queries"""

    queries = {
        'top_students': "SELECT * FROM Student WHERE IsDeleted = 0 ORDER BY CumulativeGPA DESC LIMIT 20",
        'under_enrolled': "SELECT * FROM Section WHERE CurrentEnrollment < MaxCapacity * 0.5",
        'teacher_workload': "SELECT TeacherID, COUNT(*) as SectionCount FROM Section GROUP BY TeacherID",
        'course_popularity': "SELECT CourseID, COUNT(*) as EnrollmentCount FROM Section s JOIN Enrollment e ON s.SectionID = e.SectionID GROUP BY CourseID LIMIT 20",
        'waitlist_status': "SELECT * FROM Waitlist WHERE Status = 'Waiting'",
    }

    if query_name not in queries:
        return HttpResponse("Query not found", status=404)

    results = execute_sql(queries[query_name])
    columns = results[0].keys() if results else []

    context = {
        'query_name': query_name.replace('_', ' ').title(),
        'results': results,
        'columns': columns,
        'row_count': len(results),
    }
    return render(request, 'query_results.html', context)

# university_app/views.py - Enhanced custom_query with multi-statement support

# university_app/views.py - Full SQLite3 CLI Emulator

# university_app/views.py - CLEAN SQLite3 CLI Output

# university_app/views.py - CLEAN SQLite3 CLI Output (No "Query OK" clutter)

# university_app/views.py - Fixed to show SELECT results properly

# university_app/views.py - COMPLETELY FIXED

def custom_query(request):
    """Execute SQL queries exactly like SQLite3 CLI"""

    context = {
        'query_executed': False,
        'sql_query': '',
        'output_lines': [],
        'error': None,
        'sqlite_version': '3.x',
        'tables': [],
    }

    # Get SQLite version
    try:
        with connection.cursor() as cursor:
            # In the custom_query function, before executing statements, add:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("SELECT sqlite_version()")
            row = cursor.fetchone()
            if row:
                context['sqlite_version'] = row[0]
    except:
        pass

    # Get list of tables
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            context['tables'] = [row[0] for row in cursor.fetchall()]
    except:
        pass

    if request.method == 'POST':
        sql_query = request.POST.get('sql_query', '').strip()

        if not sql_query:
            messages.error(request, 'Please enter a SQL command')
            return render(request, 'custom_query.html', context)

        context['sql_query'] = sql_query
        context['output_lines'] = []

        try:
            with connection.cursor() as cursor:

                # Handle dot commands
                if sql_query.strip().startswith('.'):
                    cmd = sql_query.strip().lower()

                    if cmd == '.tables':
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                        tables = cursor.fetchall()
                        if tables:
                            table_names = [t[0] for t in tables]
                            lines = []
                            for i in range(0, len(table_names), 5):
                                row_tables = table_names[i:i+5]
                                lines.append('  '.join(f"{t:<18}" for t in row_tables))
                            for line in lines:
                                context['output_lines'].append({
                                    'type': 'output',
                                    'content': line
                                })
                        else:
                            context['output_lines'].append({
                                'type': 'output',
                                'content': ''
                            })

                    elif cmd.startswith('.schema'):
                        table_name = sql_query.strip()[8:].strip() if len(sql_query.strip()) > 8 else None
                        if table_name:
                            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                        else:
                            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
                        schemas = cursor.fetchall()
                        for schema in schemas:
                            if schema[0]:
                                context['output_lines'].append({
                                    'type': 'output',
                                    'content': schema[0] + ';'
                                })

                    elif cmd == '.databases':
                        context['output_lines'].append({
                            'type': 'output',
                            'content': f"main: {connection.settings_dict['NAME']}"
                        })

                    elif cmd == '.help':
                        help_lines = [
                            '.tables                  List names of tables',
                            '.schema ?TABLE?          Show the CREATE statements',
                            '.databases               List attached databases',
                            '.quit                    Exit',
                            '.help                    Show this message'
                        ]
                        for line in help_lines:
                            context['output_lines'].append({
                                'type': 'output',
                                'content': line
                            })

                    else:
                        context['output_lines'].append({
                            'type': 'error',
                            'content': f'Error: unknown command: {sql_query}'
                        })

                else:
                    # Split statements by semicolon (respecting quotes)
                    statements = []
                    current = []
                    in_string = False
                    quote_char = None

                    for c in sql_query:  # Fixed: was 'chr' instead of 'c'
                        if c in ['"', "'"] and not in_string:
                            in_string = True
                            quote_char = c
                            current.append(c)
                        elif c == quote_char and in_string:
                            in_string = False
                            quote_char = None
                            current.append(c)
                        elif c == ';' and not in_string:
                            stmt = ''.join(current).strip()
                            if stmt:
                                statements.append(stmt)
                            current = []
                        else:
                            current.append(c)

                    if current:
                        stmt = ''.join(current).strip()
                        if stmt:
                            statements.append(stmt)

                    # Execute each statement
                    for stmt in statements:
                        if not stmt.strip():
                            continue

                        try:
                            cursor.execute(stmt)

                            # Check if this statement returns results
                            if cursor.description:
                                rows = cursor.fetchall()
                                columns = [desc[0] for desc in cursor.description]

                                if rows:
                                    # Calculate column widths
                                    col_widths = []
                                    for i, col in enumerate(columns):
                                        max_width = len(col)
                                        for row in rows:
                                            val = str(row[i]) if row[i] is not None else 'NULL'
                                            max_width = max(max_width, len(val))
                                        col_widths.append(max_width)

                                    # Header separator
                                    header_sep = '+' + '+'.join(['-' * (w + 2) for w in col_widths]) + '+'

                                    # Header row
                                    header_row = '|'
                                    for i, col in enumerate(columns):
                                        display_col = col[:col_widths[i]] if len(col) > col_widths[i] else col
                                        header_row += f' {display_col:<{col_widths[i]}} |'

                                    context['output_lines'].append({
                                        'type': 'separator',
                                        'content': header_sep
                                    })
                                    context['output_lines'].append({
                                        'type': 'header',
                                        'content': header_row
                                    })
                                    context['output_lines'].append({
                                        'type': 'separator',
                                        'content': header_sep
                                    })

                                    # Data rows
                                    for row in rows:
                                        data_row = '|'
                                        for i, val in enumerate(row):
                                            display_val = str(val) if val is not None else 'NULL'
                                            if len(display_val) > col_widths[i]:
                                                display_val = display_val[:col_widths[i]-3] + '...'
                                            data_row += f' {display_val:<{col_widths[i]}} |'
                                        context['output_lines'].append({
                                            'type': 'row',
                                            'content': data_row
                                        })

                                    # Footer separator
                                    context['output_lines'].append({
                                        'type': 'separator',
                                        'content': header_sep
                                    })

                                    # Row count
                                    row_word = 'row' if len(rows) == 1 else 'rows'
                                    context['output_lines'].append({
                                        'type': 'output',
                                        'content': f'{len(rows)} {row_word} in set'
                                    })
                                else:
                                    context['output_lines'].append({
                                        'type': 'output',
                                        'content': 'Query returned no results'
                                    })
                            # else: Non-SELECT queries (INSERT, UPDATE, DELETE, etc.) - show nothing

                        except Exception as stmt_error:
                            error_msg = str(stmt_error)
                            context['output_lines'].append({
                                'type': 'error',
                                'content': f'Error: {error_msg}'
                            })
                            # Stop on error
                            break

                    connection.commit()

        except Exception as e:
            connection.rollback()
            context['output_lines'].append({
                'type': 'error',
                'content': f'Error: {str(e)}'
            })

        context['query_executed'] = True

    return render(request, 'custom_query.html', context)
# ============= TRIGGER VERIFICATION VIEWS =============

def verify_triggers(request):
    """Verify trigger functionality"""
    context = {
        'trigger_tests': [],
        'recent_trigger_logs': [],
    }
    return render(request, 'verify_triggers.html', context)

def test_waitlist_scenario(request):
    """Test waitlist functionality"""
    return render(request, 'test_waitlist_scenario.html')

def test_prerequisite_scenario(request):
    """Test prerequisite enforcement"""
    return render(request, 'test_prerequisite_scenario.html')

# ============= REPORTING VIEWS =============

def reports(request):
    """Reports dashboard"""
    views_list = [
        {'name': 'Top Students by GPA', 'query': 'top_students', 'description': 'Highest performing students'},
        {'name': 'Under Enrolled Sections', 'query': 'under_enrolled', 'description': 'Sections with low enrollment'},
        {'name': 'Teacher Workload', 'query': 'teacher_workload', 'description': 'Teacher workload analysis'},
        {'name': 'Course Popularity', 'query': 'course_popularity', 'description': 'Most popular courses'},
        {'name': 'Waitlist Status', 'query': 'waitlist_status', 'description': 'Current waitlist information'},
    ]
    context = {'views': views_list}
    return render(request, 'reports.html', context)

def audit_logs(request):
    """View audit logs"""
    logs = execute_sql("""
        SELECT LogID, TableName, RecordID, Action, TriggerName, ChangedBy, ChangedAt
        FROM AuditLog
        ORDER BY ChangedAt DESC
        LIMIT 100
    """)

    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    context = {
        'logs': page_obj,
        'total_count': len(logs),
    }
    return render(request, 'audit_logs.html', context)

def system_settings_view(request):
    """View system settings"""
    settings = execute_sql("""
        SELECT SettingKey, SettingValue, Description, Category
        FROM SystemSettings
        ORDER BY Category, SettingKey
    """)

    categorized = {}
    for setting in settings:
        cat = setting.get('Category', 'General')
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(setting)

    context = {'categorized_settings': categorized}
    return render(request, 'system_settings.html', context)

def sql_console(request):
    """SQL Console - Redirect to custom query"""
    return redirect('custom_query')

def example(request):
    return render(request,'example.html')
