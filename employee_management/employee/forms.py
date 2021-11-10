from django.forms import ModelForm,Form
from .models import *

class EmployeeForm(ModelForm):
    class Meta:
        model = EmployeesInfo
        exclude = ('is_active','created_at','updated_date')