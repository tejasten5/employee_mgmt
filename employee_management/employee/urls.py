
from django.urls import path
from .views import *

urlpatterns = [
    path('',HomeTemplateView.as_view(),name="home"),
    path('login/',AdminLogin.as_view(),name="login1"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('add/employee/',AddNewEmployee.as_view(),name='add_employee'),
    path('api/employee_list/',EmployeeListAPI.as_view(),name="employee_list"),
    path('api/delete/employee/',DeleteEmployee.as_view(),name="delete_employee"),
    path("edit/<int:pk>/employee/",EditEmployee.as_view(),name="employee_edit"),
    path('search/employee/',EmployeeSearch.as_view(),name="employee_search")
]
