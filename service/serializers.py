from rest_framework import serializers
from .models import BreadOrder, Student ,JobRequest,MaintenanceRequest

class BreadOrderSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    order_number = serializers.ReadOnlyField()
    rule = serializers.ReadOnlyField()

    class Meta:
        model = BreadOrder
        fields = [ 'phone','bread_ties', 'order_number', 'rule']

    def validate(self, attrs):
        phone = attrs.get('phone')
        student = Student.objects.filter(phone=phone).first()
        if not student:
            raise serializers.ValidationError("هذا الطالب غير موجود تحقق من الرقم")
        if student.status != 'تمت الموافقة':
            raise serializers.ValidationError("يجب ان يكون الطالب مسجل في السكن")
        existing_order = BreadOrder.objects.filter(student=student, status='لم يتم الاستلام بعد').exists()
        if existing_order:
            raise serializers.ValidationError("لا يمكنك تقديم أكثر من طلب في نفس الوقت")
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        student = Student.objects.get(phone=phone)
        
        validated_data['student'] = student
        if BreadOrder.objects.exists():
            latest_order_number = BreadOrder.objects.latest('order_number').order_number
            validated_data['order_number'] = latest_order_number + 1
        else:
            validated_data['order_number'] = 1

        validated_data['rule'] = BreadOrder.objects.count() + 1

        bread_order = BreadOrder.objects.create(**validated_data)
        return bread_order
class JobRequestSerializer(serializers.ModelSerializer):
    request_number = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    class Meta:
        model = JobRequest
        fields = ['student', 'attachments', 'request_number', 'status']
    def validate(self, data):
        if JobRequest.objects.filter(student=data['student']).exists():
            raise serializers.ValidationError("لا يمكنك تقديم اكثر من طلب")
        return data
    def create(self, validated_data):
        job_request = JobRequest.objects.create(
            student=validated_data['student'],
            attachments=validated_data['attachments']
        )
        return job_request
class MaintenanceRequestSerializer(serializers.ModelSerializer):
    request_number = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    class Meta:
        model = MaintenanceRequest
        fields = ['student', 'room', 'unitNumber', 'Fail_description', 'Fail_photo', 'request_number', 'status']
    def validate(self, data):
        if MaintenanceRequest.objects.filter(student=data['student']).exists():
            raise serializers.ValidationError("لا يمكنك تقديم اكثر من طلب")
        return data        