from django.contrib import admin
from .models import Customuser, OneTimePassword ,Student
from universitie.models import Universitie,Unit,Room
# Register your models here.
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'number_of_students']
admin.site.register(Customuser)
admin.site.register(Student)
admin.site.register(Universitie)
admin.site.register(Room,RoomAdmin)
admin.site.register(Unit)


admin.site.site_header = 'التسجيل في السكن'
admin.site.site_title = 'university'
admin.site.site_url = "التسحيل في السكن"
