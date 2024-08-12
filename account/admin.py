from django.contrib import admin
from django.utils import timezone
from .models import Customuser ,Student,Staff,RegistrationRequest
from django.urls import path
from .views import change_language,send_push_notification
from service.models import BreadOrder ,JobRequest,MaintenanceRequest,Notification
from django.utils.translation import gettext_lazy as _
from universitie.models import Universitie,Unit,Room
from django.contrib.sessions.models import Session
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number','unit','number_of_students']
    list_filter = ['unit']
    search_fields = ['number']
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'university', 'unitNumber', 'room', 'status']
    list_filter = ['status']
    search_fields = ['idNationalNumber']

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
                Notification.objects.create(
                student=student,
                title='طلب التسجيل مرفوض',
                body=f"تم رفض طلب التسجيل الخاص بك في {registration_request.university.name}.",
                date=timezone.now().date(),
                time=timezone.now().time()
                )
                send_push_notification(student.notification_token, "طلب التسجيل مرفوض", "نأسف، تم رفض طلب التسجيل الخاص بك.")

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
                Notification.objects.create(
                student=student,
                title='طلب التسجيل تمت الموافقة عليه',
                body=f" تمت الموافقة على طلب التسجيل الخاص بك في سكن {registration_request.university.name}.",
                date=timezone.now().date(),
                time=timezone.now().time()
                )
                send_push_notification(student.notification_token, "طلب التسجيل تمت الموافقة عليه", "تهانينا، تمت الموافقة على طلب التسجيل الخاص بك في سكن جامعة تشرين.")

    approve_requests.short_description = "الموافقة على الطلبات المحددة"
    reject_requests.short_description = "رفض الطلبات المحددة"
    actions = [approve_requests, reject_requests]
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user','unitNumber','room','status']
    list_filter = ['status']
    search_fields = ['phone']
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='مشرف وحدة').exists():
            user_unit_number = request.user.unitNumber
            qs = qs.filter(unitNumber=user_unit_number)
        return qs
    def get_fields(self, request, obj=None):
        if request.user.groups.filter(name='مشرف وحدة').exists():
            return ['room']  
        else:
            return ['user','email', 'first_name', 'last_name', 'phone', 'year','unitNumber', 'room', 'idNationalNumber', 'university', 'faculty', 'section','status']
    def has_change_permission(self, request, obj=None):
            return True  
class CustomuserAdmin(admin.ModelAdmin):
    exclude = ('email_verification_code',)
    actions = ['logout_selected_users']

    def logout_selected_users(self, request, queryset):
        user_ids = queryset.values_list('id', flat=True)
        
        tokens = OutstandingToken.objects.filter(user_id__in=user_ids)
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                self.message_user(request, f'Error: {str(e)}', level='error')
        
        sessions = Session.objects.all()
        for session in sessions:
            session_data = session.get_decoded()
            if str(session_data.get('_auth_user_id')) in map(str, user_ids):
                session.delete()

        self.message_user(request, "Selected users have been logged out successfully.")
    
    logout_selected_users.short_description = "Logout selected users"
    list_display = ['get_full_name','job','status']
    list_filter = ['status']
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
class JobRequestAdmin(admin.ModelAdmin):
    exclude = ('status',)
    list_display = ['student','request_number','status','finishTime']
    list_filter = ['status']
    search_fields = ['request_number']
    def approve_requests(self, request, queryset):
        for order in queryset:
            if order.status != 'تمت الموافقة':
                order.status = 'تمت الموافقة'
                order.save()
        self.message_user(request, f"تمت الموافقة على {queryset.count()} طلبات بنجاح.")

    approve_requests.short_description = "الموافقة على الطلبات المحددة"

    def reject_requests(self, request, queryset):
        for order in queryset:
            if order.status != 'تم الرفض':
                order.status = 'تم الرفض'
                order.save()
        self.message_user(request, f"تمت رفض {queryset.count()} طلبات بنجاح.")

    reject_requests.short_description = "رفض على الطلبات المحددة"

    actions = [approve_requests,reject_requests]   
class MaintenanceRequestAdmin(admin.ModelAdmin):
    exclude = ('status',)
    list_display = ['student','request_number','room','unitNumber','status']
    list_filter = ['status','unitNumber']
    search_fields = ['request_number']
    def approve_requests(self, request, queryset):
        for order in queryset:
            if order.status != 'ستتم معالجته':
                order.status = 'ستتم معالجته'
                order.save()
        self.message_user(request, f"تمت الموافقة على {queryset.count()} طلبات بنجاح.")

    approve_requests.short_description = "تم الاطلاع عليه"

    actions = [approve_requests]   
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='مشرف وحدة').exists():
            user_unit_number = request.user.unitNumber
            qs = qs.filter(unitNumber=user_unit_number)
        return qs
class CustomAdminSite(admin.AdminSite):
    site_header = "Custom Admin"
    site_title = "Admin Portal"
    index_title = "Welcome to Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-language/', self.admin_view(change_language), name='change_language'),
        ]
        return custom_urls + urls

    def each_context(self, request):
        context = super().each_context(request)
        context['available_languages'] = [
            ('en', _('English')),
            ('ar', _('Arabic'))
        ]
        return context

admin_site = CustomAdminSite(name='customadmin')


admin.site.register(BreadOrder, BreadOrderAdmin)
admin.site.register(Customuser,CustomuserAdmin)
admin.site.register(RegistrationRequest,RegistrationRequestAdmin)
admin.site.register(Staff)
admin.site.register(Notification)
admin.site.register(Student,StudentAdmin)
admin.site.register(Universitie)
admin.site.register(Room,RoomAdmin)
admin.site.register(Unit)
admin.site.register(JobRequest,JobRequestAdmin)
admin.site.register(MaintenanceRequest,MaintenanceRequestAdmin)




admin.site.site_header = 'ادارة السكن الجامعي'
admin.site.index_title='ادارة السكن الجامعي'
admin.site.site_title = 'Tishreen'
admin.site.site_url = "التسحيل في السكن"
