from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from universitie.models import Room

@receiver(post_save, sender=Student)
def update_room_students_count(sender, instance, created, **kwargs):
    if created:
        instance.room.number_of_students += 1
        instance.room.save()
