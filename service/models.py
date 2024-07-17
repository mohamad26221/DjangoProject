from django.db import models
from django.core.exceptions import ValidationError
from account.models import Student
from universitie.models import Unit,Room
class BreadOrder(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    bread_ties = models.IntegerField(default=None, null=True)
    order_number = models.AutoField(primary_key=True)  
    rule = models.IntegerField()
    STATUS_CHOICES = [
        ('لم يتم الاستلام بعد', 'لم يتم الاستلام بعد'),
        ('تم التسليم', 'تم التسليم'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='لم يتم الاستلام بعد')
    def clean(self):
        existing_order = BreadOrder.objects.filter(student=self.student, status='لم يتم الاستلام بعد').exclude(pk=self.pk)
        if existing_order.exists():
            raise ValidationError('لا يمكنك تقديم أكثر من طلب في نفس الوقت.')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:
            if BreadOrder.objects.exists():
                self.order_number = BreadOrder.objects.latest('order_number').order_number + 1
            else:
                self.order_number = 1

            self.rule = BreadOrder.objects.count() + 1

        super(BreadOrder, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} by {self.student}"
class JobRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attachments = models.FileField(upload_to='C:/Users/Administrator/Desktop/Django-project/venv/subject/account/attachments/')
    request_number = models.AutoField(primary_key=True)
    finishTime = models.TimeField(null=True)
    STATUS_CHOICES = [
        ('في انتظار الموافقة', 'في انتظار الموافقة'),
        ('تمت الموافقة', 'تمت الموافقة'),
        ('تم الرفض', 'تم الرفض'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='في انتظار الموافقة')
    def save(self, *args, **kwargs):
        if not self.pk:
            if JobRequest.objects.exists():
                self.request_number = JobRequest.objects.latest('request_number').request_number + 1
            else:
                self.request_number = 1

        super(JobRequest, self).save(*args, **kwargs)    
    def __str__(self):
        return f"Order {self.request_number} by {self.student}"
class MaintenanceRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='fail_in_room',default=None,null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None,null=True)
    Fail_description = models.TextField()
    Fail_photo = models.FileField(upload_to='C:/Users/Administrator/Desktop/Django-project/venv/subject/account/attachments/')
    request_number = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('طلب جديد', 'طلب جديد'),
        ('ستتم معالجته', 'ستتم معالجته'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='طلب جديد')
    def save(self, *args, **kwargs):
        if not self.pk:
            if MaintenanceRequest.objects.exists():
                self.request_number = MaintenanceRequest.objects.latest('request_number').request_number + 1
            else:
                self.request_number = 1

        super(MaintenanceRequest, self).save(*args, **kwargs) 

    def __str__(self):
        return f"Maintenance Request {self.request_number} by {self.student}"