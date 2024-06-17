from django.urls import path
from .views import Universities,units,RoomsView




urlpatterns = [
    path('universities/', Universities.as_view(), name='universities-list'),
    path('unites/', units, name='Unites-list'),
    path('rooms/', RoomsView.as_view(), name='room-list'),
]