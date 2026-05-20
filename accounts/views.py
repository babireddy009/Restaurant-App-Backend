from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserProfileSerializer, SendOTPSerializer, VerifyOTPSerializer
from .models import OTPVerification
from django.core.mail import send_mail
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
import jwt # for dev fallback decoding

User = get_user_model()


class SendOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']

        # Clear old Unverified OTPs for this identifier
        OTPVerification.objects.filter(identifier=identifier, is_verified=False).delete()

        otp = OTPVerification(identifier=identifier)
        otp.save()

        # In a real app, send Email or SMS here via Twilio/SendGrid
        if "@" in identifier:
            from core.email_utils import send_mail_async
            send_mail_async(
                'Your OTP Verification Code',
                f'Welcome to MSR Rayalasema Ruchulu! Your secure OTP code is: {otp.otp_code}\n\nThis code will expire in 10 minutes.',
                [identifier],
                fail_silently=False,
            )
                
        print(f"\n==========================================")
        print(f" MOCK OTP SENT ")
        print(f" TO: {identifier}")
        print(f" OTP: {otp.otp_code}")
        print(f"==========================================\n")

        return Response({"detail": "OTP sent successfully. Check your console/email/SMS."}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']
        otp_code = serializer.validated_data['otp_code']

        otp = OTPVerification.objects.get(identifier=identifier, otp_code=otp_code)
        otp.is_verified = True
        otp.save()

        return Response({"detail": "OTP verified successfully. You can now register."}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class DriverRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.role = 'driver'
        user.save()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"detail": "Google token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Attempt to Verify the Token
        try:
            # We mock CLIENT_ID securely if in dev and not configured
            client_id = getattr(settings, 'GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
            
            # NOTE: If we are testing with 'YOUR_GOOGLE_CLIENT_ID', standard verification WILL crash.
            # For development ONLY: we decode without verification so the developer can see it working locally without needing actual Google Cloud configs instantly.
            if client_id == 'YOUR_GOOGLE_CLIENT_ID':
                print("\\n⚠️ WARNING: Bypassing Google OAuth strict verification because GOOGLE_CLIENT_ID is not set! Do NOT do this in production! ⚠️\\n")
                id_info = jwt.decode(token, options={"verify_signature": False})
            else:
                id_info = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)

            if id_info.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            email = id_info['email']
            first_name = id_info.get('given_name', '')
            last_name = id_info.get('family_name', '')

        except ValueError as e:
            return Response({"detail": f"Invalid Google token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"detail": "Could not parse Google token. Did you install PyJWT for dev mock?"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Find or Create User
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0],
            'first_name': first_name,
            'last_name': last_name,
        })

        if created:
            user.set_unusable_password()  # Because they use Google to log in
            user.save()

        # 3. Generate JWT tokens for our app
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


class TestEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        if not user.email:
            return Response({"error": "Your user account does not have an email address set."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if not settings.EMAIL_HOST_USER:
                return Response({
                    "error": "EMAIL_HOST_USER environment variable is not set on the server."
                }, status=status.HTTP_400_BAD_REQUEST)
                
            send_mail(
                'Test Email from MSR Rayalasema Ruchulu',
                f'Hello {user.username},\n\nIf you are reading this, your SMTP settings are working perfectly on the server!',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({
                "status": "success",
                "message": f"Test email sent successfully to {user.email}",
                "smtp_user": settings.EMAIL_HOST_USER
            })
        except Exception as e:
            import traceback
            return Response({
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "smtp_user": settings.EMAIL_HOST_USER
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
