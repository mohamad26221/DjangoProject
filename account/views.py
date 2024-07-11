from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status , serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, LoginSerializer,RegistrationRequestSerializer
class CustomAuthenticationFailed(APIException):
    status_code = 200
    default_detail = 'Invalid credentials.'
    default_code = 'authentication_failed'
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            return Response({'data':user_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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