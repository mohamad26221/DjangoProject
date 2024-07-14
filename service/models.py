from django.db import models
from django.core.exceptions import ValidationError
from account.models import Student
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