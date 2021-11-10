from django.db import models

# Create your models here.
class EmployeesInfo(models.Model):
    employee_id     = models.CharField(max_length  = 200,unique = True)
    employee_email  = models.EmailField(max_length = 256)
    employee_name   = models.CharField(max_length  = 200)
    is_active       = models.BooleanField(default  = True)
    created_at      = models.DateTimeField(auto_now_add = True)
    updated_date    = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return self.name

