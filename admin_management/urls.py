from django.urls import path
from . import views

urlpatterns = [
    path('volunteers/', views.VolunteerListView.as_view(), name='volunteer-list'),
    path('volunteers/create/', views.CreateVolunteerView.as_view(), name='create-volunteer'),
    path('volunteers/<uuid:volunteer_id>/delete/', views.DeleteVolunteerView.as_view(), name='delete-volunteer'),
    path('campus/', views.CampusManagementView.as_view(), name='create-campus'),
    path('campus/<uuid:campus_id>/', views.CampusManagementView.as_view(), name='update-delete-campus'),
]
