# university_app/models.py - CORRECTED VERSION
from django.db import models

class Department(models.Model):
    dept_id = models.AutoField(primary_key=True, db_column='DeptID')
    dept_name = models.CharField(max_length=255, unique=True, db_column='DeptName')
    dept_code = models.CharField(max_length=50, unique=True, db_column='DeptCode')
    head_teacher_id = models.IntegerField(null=True, blank=True, db_column='HeadTeacherID')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_column='Budget')
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_column='BudgetUsed')
    location = models.CharField(max_length=255, null=True, blank=True, db_column='Location')
    max_student_capacity = models.IntegerField(default=500, db_column='MaxStudentCapacity')
    is_active = models.BooleanField(default=True, db_column='IsActive')
    is_deleted = models.BooleanField(default=False, db_column='IsDeleted')

    class Meta:
        managed = False
        db_table = 'Department'

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True, db_column='TeacherID')
    first_name = models.CharField(max_length=100, db_column='FirstName')
    last_name = models.CharField(max_length=100, db_column='LastName')
    email = models.CharField(max_length=255, unique=True, db_column='Email')
    department_id = models.IntegerField(null=True, blank=True, db_column='DepartmentID')
    status = models.CharField(max_length=50, default='Active', db_column='Status')
    average_teaching_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, db_column='AverageTeachingRating')
    is_deleted = models.BooleanField(default=False, db_column='IsDeleted')

    class Meta:
        managed = False
        db_table = 'Teacher'

class Student(models.Model):
    student_id = models.AutoField(primary_key=True, db_column='StudentID')
    student_number = models.CharField(max_length=50, unique=True, db_column='StudentNumber')
    first_name = models.CharField(max_length=100, db_column='FirstName')
    last_name = models.CharField(max_length=100, db_column='LastName')
    email = models.CharField(max_length=255, unique=True, db_column='Email')
    department_id = models.IntegerField(null=True, blank=True, db_column='DepartmentID')
    cumulative_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, db_column='CumulativeGPA')
    semester_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, db_column='SemesterGPA')
    total_credits_earned = models.IntegerField(default=0, db_column='TotalCreditsEarned')
    status = models.CharField(max_length=50, default='Active', db_column='Status')
    academic_standing = models.CharField(max_length=50, default='Good Standing', db_column='AcademicStanding')
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100, db_column='AttendancePercentage')
    has_outstanding_fees = models.BooleanField(default=False, db_column='HasOutstandingFees')
    performance_flag = models.CharField(max_length=50, default='Normal', db_column='PerformanceFlag')
    is_deleted = models.BooleanField(default=False, db_column='IsDeleted')

    class Meta:
        managed = False
        db_table = 'Student'

class Course(models.Model):
    course_id = models.AutoField(primary_key=True, db_column='CourseID')
    course_code = models.CharField(max_length=50, unique=True, db_column='CourseCode')
    course_name = models.CharField(max_length=255, db_column='CourseName')
    credits = models.IntegerField(db_column='Credits')
    department_id = models.IntegerField(db_column='DepartmentID')
    is_active = models.BooleanField(default=True, db_column='IsActive')
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_column='AverageGrade')
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_column='SuccessRate')
    is_deleted = models.BooleanField(default=False, db_column='IsDeleted')

    class Meta:
        managed = False
        db_table = 'Course'

class Section(models.Model):
    section_id = models.AutoField(primary_key=True, db_column='SectionID')
    section_code = models.CharField(max_length=50, unique=True, db_column='SectionCode')
    section_name = models.CharField(max_length=255, db_column='SectionName')
    term_id = models.IntegerField(db_column='TermID')
    course_id = models.IntegerField(db_column='CourseID')
    teacher_id = models.IntegerField(null=True, blank=True, db_column='TeacherID')
    room_id = models.IntegerField(null=True, blank=True, db_column='RoomID')
    schedule = models.CharField(max_length=100, null=True, blank=True, db_column='Schedule')
    max_capacity = models.IntegerField(default=40, db_column='MaxCapacity')
    current_enrollment = models.IntegerField(default=0, db_column='CurrentEnrollment')
    status = models.CharField(max_length=50, default='Active', db_column='Status')

    class Meta:
        managed = False
        db_table = 'Section'

