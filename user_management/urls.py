from django.urls import path
from user_management import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", views.TokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path('update-push-token/', views.UpdatePushTokenView.as_view(), name='update-push-token'),
]