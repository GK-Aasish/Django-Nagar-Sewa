from django.urls import path
from .views.main_view import dashboard_view

urlpatterns = [
    path('',dashboard_view,name='dashboard')
]
