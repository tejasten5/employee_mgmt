from django.forms import ModelForm,Form, forms
from .models import *

class EmployeeForm(ModelForm):
    class Meta:
        model = EmployeesInfo
        exclude = ('is_active','created_at','updated_date')

    def clean_employee_email(self):
        email=self.cleaned_data['employee_email']      
        if EmployeesInfo.objects.filter(employee_email=email).exists():
            raise forms.ValidationError("Email already exists.Please use a different email.")       
        return email

class EditEmployeeForm(ModelForm):
    class Meta:
        model = EmployeesInfo
        exclude = ('employee_id','is_active','created_at','updated_date')

    # def clean_employee_email(self):
        
    #     email=self.cleaned_data['employee_email']      
    #     if EmployeesInfo.objects.filter(employee_email=email).exists():
    #         raise forms.ValidationError("Email already exists.Please use a different email.")       
    #     return email