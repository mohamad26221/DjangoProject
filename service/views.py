from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .models import MaintenanceRequest
from .serializers import BreadOrderSerializer,JobRequestSerializer,MaintenanceRequestSerializer

class BreadOrderView(GenericAPIView):
    serializer_class = BreadOrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class JobRequestCreateView(GenericAPIView):
    serializer_class = JobRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job_request = serializer.save()
            response_data = {
                'request_number': job_request.request_number,
                'status': job_request.status
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors.get('non_field_errors', ["لا يمكنك تقديم اكثر من طلب"])}, status=status.HTTP_400_BAD_REQUEST)
class MaintenanceRequestCreateView(GenericAPIView):
    serializer_class = MaintenanceRequestSerializer

    def post(self, request, *args, **kwargs):
        room_number = request.data.get('room')
        unit_number = request.data.get('unitNumber')

        if MaintenanceRequest.objects.filter(room=room_number, unitNumber=unit_number).exists():
            return Response({'message': 'لا يمكنكم التقديم بأكثر من طلب لنفس الغرفة'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            maintenance_request = serializer.save()
            response_data = {
                'request_number': maintenance_request.request_number,
                'status': maintenance_request.status
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)