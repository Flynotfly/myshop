from django.urls import path
from . import views


app_name = 'payment'

urlpatterns = [
    path('process/', views.process, name='process'),
    path('completed/', views.completed, name='completed'),
    path('canceled/', views.canceled, name='canceled'),
]
