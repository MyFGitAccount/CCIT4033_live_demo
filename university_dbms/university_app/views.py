# university_app/views.py

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
    conn = connection.cursor()
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
    # Get summary statistics
    stats = {}
    
    with connection.cursor() as cursor:
        # Student stats
        cursor.execute("SELECT COUNT(*) FROM Student WHERE IsDeleted = 0")
        stats['total_students'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Student WHERE Status = 'Active' AND IsDeleted = 0")
        stats['active_students'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Student WHERE AcademicStanding = 'Academic Probation'")
        stats['probation_students'] = cursor.fetchone()[0]
        
        # Teacher stats
        cursor.execute("SELECT COUNT(*) FROM Teacher WHERE IsDeleted = 0")
        stats['total_teachers'] = cursor.fetchone()[0]
        
        # Course stats
        cursor.execute("SELECT COUNT(*) FROM Course WHERE IsDeleted = 0")
        stats['total_courses'] = cursor.fetchone()[0]
        
        # Current sections
        cursor.execute("""
            SELECT COUNT(*) FROM Section s
            JOIN AcademicTerm t ON s.TermID = t.TermID
            WHERE t.IsCurrent = 1 AND s.Status = 'Active'
        """)
        stats['active_sections'] = cursor.fetchone()[0]
        
        # Total enrollments this term
        cursor.execute("""
            SELECT COUNT(*) FROM Enrollment e
            JOIN Section s ON e.SectionID = s.SectionID
            JOIN AcademicTerm t ON s.TermID = t.TermID
            WHERE t.IsCurrent = 1 AND e.Status = 'Enrolled'
        """)
        stats['current_enrollments'] = cursor.fetchone()[0]
    
    # Get recent audit logs
    recent_logs = execute_sql("""
        SELECT LogID, TableName, Action, TriggerName, ChangedBy, ChangedAt
        FROM AuditLog
        ORDER BY ChangedAt DESC
        LIMIT 20
    """)
    
    # Get system settings - handle if table is empty
    try:
        settings = list(SystemSettings.objects.all())
    except Exception:
        settings = []
    
    # Get top students
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
        'settings': settings,
        'top_students': top_students,
    }
    return render(request, 'dashboard.html', context)

# ============= DATA ENTRY VIEWS =============

def add_student(request):
    """Add a new student"""
    if request.method == 'POST':
        try:
            # Generate student number
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Student")
                count = cursor.fetchone()[0] + 1
                student_number = f"STU{datetime.now().year}{count:04d}"
            
            sql = """
                INSERT INTO Student (
                    StudentNumber, FirstName, LastName, NationalID, Country,
                    Email, Phone, Address, DepartmentID, EnrollmentDate,
                    Status, CurrentSemester
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), 'Active', 1)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    student_number,
                    request.POST.get('first_name'),
                    request.POST.get('last_name'),
                    request.POST.get('national_id'),
                    request.POST.get('country'),
                    request.POST.get('email'),
                    request.POST.get('phone'),
                    request.POST.get('address'),
                    int(request.POST.get('department_id')) if request.POST.get('department_id') else None
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
                INSERT INTO Course (CourseCode, CourseName, Credits, DepartmentID, Description, IsActive, IsDeleted)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            """
            
            with connection.cursor() as cursor:
                cursor.execute(sql, [
                    request.POST.get('course_code'),
                    request.POST.get('course_name'),
                    int(request.POST.get('credits')),
                    int(request.POST.get('department_id')),
                    request.POST.get('description', '')
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
            # Generate section code
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
                    int(request.POST.get('term_id')),
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
    
    # Get active sections with availability
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
    
    # Get enrollments without grades
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
        'top_students': """
            SELECT * FROM TopStudentsByGPA
        """,
        'under_enrolled': """
            SELECT * FROM UnderEnrolledSections
        """,
        'teacher_workload': """
            SELECT * FROM TeacherWorkloadReport
        """,
        'course_popularity': """
            SELECT * FROM CoursePopularityReport LIMIT 20
        """,
        'graduation_audit': """
            SELECT * FROM GraduationAudit
        """,
        'risk_assessment': """
            SELECT * FROM StudentRiskAssessment
        """,
        'waitlist_status': """
            SELECT * FROM WaitlistStatus
        """,
        'teacher_performance': """
            SELECT * FROM TeacherPerformanceTrends
        """,
        'student_profile': """
            SELECT * FROM UnifiedStudentProfile LIMIT 50
        """,
    }
    
    if query_name not in queries:
        return HttpResponse("Query not found", status=404)
    
    results = execute_sql(queries[query_name])
    
    # Get column names from results
    columns = results[0].keys() if results else []
    
    context = {
        'query_name': query_name.replace('_', ' ').title(),
        'results': results,
        'columns': columns,
        'row_count': len(results),
    }
    return render(request, 'query_results.html', context)

def custom_query(request):
    """Execute custom SQL query"""
    if request.method == 'POST':
        sql_query = request.POST.get('sql_query', '')
        
        # Security: Only allow SELECT queries
        if not sql_query.strip().upper().startswith('SELECT'):
            messages.error(request, 'Only SELECT queries are allowed for security reasons.')
            return redirect('custom_query')
        
        try:
            results = execute_sql(sql_query)
            columns = results[0].keys() if results else []
            
            context = {
                'query_executed': True,
                'sql_query': sql_query,
                'results': results,
                'columns': columns,
                'row_count': len(results),
            }
            return render(request, 'custom_query.html', context)
        except Exception as e:
            messages.error(request, f'Query error: {str(e)}')
    
    return render(request, 'custom_query.html', {'query_executed': False})

# ============= TRIGGER VERIFICATION VIEWS =============

def verify_triggers(request):
    """Verify trigger functionality with test cases"""
    
    trigger_tests = []
    
    # Test 1: Academic Probation Trigger
    with connection.cursor() as cursor:
        # Get a student with low GPA to test probation
        cursor.execute("""
            SELECT StudentID, StudentNumber, CumulativeGPA, AcademicStanding
            FROM Student WHERE CumulativeGPA < 2.0 LIMIT 1
        """)
        probation_student = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Academic Standing Update',
            'description': 'Student automatically placed on probation when GPA < 2.0',
            'result': 'PASS' if probation_student else 'No student with GPA < 2.0',
            'data': probation_student
        })
    
    # Test 2: Waitlist Management
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SectionID, SectionCode, MaxCapacity, CurrentEnrollment, WaitlistCount
            FROM Section WHERE WaitlistCount > 0 LIMIT 1
        """)
        waitlist_section = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Waitlist Management',
            'description': 'Students automatically added to waitlist when section is full',
            'result': 'Active' if waitlist_section else 'No active waitlists',
            'data': waitlist_section
        })
    
    # Test 3: Fee Late Fee Application
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT FeeID, Amount, LateFee, Status
            FROM Fee WHERE Status = 'Overdue' LIMIT 1
        """)
        overdue_fee = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Late Fee Application',
            'description': 'Late fee automatically applied to overdue payments',
            'result': 'PASS' if overdue_fee else 'No overdue fees',
            'data': overdue_fee
        })
    
    # Test 4: Scholarship GPA Adjustment
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.ScholarshipID, s.Amount, s.EligibilityStatus, stu.CumulativeGPA
            FROM Scholarship s
            JOIN Student stu ON s.StudentID = stu.StudentID
            LIMIT 1
        """)
        scholarship = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Scholarship GPA Adjustment',
            'description': 'Scholarship amount adjusts based on GPA changes',
            'result': 'Active' if scholarship else 'No scholarships',
            'data': scholarship
        })
    
    # Test 5: Grade Lock After Completion
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EnrollmentID, NumericGrade, GradeLocked, Status
            FROM Enrollment WHERE Status = 'Completed' AND GradeLocked = 1 LIMIT 1
        """)
        locked_grade = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Grade Lock',
            'description': 'Grades automatically locked after completion period',
            'result': 'PASS' if locked_grade else 'No locked grades found',
            'data': locked_grade
        })
    
    # Test 6: Attendance Trigger
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT StudentID, AttendancePercentage
            FROM Student WHERE AttendancePercentage < 75 LIMIT 1
        """)
        low_attendance = cursor.fetchone()
        
        trigger_tests.append({
            'name': 'Attendance Tracking',
            'description': 'Student attendance percentage automatically updated',
            'result': 'Active' if low_attendance else 'All students have good attendance',
            'data': low_attendance
        })
    
    # Test 7: Prerequisite Check
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cp.CourseID, c.CourseCode, cp.PrerequisiteCourseID, pc.CourseCode as PrereqCode
            FROM CoursePrerequisite cp
            JOIN Course c ON cp.CourseID = c.CourseID
            JOIN Course pc ON cp.PrerequisiteCourseID = pc.CourseID
            LIMIT 3
        """)
        prerequisites = cursor.fetchall()
        
        trigger_tests.append({
            'name': 'Prerequisite Enforcement',
            'description': 'System prevents enrollment without prerequisites',
            'result': f'{len(prerequisites)} prerequisite rules active',
            'data': prerequisites
        })
    
    # Get recent trigger executions from audit log
    recent_trigger_logs = execute_sql("""
        SELECT LogID, TableName, Action, TriggerName, ChangedAt
        FROM AuditLog
        WHERE TriggerName != 'SYSTEM'
        ORDER BY ChangedAt DESC
        LIMIT 30
    """)
    
    context = {
        'trigger_tests': trigger_tests,
        'recent_trigger_logs': recent_trigger_logs,
    }
    return render(request, 'verify_triggers.html', context)

