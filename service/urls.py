# urls.py
from django.urls import path
from .views import BreadOrderView,JobRequestCreateView,MaintenanceRequestCreateView

urlpatterns = [
    path('bread_order/', BreadOrderView.as_view(), name='bread_order'),
    path('job_request/', JobRequestCreateView.as_view(), name='job_request'),
    path('fail_request/', MaintenanceRequestCreateView.as_view(), name='fail_request'),
]
