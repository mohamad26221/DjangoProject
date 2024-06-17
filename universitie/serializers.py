from rest_framework import serializers
from universitie.models import Universitie ,Unit,UniversitySearchRequest,Room

class universitieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universitie
        fields = ['name']

class UniteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['Unit_name'] 
class UniversitySearchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversitySearchRequest
        fields = ['university_name']
class RoomSerializer(serializers.ModelSerializer):
    number_of_students = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = ['id', 'number', 'number_of_students']

class UniversityUnitInputSerializer(serializers.Serializer):
    university_name = serializers.CharField(max_length=100)
    unit_number = serializers.CharField(max_length=30)