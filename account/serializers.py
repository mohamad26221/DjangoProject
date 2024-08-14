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
from universitie.models import Unit,Universitie,Room

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
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2', 'year', 'job', 'unitNumber', 'room', 'idNationalNumber', 'university', 'faculty', 'section']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("كلمة المرور غير متطابقة")

        return attrs
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    email_verification_code = serializers.CharField(max_length=6)
class RegistrationRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    university = serializers.CharField(write_only=True)
    unitNumber = serializers.CharField(write_only=True)
    room = serializers.CharField(write_only=True)

    class Meta:
        model = RegistrationRequest
        fields = ['email', 'university', 'unitNumber', 'room', 'Front_face', 'back_face', 'Face_picture', 'payment_method']
        extra_kwargs = {
            'Front_face': {'required': False},
            'back_face': {'required': False},
            'Face_picture': {'required': False},
            'status': {'write_only': True},
            'payment_method': {'write_only': True},
            'Front_face': {'write_only': True},
            'back_face': {'write_only': True},
            'Face_picture': {'write_only': True},
            'idNationalNumber': {'write_only': True}
        }

    def create(self, validated_data):
        email = validated_data.pop('email', None)


        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            raise serializers.ValidationError("البريد الالكتروني هذا غير موجود تأكد من صحة الإدخال")

        if RegistrationRequest.objects.filter(student=student).exists():
            raise serializers.ValidationError("تم تسجيل هذا الطالب بالفعل")
        try:
            university = Universitie.objects.get(name=validated_data.pop('university'))
            unit = Unit.objects.get(Unit_name=validated_data.pop('unitNumber'))
            room = Room.objects.get(number=validated_data.pop('room'))
        except (Universitie.DoesNotExist, Unit.DoesNotExist, Room.DoesNotExist):
            raise serializers.ValidationError("تأكد من صحة المدخلات الخاصة بالجامعة أو الوحدة أو الغرفة")

        registration_request = RegistrationRequest.objects.create(
            student=student,
            university=university,
            unitNumber=unit,
            room=room,
            Front_face=validated_data.get('Front_face'),
            back_face=validated_data.get('back_face'),
            Face_picture=validated_data.get('Face_picture'),
            payment_method=validated_data.get('payment_method'),
            status='في انتظار الموافقة',
        )

        return registration_request
class RegistrationRequestUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True) 

    class Meta:
        model = RegistrationRequest
        fields = [ 'email', 'university', 'unitNumber', 'room', 'Front_face','back_face','Face_picture','payment_method']
        extra_kwargs = {
            'university': {'required': False},
            'unitNumber': {'required': False},
            'room': {'required': False},
            'Front_face': {'required': False},
            'back_face': {'required': False},
            'Face_picture': {'required': False},
            'payment_method': {'required': False},
        }
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
            'id': user.id,
            'email': user.email,
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
class CustomUserIdSerializer(serializers.Serializer): # من اجل جلب بيانات المستخدم من خلال الايدي
    id = serializers.IntegerField()
class FCMTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    token = serializers.CharField(max_length=255)