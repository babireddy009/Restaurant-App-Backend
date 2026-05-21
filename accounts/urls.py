from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, DriverRegisterView, UserProfileView, LogoutView, SendOTPView, VerifyOTPView, GoogleLoginView, TestEmailView, RunDiagnosticsView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='auth-send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='auth-verify-otp'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('driver/register/', DriverRegisterView.as_view(), name='auth-driver-register'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('google/', GoogleLoginView.as_view(), name='auth-google'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/', UserProfileView.as_view(), name='auth-profile'),
    path('test-email/', TestEmailView.as_view(), name='auth-test-email'),
    path('run-diagnostics/', RunDiagnosticsView.as_view(), name='auth-run-diagnostics'),
]
