from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import UserManager
from universitie.models import Universitie , Unit , Room


AUTH_PROVIDERS ={'email':'email', 'google':'google', 'github':'github', 'linkedin':'linkedin'}

class Customuser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False) 
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
    fathername = models.CharField(max_length=20,default=None,null=True)
    mothername = models.CharField(max_length=20,default=None,null=True)
    phone = models.IntegerField(unique=True,null=True)
    idNumber = models.IntegerField(default=None,null=True)
    idNationalNumber = models.IntegerField(unique=True,default=None,null=True)
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None,null=True)
    faculty = models.CharField(max_length=20,default=None,null=True)
    section = models.CharField(max_length=20,default=None,null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None,null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,default=None,null=True)
    city = models.CharField(max_length=20,default=None,null=True)
    year = models.IntegerField(default=None,null=True)
    status = models.CharField(max_length=20,default=None,null=True)
    job = models.CharField(max_length=20,null=True,default=None)
    typejob = models.CharField(max_length=20,null=True,default=None)
    img = models.CharField(max_length=200,null=True,default=None)

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
        return self.first_name

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    @property
    def get_data(self):
        user = Customuser.objects.all().filter(email=self.email)
        return user
class OneTimePassword(models.Model):
    user=models.OneToOneField(Customuser, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)


    def __str__(self):
        return f"{self.user.first_name} - otp code"
class Student(models.Model):
    user = models.OneToOneField(Customuser, on_delete=models.CASCADE, related_name='student_profile')
    email = models.EmailField(max_length=255,default=None,null=True)
    first_name = models.CharField(max_length=100,default=None,null=True)
    last_name = models.CharField(max_length=100,default=None,null=True)
    phone = models.CharField(max_length=15,default=None,null=True)
    unitNumber = models.ForeignKey(Unit, on_delete=models.CASCADE,default=None,null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='students')
    university = models.ForeignKey(Universitie, on_delete=models.CASCADE,default=None,null=True)
    faculty = models.CharField(max_length=20,default=None,null=True)
    section = models.CharField(max_length=20,default=None,null=True)
    year = models.IntegerField(default=None,null=True)   
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