class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True, db_column='EnrollmentID')
    student_id = models.IntegerField(db_column='StudentID')
    section_id = models.IntegerField(db_column='SectionID')
    status = models.CharField(max_length=50, default='Enrolled', db_column='Status')
    numeric_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, db_column='NumericGrade')
    letter_grade = models.CharField(max_length=2, null=True, blank=True, db_column='LetterGrade')
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, db_column='GradePoints')
    grade_locked = models.BooleanField(default=False, db_column='GradeLocked')

    class Meta:
        managed = False
        db_table = 'Enrollment'

class AcademicTerm(models.Model):
    term_id = models.AutoField(primary_key=True, db_column='TermID')
    semester = models.CharField(max_length=20, db_column='Semester')
    academic_year = models.CharField(max_length=20, db_column='AcademicYear')
    start_date = models.DateField(db_column='StartDate')
    end_date = models.DateField(db_column='EndDate')
    add_drop_deadline = models.DateField(db_column='AddDropDeadline')
    is_current = models.BooleanField(default=False, db_column='IsCurrent')
    is_active = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        managed = False
        db_table = 'AcademicTerm'

# Add to university_app/models.py - after the existing models

class SystemSettings(models.Model):
    setting_key = models.CharField(primary_key=True, max_length=100, db_column='SettingKey')
    setting_value = models.TextField(db_column='SettingValue')
    description = models.TextField(null=True, blank=True, db_column='Description')
    category = models.CharField(max_length=100, null=True, blank=True, db_column='Category')
    last_modified = models.DateTimeField(null=True, blank=True, db_column='LastModified')
    modified_by = models.CharField(max_length=100, default='SYSTEM', db_column='ModifiedBy')

    class Meta:
        managed = False
        db_table = 'SystemSettings'


class SystemMode(models.Model):
    mode_id = models.IntegerField(primary_key=True, db_column='ModeID')
    environment = models.CharField(max_length=50, default='PRODUCTION', db_column='Environment')
    strict_mode = models.BooleanField(default=True, db_column='StrictMode')
    allow_test_data = models.BooleanField(default=False, db_column='AllowTestData')
    debug_logging = models.BooleanField(default=False, db_column='DebugLogging')
    last_changed = models.DateTimeField(null=True, blank=True, db_column='LastChanged')

    class Meta:
        managed = False
        db_table = 'SystemMode'


class Classroom(models.Model):
    room_id = models.AutoField(primary_key=True, db_column='RoomID')
    room_number = models.CharField(max_length=50, unique=True, db_column='RoomNumber')
    building = models.CharField(max_length=100, db_column='Building')
    capacity = models.IntegerField(db_column='Capacity')
    current_occupancy = models.IntegerField(default=0, db_column='CurrentOccupancy')
    utilization_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, db_column='UtilizationRate')
    type = models.CharField(max_length=50, db_column='Type')

    class Meta:
        managed = False
        db_table = 'Classroom'


class Fee(models.Model):
    fee_id = models.AutoField(primary_key=True, db_column='FeeID')
    student_id = models.IntegerField(db_column='StudentID')
    term_id = models.IntegerField(null=True, blank=True, db_column='TermID')
    fee_type = models.CharField(max_length=50, db_column='FeeType')
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='Amount')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='PaidAmount')
    due_date = models.DateField(db_column='DueDate')
    paid_date = models.DateField(null=True, blank=True, db_column='PaidDate')
    status = models.CharField(max_length=50, default='Pending', db_column='Status')
    payment_method = models.CharField(max_length=50, null=True, blank=True, db_column='PaymentMethod')
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, db_column='LateFee')
    created_date = models.DateField(null=True, blank=True, db_column='CreatedDate')
    created_by = models.CharField(max_length=100, default='SYSTEM', db_column='CreatedBy')

    class Meta:
        managed = False
        db_table = 'Fee'


