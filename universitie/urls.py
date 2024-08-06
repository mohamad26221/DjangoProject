from django.urls import path
from .views import Universities,units,RoomsView
from . import views
urlpatterns = [
    path('universities/', Universities.as_view(), name='universities-list'),
    path('unites/', units, name='Unites-list'),
    path('long_polling/', views.long_polling_view, name='long_polling'),    
    path('rooms/', RoomsView.as_view(), name='room-list'),
]