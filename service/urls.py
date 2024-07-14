# urls.py
from django.urls import path
from .views import BreadOrderView

urlpatterns = [
    path('bread_order/', BreadOrderView.as_view(), name='bread_order'),
]
