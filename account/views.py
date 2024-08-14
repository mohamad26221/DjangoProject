from rest_framework.exceptions import APIException
from rest_framework.views import APIView
import random 
import http.client
import json
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from rest_framework.generics import GenericAPIView
from django.utils.translation import activate
from django.urls import reverse
from rest_framework.response import Response
from .forms import LanguageForm
from django.core.mail import EmailMessage
from django.shortcuts import  redirect
from rest_framework import status , serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customuser,Student,RegistrationRequest
from .serializers import UserRegisterSerializer, LoginSerializer,RegistrationRequestSerializer,EmailVerificationSerializer,CustomUserIdSerializer,RegistrationRequestUpdateSerializer,FCMTokenSerializer
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
class RegistrationRequestUpdateView(GenericAPIView):
    serializer_class = RegistrationRequestUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                student = Student.objects.get(email=email)
                registration_request = RegistrationRequest.objects.get(student=student)

                for attr, value in serializer.validated_data.items():
                    if value is not None: 
                        setattr(registration_request, attr, value)
                
                registration_request.save()

                return Response({"message": "تم تحديث طلب التسجيل بنجاح"}, status=status.HTTP_200_OK)

            except Student.DoesNotExist:
                return Response({"error": "الطالب غير موجود"}, status=status.HTTP_404_NOT_FOUND)
            except RegistrationRequest.DoesNotExist:
                return Response({"error": "طلب التسجيل غير موجود"}, status=status.HTTP_404_NOT_FOUND)

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
def change_language(request):
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            activate(language)
            response = redirect(reverse('admin:index'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
    else:
        form = LanguageForm()
    return render(request, 'admin/change_language.html', {'form': form})
class CustomUserDetailView(GenericAPIView):
    serializer_class = CustomUserIdSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data.get('id')
            try:
                user = Customuser.objects.get(id=student_id)
                tokens = RefreshToken.for_user(user)
                response_data = {
                    'id': user.id,
                    'email':user.email,
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
                    'token': str(tokens.access_token),
                    'refresh_token': str(tokens),
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except Customuser.DoesNotExist:
                return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def send_push_notification(token, title, body):
    conn = http.client.HTTPSConnection("fcm.googleapis.com")
    payload = {
        "message": {
            "token": token,  
            "notification": {
                "title": title, 
                "body": body   
            },
            "android": {
                "notification": {
                    "notification_priority": "PRIORITY_MAX",
                    "sound": "default"
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "content_available": True
                    }
                }
            },
            "data": {
                "type": "notification",
                "id": "studentId",  
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
        }
    }
    try:
        print("Payload to be sent:", json.dumps(payload, indent=4))
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_SERVER_KEY'
        }
        conn.request("POST", "/v1/projects/YOUR_PROJECT_ID/messages:send", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
    except Exception as e:
        print(f"An error occurred: {e}")
class UpdateFCMTokenView(GenericAPIView):
    serializer_class = FCMTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['id']
            token = serializer.validated_data['token']
            
            try:
                student = Student.objects.get(id=student_id)
                student.notification_token = token
                student.save()
                return Response({'status': 'Token updated successfully'}, status=status.HTTP_200_OK)
            except Student.DoesNotExist:
                return Response({'error': 'Student with this ID does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)