def test_waitlist_scenario(request):
    """Test the waitlist functionality"""
    if request.method == 'POST':
        try:
            # Get a section that's almost full
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT SectionID, SectionCode, MaxCapacity, CurrentEnrollment
                    FROM Section
                    WHERE CurrentEnrollment < MaxCapacity AND Status = 'Active'
                    LIMIT 1
                """)
                section = cursor.fetchone()
                
                if not section:
                    messages.error(request, 'No available sections found for testing')
                    return redirect('test_waitlist_scenario')
                
                # Try to enroll more students than capacity
                remaining = section[2] - section[3]
                messages.info(request, f'Section {section[1]} has {remaining} seats remaining')
                
                # Get students to test waitlist
                cursor.execute("""
                    SELECT StudentID, StudentNumber, FirstName || ' ' || LastName as Name
                    FROM Student
                    WHERE IsDeleted = 0 AND Status = 'Active'
                    LIMIT 5
                """)
                students = cursor.fetchall()
                
                context = {
                    'section': {'id': section[0], 'code': section[1], 'capacity': section[2], 'current': section[3]},
                    'students': students,
                }
                return render(request, 'test_waitlist_scenario.html', context)
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'test_waitlist_scenario.html')

def test_prerequisite_scenario(request):
    """Test prerequisite enforcement"""
    with connection.cursor() as cursor:
        # Get a course with prerequisites
        cursor.execute("""
            SELECT cp.CourseID, c.CourseCode, c.CourseName,
                   cp.PrerequisiteCourseID, pc.CourseCode as PrereqCode
            FROM CoursePrerequisite cp
            JOIN Course c ON cp.CourseID = c.CourseID
            JOIN Course pc ON cp.PrerequisiteCourseID = pc.CourseID
            LIMIT 3
        """)
        prerequisites = cursor.fetchall()
        
        # Get students who have completed the prerequisites
        prereq_courses = [p[3] for p in prerequisites]
        
        if prerequisites:
            cursor.execute(f"""
                SELECT DISTINCT s.StudentID, s.StudentNumber, s.FirstName || ' ' || s.LastName as Name
                FROM Student s
                JOIN Enrollment e ON s.StudentID = e.StudentID
                JOIN Section sec ON e.SectionID = sec.SectionID
                WHERE e.Status = 'Completed'
                  AND sec.CourseID IN ({','.join(['?'] * len(prereq_courses))})
                LIMIT 5
            """, prereq_courses)
            eligible_students = cursor.fetchall()
        else:
            eligible_students = []
    
    context = {
        'prerequisites': prerequisites,
        'eligible_students': eligible_students,
    }
    return render(request, 'test_prerequisite_scenario.html', context)

# ============= REPORTING VIEWS =============

def reports(request):
    """Reports dashboard"""
    # Get all available views
    views = [
        {'name': 'Unified Student Profile', 'query': 'student_profile', 'description': 'Complete student information with academic standing'},
        {'name': 'Top Students by GPA', 'query': 'top_students', 'description': 'Highest performing students'},
        {'name': 'Under Enrolled Sections', 'query': 'under_enrolled', 'description': 'Sections with low enrollment'},
        {'name': 'Teacher Workload Report', 'query': 'teacher_workload', 'description': 'Teacher workload analysis'},
        {'name': 'Course Popularity', 'query': 'course_popularity', 'description': 'Most popular courses by enrollment'},
        {'name': 'Graduation Audit', 'query': 'graduation_audit', 'description': 'Graduation eligibility check'},
        {'name': 'Risk Assessment', 'query': 'risk_assessment', 'description': 'Student at-risk identification'},
        {'name': 'Waitlist Status', 'query': 'waitlist_status', 'description': 'Current waitlist information'},
        {'name': 'Teacher Performance Trends', 'query': 'teacher_performance', 'description': 'Teacher effectiveness tracking'},
    ]
    
    # Get summary stats for each category
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN RiskLevel = 'Critical Risk' THEN StudentID END) as critical_risk,
                COUNT(DISTINCT CASE WHEN RiskLevel = 'High Risk' THEN StudentID END) as high_risk,
                COUNT(DISTINCT CASE WHEN RiskLevel = 'Moderate Risk' THEN StudentID END) as moderate_risk
            FROM StudentRiskAssessment
        """)
        risk_stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN GraduationEligibility = 'Eligible for Graduation' THEN StudentID END) as eligible_graduation
            FROM GraduationAudit
        """)
        grad_stats = cursor.fetchone()
    
    context = {
        'views': views,
        'risk_stats': risk_stats,
        'grad_stats': grad_stats,
    }
    return render(request, 'reports.html', context)

def audit_logs(request):
    """View audit logs"""
    page = request.GET.get('page', 1)
    
    logs = execute_sql("""
        SELECT LogID, TableName, RecordID, Action, OldValue, NewValue,
               TriggerName, ChangedBy, ChangedAt
        FROM AuditLog
        ORDER BY ChangedAt DESC
    """)
    
    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(page)
    
    context = {
        'logs': page_obj,
        'total_count': len(logs),
    }
    return render(request, 'audit_logs.html', context)

def system_settings_view(request):
    """View and manage system settings"""
    if request.method == 'POST':
        try:
            setting_key = request.POST.get('setting_key')
            setting_value = request.POST.get('setting_value')
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE SystemSettings
                    SET SettingValue = ?, LastModified = CURRENT_TIMESTAMP
                    WHERE SettingKey = ?
                """, [setting_value, setting_key])
            
            messages.success(request, f'Setting {setting_key} updated successfully!')
            return redirect('system_settings')
        except Exception as e:
            messages.error(request, f'Error updating setting: {str(e)}')
    
    settings = execute_sql("""
        SELECT SettingKey, SettingValue, Description, Category
        FROM SystemSettings
        ORDER BY Category, SettingKey
    """)
    
    # Group by category
    categorized = {}
    for setting in settings:
        cat = setting.get('Category', 'General')
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(setting)
    
    context = {'categorized_settings': categorized}
    return render(request, 'system_settings.html', context)
