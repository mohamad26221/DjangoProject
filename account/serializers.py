
import json
from dataclasses import field
from django.core.validators import validate_email
from .models import Customuser ,Student
from rest_framework import serializers
from django.contrib.auth.models import User
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError

class CustomAuthenticationFailed(APIException):
    status_code = 200
    default_detail = 'Invalid credentials.'
    default_code = 'authentication_failed'
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, CustomAuthenticationFailed):
        custom_response_data = {
            'error': str(exc.detail),
        }

        return Response(custom_response_data, status=status.HTTP_200_OK)

    return response

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=Customuser
        fields = ['email', 'first_name', 'last_name','phone','password', 'password2']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        user= Customuser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone=validated_data.get('phone'),
            password=validated_data.get('password')
            )
        return user
class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = Student
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2','unitNumber','room','university']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    def validate_email(self, value):
        if Customuser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone(self, value):
        if Customuser.objects.filter(phone=value).exists() or Student.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')  
        password = validated_data.pop('password')
        user = Customuser.objects.create_user(password=password, **validated_data)
    
        student = Student.objects.create(user=user, **validated_data)
    
        return student

class LoginSerializer(serializers.Serializer): 
    email = serializers.EmailField(
        max_length=155,
        required=True,
        allow_blank=False,
        error_messages={
            'invalid': 'البريد غير صالح'
        }
    )
    password = serializers.CharField(
        max_length=68,
        write_only=True,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'كلمة المرور مطلوبة',
        }
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError({'email': 'البريد غير صالح'})

        if email is None or password is None:
            raise serializers.ValidationError({'email': 'البريد الإلكتروني مطلوب', 'password': 'كلمة المرور مطلوبة'})

        email = email.strip() if email else None
        password = password.strip() if password else None

        if not email or not password:
            raise serializers.ValidationError({'email': 'البريد الإلكتروني مطلوب', 'password': 'كلمة المرور مطلوبة'})

        request = self.context.get('request')
        
        user = authenticate(request, email=email, password=password)

        if not user:
            raise serializers.ValidationError({'email': 'كلمة المرور أو البريد الإلكتروني غير صحيحين'})

        if not user.is_verified:
            raise serializers.ValidationError({'email': 'البريد الإلكتروني غير مفعل.'})

        self.context['user'] = user
        return attrs

    def to_representation(self, instance):
        user = self.context['user']
        tokens = user.tokens()
        return {
            'full_name': user.get_full_name,
            'fathername': user.fathername,
            'mothername': user.mothername,
            'phone': user.phone,
            'idNumber': user.idNumber,
            'idNationalNumber': user.idNationalNumber,
            'university': user.university.name if user.university else None,
            'faculty': user.faculty,
            'section': user.section,
            'unitNumber': user.unitNumber.number if user.unitNumber else None,
            'room': user.room.number if user.room else None,
            'city': user.city,
            'year': user.year,
            'status': user.status,
            'job': user.job,
            'typejob': user.typejob,
            'img': user.img,
            'access_token': str(tokens.get('access')),
            # 'refresh_token': str(tokens.get('refresh'))  # Uncomment if you need the refresh token
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        
        email = attrs.get('email')
        if Customuser.objects.filter(email=email).exists():
            user= Customuser.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            current_site=get_current_site(request).domain
            relative_link =reverse('reset-password-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{current_site}{relative_link}"
            print(abslink)
            email_body=f"Hi {user.first_name} use the link below to reset your password {abslink}"
            data={
                'email_body':email_body, 
                'email_subject':"Reset your Password", 
                'to_email':user.email
                }
            send_normal_email(data)

        return super().validate(attrs)  
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(min_length=1, write_only=True)
    token=serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=Customuser.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

    

    
    

