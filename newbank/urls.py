from django.urls import path
from .views import bank_admin,custom_login,landing,add_branch,bank_login,logout_view,branch_details,register_and_create_account
from .views import DashboardView,make_transfer,add_employee
urlpatterns = [
    path('bank/<str:bank_id>/', bank_admin, name='bank'),
    path('login/', custom_login, name='login'),#
    path('landing/', landing, name='landing'),
    path('bank_login/', bank_login, name='bank_login'),#
    path('add_branch/', add_branch, name='add_branch'),
    path('branch/<str:branch_ifsc>/', branch_details, name='branch_details'),
    path('logout/', logout_view, name='logout'),
    path('register_and_create_account/<str:ifsc_code>', register_and_create_account, name='register_and_create_account'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('make_transfer/', make_transfer, name='make_transfer'),
    path('add_employee/<str:ifsc_code>/', add_employee, name='add_employee'),

]
