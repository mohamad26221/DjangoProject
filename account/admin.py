from django.contrib import admin
from .models import Customuser ,Student,Staff,RegistrationRequest
from service.models import BreadOrder
from django.utils import timezone
from datetime import timedelta
from universitie.models import Universitie,Unit,Room
from django.contrib.sessions.models import Session
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number','unit','number_of_students']
    list_filter = ['unit']
    search_fields = ['number']
@admin.action(description='الموافقة على الطلب')
def approve_requests(modeladmin, request, queryset):
    for registration_request in queryset:
        if registration_request.status != 'تمت الموافقة':
            student = registration_request.student
            student.university = registration_request.university
            student.unitNumber = registration_request.unitNumber
            student.room = registration_request.room
            student.status = 'تمت الموافقة'
            student.save()
            registration_request.status = 'تمت الموافقة'
            registration_request.save()
@admin.action(description='رفض الطلب')
def reject_requests(modeladmin, request, queryset):
    for registration_request in queryset:
        if registration_request.status != 'مرفوض':
            student = registration_request.student
            student.university = registration_request.university
            student.unitNumber = registration_request.unitNumber
            student.room = registration_request.room
            student.status = 'مرفوض'
            student.save()
            registration_request.status = 'مرفوض'
            registration_request.save()
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'university', 'unitNumber', 'room', 'status']
    list_filter = ['status']
    search_fields = ['idNationalNumber']
    actions = [approve_requests, reject_requests]
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user','unitNumber','room','status']
    list_filter = ['status']
    search_fields = ['phone']
class CustomuserAdmin(admin.ModelAdmin):
    actions = ['logout_all_users']

    def logout_all_users(self, request, queryset):
        # Blacklist all tokens
        tokens = OutstandingToken.objects.all()
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                self.message_user(request, f'Error: {str(e)}', level='error')
        
        # Clear all sessions
        sessions = Session.objects.all()
        for session in sessions:
            session.delete()

        self.message_user(request, "All users have been logged out successfully.")
    
    logout_all_users.short_description = "Logout all users"
    list_display = ['get_full_name','job']
    list_filter = ['job']
    search_fields = ['idNationalNumber']
class BreadOrderAdmin(admin.ModelAdmin):
    exclude = ('rule',)  
    list_display = ('student', 'order_number', 'bread_ties','rule', 'status') 
    list_filter = ('status',)  
    search_fields = ('order_number',) 

    def approve_orders(self, request, queryset):
        for order in queryset:
            if order.status != 'تم التسليم':
                order.status = 'تم التسليم'
                order.save()
                order.delete()
        self.message_user(request, f"تمت الموافقة على {queryset.count()} طلبات بنجاح.")

    approve_orders.short_description = "الموافقة على الطلبات المحددة"

    actions = [approve_orders]


admin.site.register(BreadOrder, BreadOrderAdmin)
admin.site.register(Customuser,CustomuserAdmin)
admin.site.register(RegistrationRequest,RegistrationRequestAdmin)
admin.site.register(Staff)
admin.site.register(Student,StudentAdmin)
admin.site.register(Universitie)
admin.site.register(Room,RoomAdmin)
admin.site.register(Unit)



admin.site.site_header = 'التسجيل في السكن'
admin.site.index_title='ادارة السكن الجامعي'
admin.site.site_title = 'Tishreen'
admin.site.site_url = "التسحيل في السكن"
