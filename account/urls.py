from django.urls import path
from .admin import admin_site
from .views import (
        RegisterUserView, 
        RegistrationRequestView,
        EmailVerificationAPIView,
        LoginUserView, 
        change_language,
        LogoutView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('register_housing/', RegistrationRequestView.as_view(), name='register_housing'),
    path('verify_email/', EmailVerificationAPIView.as_view(), name='verify_email'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('change-language/', change_language, name='change_language'),
    path('logout/', LogoutView.as_view(), name='logout'),
   
    ]
