from django.urls import path
from .views.main_view import dashboard_view,setting_view,notice_view
from .views.auth_view import signup_module,login_module,logout_module

urlpatterns = [
    path('',dashboard_view,name='dashboard'),
    path('signup/',signup_module,name='signup'),
    path('login/',login_module,name='login'),
    path('setting/',setting_view,name='setting'),
    path('notice/',notice_view,name ='notice'),
    path('logout/',logout_module,name='logout'),
    path("settings/change-password/",setting_view, name="change_password"),
]
