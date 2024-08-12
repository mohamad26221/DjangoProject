from django.urls import path
from .views import (
        RegisterUserView, 
        RegistrationRequestView,
        EmailVerificationAPIView,
        LoginUserView, 
        CustomUserDetailView,
        UpdateFCMTokenView,
        RegistrationRequestUpdateView,
        change_language,
        LogoutView)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('register_housing/', RegistrationRequestView.as_view(), name='register_housing'),
    path('register_housing_update/', RegistrationRequestUpdateView.as_view(), name='registration-update'),
    path('verify_email/', EmailVerificationAPIView.as_view(), name='verify_email'),
    path('update_fcm_token/', UpdateFCMTokenView.as_view(), name='update_fcm_token'),
    path('student/', CustomUserDetailView.as_view(), name='student-detail'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('change-language/', change_language, name='change_language'),
    path('logout/', LogoutView.as_view(), name='logout'),
   
    ]
