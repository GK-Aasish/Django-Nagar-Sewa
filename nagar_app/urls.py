from django.urls import path
from .views.main_view import dashboard_view,setting_view,notice_view,react_to_notice,delete_notice_view
from .views.auth_view import signup_module,login_module,logout_module
from .views.components_view import add_notice_model,edit_notice_view,cancel_edit

urlpatterns = [
    path('',dashboard_view,name='dashboard'),
    path('signup/',signup_module,name='signup'),
    path('login/',login_module,name='login'),
    path('setting/',setting_view,name='setting'),
    path('notice/',notice_view,name ='notice'),
    path('notice/add/',add_notice_model,name='add_notice'),
    path("notice/react/", react_to_notice, name="react_to_notice"),
    path('notices/edit/<int:notice_id>/', edit_notice_view, name='edit_notice'),
    path('notices/delete/<int:notice_id>/', delete_notice_view, name='delete_notice'),
    path('notice/<int:notice_id>/cancel/', cancel_edit, name='cancel_edit_notice_confirm'),
    path('logout/',logout_module,name='logout'),
    path("settings/change-password/",setting_view, name="change_password"),
]