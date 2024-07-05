from rest_framework.views import APIView 
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from universitie.models import Universitie , Unit ,Room
from rest_framework import status
from rest_framework.exceptions import NotFound
from .serializers import UniversitySearchRequestSerializer,UniversityUnitInputSerializer,RoomSerializer

class Universities(APIView):
    def get(self, request):
        queryset = Universitie.objects.all()
        data_list = list(queryset.values_list('name', flat=True)) 
        return Response(data_list) 
@api_view(['POST'])
def units(request):
    if request.method == 'POST':
        serializer = UniversitySearchRequestSerializer(data=request.data)
        if serializer.is_valid():
            university_name = serializer.validated_data['university_name']
            units = Unit.objects.filter(university_name__name=university_name)
            if units.exists():
                unit_names = [unit.Unit_name for unit in units]
                return Response(unit_names)
            else:
                raise NotFound("اسم الجامعة غير موجود")
        else:
            return Response(serializer.errors, status=400)
class RoomsView(GenericAPIView):
    serializer_class = UniversityUnitInputSerializer

    def get_units(self, university_name):
        try:
            unit = Unit.objects.filter(university_name__name=university_name)
            return unit
        except Unit.DoesNotExist:
            return None

    def get_queryset(self, unit_number=None):
        queryset = Room.objects.all()
        if unit_number:
            try:
                unit = Unit.objects.get(Unit_name=unit_number)
                queryset = queryset.filter(unit=unit)
            except Unit.DoesNotExist:
                queryset = Room.objects.none()
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        university_name = serializer.validated_data.get('university_name')
        unit_number = serializer.validated_data.get('unit_number')

        units = self.get_units(university_name)
        if not units:
            return Response({"error": "University not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset(unit_number)
        if not queryset:
            return Response({"error": "Unit not found"}, status=status.HTTP_404_NOT_FOUND)

        rooms_data = []
        for room in queryset:
            rooms_data.append({
                'room_number': room.number,
                'number_of_students': room.number_of_students
            })

        return Response(rooms_data)
