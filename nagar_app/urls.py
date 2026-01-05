from django.urls import path
from .views.main_view import dashboard_view
from .views.auth_view import signup_module,login_module

urlpatterns = [
    path('',dashboard_view,name='dashboard'),
    path('signup/',signup_module,name='signup'),
    path('login/',login_module,name='login'),
]
