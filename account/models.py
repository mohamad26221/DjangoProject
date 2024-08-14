from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from guardian.shortcuts import assign_perm
from .managers import UserManager
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from universitie.models import Universitie , Unit , Room

AUTH_PROVIDERS ={'email':'email', 'google':'google', 'github':'github', 'linkedin':'linkedin'}

class Customuser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True) 
    email = models.EmailField(max_length=255, verbose_name=_("Email Address"), unique=True)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    fathername = models.CharField(max_length=20,default=None, blank=True, null=True)
    mothername = models.CharField(max_length=20,default=None, blank=True, null=True)
    phone = models.IntegerField(unique=True,null=True)
    idNumber = models.IntegerField(default=None, blank=True, null=True)
    idNationalNumber = models.IntegerField(unique=True,default=None, blank=True, null=True)
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None, blank=True, null=True)
    faculty = models.CharField(max_length=20,default=None, blank=True, null=True)
    section = models.CharField(max_length=20,default=None, blank=True, null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,default=None, blank=True, null=True)
    city = models.CharField(max_length=20,default=None, blank=True, null=True)
    year = models.CharField(max_length=10,default=None, blank=True, null=True)
    notification_token = models.CharField(max_length=255, null=True, blank=True)  
    typeJob = models.CharField(max_length=10,default=None, blank=True, null=True)
    img = models.CharField(max_length=200,null=True,default=None, blank=True)
    status = models.CharField(max_length=20,default='غير مسجل في السكن',null=True)
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),)
    job = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student',null=True)
    email_verification_code = models.CharField(max_length=20, null=True, blank=True)
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    class Meta:
        verbose_name_plural = "المستخدمين"
        verbose_name = ("مستخدم") 
class Student(models.Model):
    user = models.OneToOneField(Customuser, on_delete=models.CASCADE, related_name='student_profile')
    email = models.EmailField(max_length=255,default=None, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    last_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    phone = models.CharField(max_length=15,default=None, blank=True, null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='students_in_room',default=None, blank=True, null=True)
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None, blank=True, null=True)
    idNationalNumber = models.IntegerField(unique=True,default=None, blank=True, null=True)
    faculty = models.CharField(max_length=20,default=None, blank=True, null=True)
    section = models.CharField(max_length=20,default=None, blank=True, null=True)
    notification_token = models.CharField(max_length=255, null=True, blank=True)  
    year = models.CharField(max_length=10,default=None, blank=True, null=True)
    status = models.CharField(max_length=20,default='غير مسجل في السكن',null=True)   
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        assign_perm('change_room', self.user, self)
    class Meta:
        permissions = [
            ('change_room', 'Can change room field'),
        ]
    class Meta:
        verbose_name_plural = "الطلاب"
        verbose_name = ("طالب")  
class Staff(models.Model):
    user = models.OneToOneField(Customuser, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255,default=None, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    last_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    phone = models.CharField(max_length=15,default=None, blank=True, null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None, blank=True, null=True)
    idNationalNumber = models.IntegerField(unique=True,default=None, blank=True, null=True)
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None, blank=True, null=True)
    year = models.CharField(max_length=10,default=None, blank=True, null=True)
    USER_TYPE_CHOICES = (
        ('مشرف وحدة', 'مشرف وحدة'),
        ('موظف ذاتية','موظف ذاتية'),
        ('معتمد خبز','معتمد خبز'),
        ('حارس باب','حارس باب'),)
    typeJob = models.CharField(max_length=10, choices=USER_TYPE_CHOICES,default=None, blank=True, null=True)  
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    class Meta:
        verbose_name_plural = "الموظفين"
        verbose_name = ("الموظفين")  
class RegistrationRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None, blank=True, null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None, blank=True, null=True)
    idNationalNumber = models.IntegerField(unique=True,default=None, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='requests_for_room',default=None, blank=True, null=True)
    Front_face = models.FileField(upload_to='C:/Users/Administrator/Desktop/Django-project/venv/subject/account/attachments/',default=None, blank=True, null=True)
    back_face = models.FileField(upload_to='C:/Users/Administrator/Desktop/Django-project/venv/subject/account/attachments/',default=None, blank=True, null=True)
    Face_picture = models.FileField(upload_to='C:/Users/Administrator/Desktop/Django-project/venv/subject/account/attachments/',default=None, blank=True, null=True)
    payment_method = models.CharField(max_length=50,default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='في انتظار الموافقة')

    def __str__(self):
        return f"Request for {self.student} at {self.university}"
    class Meta:
        verbose_name_plural = "طلبات التسجيل في السكن"
        verbose_name = ("طلبات التسجيل في السكن")         