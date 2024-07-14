from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from .models import Student,Customuser,Staff

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
                typeJob=instance.typeJob,
            )
            student.delete()
            instance.is_staff = True  
            instance.save(update_fields=['is_staff'])
        except Student.DoesNotExist:
            pass  
    elif instance.job == 'student':
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
                year=instance.year,
            )
            employee.delete()
            instance.is_staff = False  
            instance.save(update_fields=['is_staff'])
        except Staff.DoesNotExist:
            pass 