class Scholarship(models.Model):
    scholarship_id = models.AutoField(primary_key=True, db_column='ScholarshipID')
    student_id = models.IntegerField(db_column='StudentID')
    term_id = models.IntegerField(null=True, blank=True, db_column='TermID')
    scholarship_name = models.CharField(max_length=255, db_column='ScholarshipName')
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='Amount')
    start_date = models.DateField(null=True, blank=True, db_column='StartDate')
    end_date = models.DateField(null=True, blank=True, db_column='EndDate')
    award_date = models.DateField(null=True, blank=True, db_column='AwardDate')
    renewal_date = models.DateField(null=True, blank=True, db_column='RenewalDate')
    eligibility_status = models.CharField(max_length=50, default='Active', db_column='EligibilityStatus')

    class Meta:
        managed = False
        db_table = 'Scholarship'


class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key=True, db_column='AssessmentID')
    section_id = models.IntegerField(db_column='SectionID')
    assessment_type = models.CharField(max_length=50, db_column='AssessmentType')
    assessment_name = models.CharField(max_length=255, db_column='AssessmentName')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, db_column='MaxScore')
    weight = models.DecimalField(max_digits=5, decimal_places=2, db_column='Weight')
    due_date = models.DateField(null=True, blank=True, db_column='DueDate')

    class Meta:
        managed = False
        db_table = 'Assessment'


class StudentAssessment(models.Model):
    student_assessment_id = models.AutoField(primary_key=True, db_column='StudentAssessmentID')
    enrollment_id = models.IntegerField(db_column='EnrollmentID')
    assessment_id = models.IntegerField(db_column='AssessmentID')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, db_column='Score')
    date_recorded = models.DateField(null=True, blank=True, db_column='DateRecorded')

    class Meta:
        managed = False
        db_table = 'StudentAssessment'


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True, db_column='AttendanceID')
    student_id = models.IntegerField(db_column='StudentID')
    section_id = models.IntegerField(db_column='SectionID')
    date = models.DateField(db_column='Date')
    status = models.CharField(max_length=20, db_column='Status')
    remarks = models.TextField(null=True, blank=True, db_column='Remarks')

    class Meta:
        managed = False
        db_table = 'Attendance'


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True, db_column='LogID')
    table_name = models.CharField(max_length=100, db_column='TableName')
    record_id = models.IntegerField(db_column='RecordID')
    action = models.CharField(max_length=50, db_column='Action')
    old_value = models.TextField(null=True, blank=True, db_column='OldValue')
    new_value = models.TextField(null=True, blank=True, db_column='NewValue')
    trigger_name = models.CharField(max_length=100, db_column='TriggerName')
    changed_by = models.CharField(max_length=100, default='SYSTEM', db_column='ChangedBy')
    changed_at = models.DateTimeField(db_column='ChangedAt')
    ip_address = models.CharField(max_length=50, null=True, blank=True, db_column='IPAddress')
    session_id = models.CharField(max_length=100, null=True, blank=True, db_column='SessionID')
    checksum = models.CharField(max_length=255, null=True, blank=True, db_column='Checksum')

    class Meta:
        managed = False
        db_table = 'AuditLog'


class Waitlist(models.Model):
    waitlist_id = models.AutoField(primary_key=True, db_column='WaitlistID')
    student_id = models.IntegerField(db_column='StudentID')
    section_id = models.IntegerField(db_column='SectionID')
    position = models.IntegerField(db_column='Position')
    requested_at = models.DateTimeField(db_column='RequestedAt')
    notified_at = models.DateTimeField(null=True, blank=True, db_column='NotifiedAt')
    status = models.CharField(max_length=50, default='Waiting', db_column='Status')
    offered_until = models.DateTimeField(null=True, blank=True, db_column='OfferedUntil')

    class Meta:
        managed = False
        db_table = 'Waitlist'
