# djnagoadmin/urls.py
from django.urls import path
from .views import CustomAdminLoginView, dashboard_redirect

urlpatterns = [
    path('admin/login/', CustomAdminLoginView.as_view(), name='custom_admin_login'),
    path('admin/dashboard/', dashboard_redirect, name='dashboard_redirect'),
]

