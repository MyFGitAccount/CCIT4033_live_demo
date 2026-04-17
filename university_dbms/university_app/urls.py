# university_app/urls.py - CLEAN VERSION

from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),

    # Data entry views
    path('add-student/', views.add_student, name='add_student'),
    path('add-course/', views.add_course, name='add_course'),
    path('add-section/', views.add_section, name='add_section'),
    path('enroll-student/', views.enroll_student, name='enroll_student'),
    path('add-grade/', views.add_grade, name='add_grade'),
    path('add-fee/', views.add_fee, name='add_fee'),
    path('add-attendance/', views.add_attendance, name='add_attendance'),

    # Query views
    path('query/<str:query_name>/', views.query_results, name='query_results'),
    path('custom-query/', views.custom_query, name='custom_query'),

    # Trigger verification views
    path('verify-triggers/', views.verify_triggers, name='verify_triggers'),
    path('test-waitlist/', views.test_waitlist_scenario, name='test_waitlist_scenario'),
    path('test-prerequisite/', views.test_prerequisite_scenario, name='test_prerequisite_scenario'),

    # Report views
    path('reports/', views.reports, name='reports'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('system-settings/', views.system_settings_view, name='system_settings'),
    path('example/',views.example,name='example')
]
