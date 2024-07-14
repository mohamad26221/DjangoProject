from django.core.validators import validate_email
from .models import Customuser ,Student,Staff,RegistrationRequest
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.views import exception_handler
from rest_framework import status
from django.utils import timezone
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
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    class Meta:
        model = Customuser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2','year', 'job', 'unitNumber', 'room','idNationalNumber', 'university', 'faculty', 'section']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("كلمة المرور غير متطابقة")

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 
        job = validated_data.pop('job')
        password = validated_data.pop('password')

        user = Customuser.objects.create_user(**validated_data, password=password, job=job)

        return user
class RegistrationRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)


    class Meta:
        model = RegistrationRequest
        fields = [ 'email', 'university', 'unitNumber', 'room', 'attachments', 'payment_method']
        extra_kwargs = {
            'attachments': {'required': False},
            'status': {'write_only': True},
            'idNationalNumber': {'write_only': True}
        }
    def validate_email(self, value):
        if RegistrationRequest.objects.filter(student__email=value).exists():
            raise serializers.ValidationError("البريد الالكتروني مستخدم من قبل في التسجيل")
        return value

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            raise serializers.ValidationError("البريد الالكتروني هذا غير موجود تاكد من صحة الادخال")
        if RegistrationRequest.objects.filter(student=student).exists():
            raise serializers.ValidationError("تم تسجيل هذا الطالب بالفعل")
        
        
        registration_request = RegistrationRequest.objects.create(
            student=student,
            university=validated_data.get('university'),
            unitNumber=validated_data.get('unitNumber'),
            idNationalNumber=validated_data.get('idNationalNumber'),
            room=validated_data.get('room'),
            attachments=validated_data.get('attachments'),
            payment_method=validated_data.get('payment_method'),
            status='في انتظار الموافقة'  ,
        )
        
        return registration_request
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
                raise serializers.ValidationError({'message': 'البريد غير صالح'})

        if email is None or password is None:
            raise serializers.ValidationError({'message': 'البريد الإلكتروني مطلوب وكلمة المرور مطلوبة'})

        email = email.strip() if email else None
        password = password.strip() if password else None

        if not email or not password:
            raise serializers.ValidationError({'message': 'البريد الإلكتروني مطلوب وكلمة المرور مطلوبة'})

        request = self.context.get('request')
        
        user = authenticate(request, email=email, password=password)

        if not user:
            raise serializers.ValidationError({'message': 'كلمة المرور أو البريد الإلكتروني غير صحيحين'})


        self.context['user'] = user
        return attrs

    def to_representation(self, instance):
        user = self.context['user']
        tokens = user.tokens()
        user.last_login = timezone.now()
        user.save()
        return {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'fatherName': user.fathername,
            'motherName': user.mothername,
            'phoneNumber': user.phone,
            'idNationalNumber': user.idNationalNumber,
            'university': user.university.name if user.university else None,
            'faculty': user.faculty,
            'section': user.section,
            'unitNumber': user.unitNumber.Unit_name if user.unitNumber else None,
            'roomNumber': user.room.number if user.room else None,
            'city': user.city,
            'year': user.year,
            'status': user.status,
            'job': user.job,
            'img': user.img,
            'token': str(tokens.get('access')),
            'refresh_token': str(tokens.get('refresh')) 
        }