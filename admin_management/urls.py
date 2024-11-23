from django.urls import path
from . import views

urlpatterns = [
    path('volunteers/', views.VolunteerListView.as_view(), name='volunteer-list'),
    path('volunteers/create/', views.CreateVolunteerView.as_view(), name='create-volunteer'),
    path('volunteers/<uuid:volunteer_id>/delete/', views.DeleteVolunteerView.as_view(), name='delete-volunteer'),
    path('campus/', views.CampusManagementView.as_view(), name='create-campus'),
    path('campus/<uuid:campus_id>/', views.CampusManagementView.as_view(), name='update-delete-campus'),
    path('grade/', views.GradeManagementView.as_view(), name='create-grade'),
    path('grade/<uuid:grade_id>/', views.GradeManagementView.as_view(), name='update-delete-grade'),
    path('subject/', views.SubjectManagementView.as_view(), name='create-subject'),
    path('subject/<uuid:subject_id>/', views.SubjectManagementView.as_view(), name='update-delete-subject'),
    path('proficiency/', views.ProficiencyManagementView.as_view(), name='create-proficiency'),
    path('proficiency/<uuid:proficiency_id>/', views.ProficiencyManagementView.as_view(), name='update-delete-proficiency'),
    path('lesson/', views.LessonManagementView.as_view(), name='create-lesson'),
    path('lesson/<uuid:lesson_id>/', views.LessonManagementView.as_view(), name='update-delete-lesson'),
]
