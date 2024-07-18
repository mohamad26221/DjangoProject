from rest_framework.exceptions import APIException
from rest_framework.views import APIView
import random
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from service.models import BreadOrder
from rest_framework import status , serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customuser
from .serializers import UserRegisterSerializer, LoginSerializer,RegistrationRequestSerializer,EmailVerificationSerializer
class CustomAuthenticationFailed(APIException):

    status_code = 200
    default_detail = 'Invalid credentials.'
    default_code = 'authentication_failed'
temporary_user_data = {}
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_data = serializer.validated_data
            email = user_data['email']
            
            if Customuser.objects.filter(email=email).exists():
                return Response({'error': 'المستخدم بهذا البريد الإلكتروني موجود بالفعل'}, status=status.HTTP_400_BAD_REQUEST)
            def get_random_numeric_string(length=6):
                numbers = '0123456789'
                return ''.join(random.choice(numbers) for _ in range(length))

            verification_code = get_random_numeric_string(6)
            temporary_user_data[email] = {
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'phone': user_data['phone'],
                'password': user_data['password'],
                'year': user_data['year'],
                'job': user_data['job'],
                'unitNumber': user_data['unitNumber'],
                'room': user_data['room'],
                'idNationalNumber': user_data['idNationalNumber'],
                'university': user_data['university'],
                'faculty': user_data['faculty'],
                'section': user_data['section'],
                'verification_code': verification_code
            }
            subject = 'رمز التحقق'
            message = f'شكرا لتسجيلك في تطبيق المدينة الجامعية رمز التحقق هو :{verification_code}'
            from_email = 'Tishreen <garethbale26221@gmail.com>'
            to_email = [email]

            email_message = EmailMessage(subject, message, from_email, to_email)
            email_message.send()

            return Response({'message': 'تم إرسال رمز التحقق إلى بريدك الإلكتروني. يرجى التحقق من بريدك لإكمال التسجيل.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class EmailVerificationAPIView(GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        verification_code = serializer.validated_data['email_verification_code']

        if email not in temporary_user_data:
            return Response({'error': 'المستخدم غير موجود أو لم يتم إرسال رمز التحقق'}, status=status.HTTP_404_NOT_FOUND)

        if temporary_user_data[email]['verification_code'] == verification_code:
            user_data = temporary_user_data.pop(email)
            user = Customuser(
                email=email,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                year=user_data['year'],
                job=user_data['job'],
                unitNumber=user_data['unitNumber'],
                room=user_data['room'],
                idNationalNumber=user_data['idNationalNumber'],
                university=user_data['university'],
                faculty=user_data['faculty'],
                section=user_data['section'],
                is_active=True,
                is_verified=True

            )
            user.set_password(user_data['password'])
            user.save()
            return Response({'message': 'تم التحقق من البريد الإلكتروني بنجاح. يمكنك الآن تسجيل الدخول.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'رمز التحقق غير صحيح'}, status=status.HTTP_400_BAD_REQUEST)
class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            detail = e.detail
            if isinstance(detail, dict):
                message = "; ".join(" ".join(errors) for errors in detail.values())
            else:
                message = detail
            return Response({'message': message}, status=status.HTTP_200_OK)
        except CustomAuthenticationFailed as e:
            return Response({'message': e.detail}, status=status.HTTP_200_OK)
        
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
class RegistrationRequestView(GenericAPIView):
    serializer_class = RegistrationRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            registration_request = serializer.save()
            student = registration_request.student
            student.status = 'في انتظار الموافقة'
            student.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LogoutView(APIView):  
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)