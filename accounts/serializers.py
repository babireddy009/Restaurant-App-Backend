from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from django.utils import timezone
from .models import OTPVerification

User = get_user_model()

class SendOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=150)

    def validate_identifier(self, value):
        val = value.strip()
        if "@" in val:
            val = val.lower()
            if User.objects.filter(email__iexact=val).exists():
                raise serializers.ValidationError("An account with this email already exists.")
        else:
            if User.objects.filter(phone__exact=val).exists():
                raise serializers.ValidationError("An account with this phone number already exists.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=150)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        otp_code = attrs.get('otp_code')
        
        try:
            otp_obj = OTPVerification.objects.get(identifier=identifier, otp_code=otp_code)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "Invalid OTP code."})
            
        if not otp_obj.is_valid():
            raise serializers.ValidationError({"otp_code": "OTP has expired or already been used."})
            
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
            
        email = attrs.get('email')
        if email:
            email = email.strip().lower()
            attrs['email'] = email
            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError({"email": "This email is already registered."})

        phone = attrs.get('phone')
        if phone:
            phone = phone.strip()
            attrs['phone'] = phone
            if User.objects.filter(phone__exact=phone).exists():
                raise serializers.ValidationError({"phone": "This phone number is already registered."})

        # Ensure either email or phone is provided and has a verified OTP
        identifier = email or phone
        if not identifier:
            raise serializers.ValidationError({"identifier": "Email or phone is required."})
            
        try:
            # Check for the most recent verified OTP
            otp = OTPVerification.objects.filter(
                identifier=identifier, 
                is_verified=True
            ).latest('created_at')
            if (timezone.now() - otp.expires_at).total_seconds() > 3600: # OTP verification expires after 1hr
                raise serializers.ValidationError({"identifier": "OTP verification expired. Please verify again."})
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({"identifier": "Identifier has not been verified."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        if 'email' in validated_data and validated_data['email']:
            validated_data['email'] = validated_data['email'].strip().lower()
        user = User.objects.create_user(**validated_data)
        
        # Cleanup the used OTP
        identifier = validated_data.get('email') or validated_data.get('phone')
        OTPVerification.objects.filter(identifier=identifier).delete()
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role', 'profile_image', 'created_at')
        read_only_fields = ('id', 'username', 'role', 'created_at')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone')
