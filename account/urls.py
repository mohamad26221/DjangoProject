from django.urls import path

from .views import (
        RegisterUserView, 
        RegistrationRequestView,
        LoginUserView, 
        LogoutView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('register_housing/', RegistrationRequestView.as_view(), name='register_housing'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    ]