from django.db.models.signals import post_save,post_delete,pre_save,pre_delete
from django.dispatch import receiver
from .models import Student,Customuser,Staff
from django.db.models import F
from django.contrib.auth.models import Group
from service.models import BreadOrder

@receiver(pre_save, sender=Student)
def store_old_room(sender, instance, **kwargs):
    if instance.pk:
        instance._old_room = Student.objects.get(pk=instance.pk).room
    else:
        instance._old_room = None
@receiver(post_save, sender=Student)
def update_room_student_count_on_save(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        if room:
            room.number_of_students += 1
            room.save()
    else:
        old_room = instance._old_room
        new_room = instance.room
        if old_room != new_room:
            if old_room:
                old_room.number_of_students -= 1
                old_room.save()
            if new_room:
                new_room.number_of_students += 1
                new_room.save()
@receiver(post_delete, sender=Student)
def update_room_student_count_on_delete(sender, instance, **kwargs):
    room = instance.room
    if room:
        room.number_of_students -= 1
        room.save()
@receiver(post_save, sender=Customuser)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.job == 'student':
        Student.objects.create(
                user=instance,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                phone=instance.phone,
                unitNumber=instance.unitNumber,
                room=instance.room,
                university=instance.university,
                faculty=instance.faculty,
                section=instance.section,
                status = instance.status,
                idNationalNumber=instance.idNationalNumber,
                year=instance.year)
        instance.is_staff = False  
        instance.save(update_fields=['is_staff'])  
    elif created and instance.job == 'staff':
            Staff.objects.create(
                user=instance,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                phone=instance.phone,
                university=instance.university,
                idNationalNumber=instance.idNationalNumber,
                year=instance.year,
                status = instance.status,
                typeJob=instance.typeJob,
            )        
            instance.is_staff = True  
            instance.save(update_fields=['is_staff'])
    elif not created and instance.job == 'staff':
        try:
            
            student = Student.objects.get(user=instance)
            Staff.objects.create(
                user=instance,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                phone=instance.phone,
                university=instance.university,
                idNationalNumber=instance.idNationalNumber,
                year=instance.year,
                status = instance.status,
                typeJob=instance.typeJob,
            )
            student.delete()
            instance.is_staff = True  
            instance.save(update_fields=['is_staff'])
        except Student.DoesNotExist:
            pass  
    elif not created and instance.job == 'student':
        try:
            employee = Staff.objects.get(user=instance)
            Student.objects.create(
                user=instance,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                phone=instance.phone,
                unitNumber=instance.unitNumber,
                room=instance.room,
                university=instance.university,
                faculty=instance.faculty,
                section=instance.section,
                idNationalNumber=instance.idNationalNumber,
                status = instance.status,
                year=instance.year,
            )
            employee.delete()
            instance.is_staff = False  
            instance.save(update_fields=['is_staff'])
        except Staff.DoesNotExist:
            pass 

@receiver(post_save, sender=Student)
def update_student_profile(sender, instance, created, **kwargs):
    if not created :
        try:
            customuser = instance.user  
            if customuser:
                customuser.email = instance.email
                customuser.first_name = instance.first_name
                customuser.last_name = instance.last_name
                customuser.phone = instance.phone
                customuser.unitNumber = instance.unitNumber
                customuser.room = instance.room
                customuser.university = instance.university
                customuser.faculty = instance.faculty
                customuser.section = instance.section
                customuser.notification_token = instance.notification_token
                customuser.idNationalNumber = instance.idNationalNumber
                customuser.year = instance.year
                customuser.status = instance.status
                customuser.save()
        except Student.DoesNotExist:
            pass
@receiver(post_save, sender=Staff)
def update_staff_profile(sender, instance, created, **kwargs):
    available_groups = ['مشرف وحدة','موظف ذاتية','معتمد خبز','حارس باب']
    if not created : 
        try:
            customuser = instance.user  
            if instance.typeJob:
                customuser.groups.clear()
            if customuser:
                customuser.email = instance.email
                customuser.first_name = instance.first_name
                customuser.last_name = instance.last_name
                customuser.phone = instance.phone
                customuser.unitNumber = instance.unitNumber
                customuser.university = instance.university
                customuser.idNationalNumber = instance.idNationalNumber
                customuser.year = instance.year
                customuser.status = instance.status
                if instance.typeJob in available_groups:
                    group = Group.objects.get(name=instance.typeJob)
                    customuser.groups.add(group)
                customuser.save()
        except Staff.DoesNotExist:
            pass

@receiver(pre_delete, sender=BreadOrder)
def update_rule(sender, instance, **kwargs):
    current_position = instance.rule
    BreadOrder.objects.filter(rule__gt=current_position).update(rule=F('rule') - 1)