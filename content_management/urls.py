from django.urls import path
from . import views

urlpatterns = [
    path('campuses/', views.CampusListView.as_view(), name='campus-list'),
    path('campuses/<uuid:campus_id>/', views.CampusDetailView.as_view(), name='campus-detail'),
    path('grades/<uuid:grade_id>/', views.GradeDetailView.as_view(), name='grade-detail'),
    path('subjects/<uuid:subject_id>/', views.SubjectDetailView.as_view(), name='subject-detail'),
    path('proficiencies/<uuid:proficiency_id>/lessons/', views.ProficiencyLessonsView.as_view(), name='proficiency-lessons'),
    path('lessons/<uuid:lesson_id>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<uuid:lesson_id>/mark-done/', views.MarkLessonDoneView.as_view(), name='mark-lesson-done'),
    path('lessons/<uuid:lesson_id>/mark-not-done/', views.MarkLessonNotDoneView.as_view(), name='mark-lesson-not-done'),
    path('parse/', views.ParseCSVView.as_view(), name='test'),
    path('sheets/', views.GetAllSheetsView.as_view(), name='get-all-sheets'),
    path('sheets/parse/', views.ParseCSVView.as_view(), name='parse-csv'),
    path('delete-li-content/', views.DeleteLIContentView.as_view(), name='delete-li-content'),
]
