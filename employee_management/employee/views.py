from django.forms import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import (authenticate, login, logout)
from django.http import (HttpResponseRedirect,JsonResponse)
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from ast import literal_eval

# Create your views here.

# Global responsein case of exception
SERVER_ERROR = {"error":"Something went wrong ! Please contact techinical team."}


class HomeTemplateView(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard.html'
    def get_context_data(self,**kwargs): 
        """Call the base implementation first to get a context.
        Add in a QuerySet of all the devices and group.

        Returns:
            queryset: Returns context .
        """            

        context              = super().get_context_data(**kwargs)
        context['employees'] = EmployeesInfo.objects.all()        
        return context

class AdminLogin(View):
    """This class handles login functionality.    
    """
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('/home/')        
        return render(request, 'login.html', {})

    def post(self,request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/home/')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)                    
                    return HttpResponseRedirect('/home/')
            messages.error(request, "Sorry, that didn't work. Please try again")
        return render(request, 'login.html', {})

class LogoutView(View):
    def get(self, request):  
          
        if request.user.is_authenticated:
            user = request.user            
            user.save()
        logout(request)
        return HttpResponseRedirect('/')


class AddNewEmployee(View):
    def post(self,request):
        try:
            form = EmployeeForm(request.POST)
            if form.is_valid():
                form.save()     
                return JsonResponse({"status":"OK"},status = 201)  
                 
            return JsonResponse(form.errors,status = 400)            
        except Exception as e:
            print(str(e))
            return JsonResponse(SERVER_ERROR,status = 500) 


class EmployeeListAPI(LoginRequiredMixin,View):   

    

    def get_initial_query(self):    
        return EmployeesInfo.objects.all()

    def get_ordered_query(self, emp_query, request):        
        column_index    = request.POST.get("order[0][column]")
        order_dir       = request.POST.get("order[0][dir]", "")
        column_name     = request.POST.get(f"columns[{column_index}][data]")

        if column_name:
            prefix = "" if order_dir == "asc" else "-"
            return emp_query.order_by(f"{prefix}{column_name}")
        return emp_query

    def get_filtered_query(self, emp_query, request):        
        searched_value = request.POST.get("search[value]", "").lower()
        return emp_query.filter(
                Q(employee_id__icontains=searched_value)|Q(employee_email__icontains=searched_value)|Q(employee_name__icontains = searched_value)
            )

    def format_paginated_query(self, emp_list, request):        
        emp_data = []
        row_number = emp_list.start_index()
        for emp in emp_list:
            delete_link = f"""<a href="javascript:void(0)"><i class='fa fa-times delete_employee' data-empname = "{emp['employee_name']}"  data-id = "{emp['id']}" title="Employee Delete" style="color: #e80016;" ></i></a>"""
            edit_link = f"""<a href="/edit/{emp['id']}/employee/" title="Edit Employee" class="edit_employee"><i class='fa fa-edit'  style="color: #006fff;"></i></a>"""

            emp_data.append({
                "srno":row_number,
                "employee_id":emp["employee_id"],
                'employee_name':emp["employee_name"],
                'employee_email':emp["employee_email"],
                "action":f"""
                    {edit_link}
                    {delete_link}
                """             
            })   
            row_number += 1
        return emp_data

       
    def post(self,request): 
        try:            
            start = literal_eval(request.POST.get("start", "0"))
            length = literal_eval(request.POST.get("length", "10"))            

            initial_query = self.get_initial_query()
            filtered_location_query = self.get_filtered_query(initial_query, request)
            user_query = self.get_ordered_query(filtered_location_query, request)
            page = int(start/length) + 1
            paginator = Paginator(user_query.values("id","employee_id",'employee_name','employee_email'),length)         
                        

            try:
                employee_list = paginator.page(page)
            except PageNotAnInteger:
                employee_list = paginator.page(1)
            except EmptyPage:
                employee_list = paginator.page(paginator.num_pages)

            user_data = self.format_paginated_query(employee_list, request)
            data = {
                "data": user_data,
                "recordsTotal": initial_query.count(),   
                "recordsFiltered": user_query.count(),             
            }     
            return JsonResponse(data,status = 200)
        except Exception as e:
            print(str(e))
            return JsonResponse(SERVER_ERROR,status = 500)    


class DeleteEmployee(View):
    def post(self,request):
        try:
            employee_id = request.POST.get('employee_id')

            employee_queryset = EmployeesInfo.objects.filter(id = employee_id)
            if employee_queryset.exists():
                employee_queryset.delete()
                return JsonResponse({"status":"Success"},status = 200)
            return JsonResponse({"status":"Error"},status = 400)            
        except Exception as e:
            print(str(e))
            return JsonResponse(SERVER_ERROR,status = 500)


class EditEmployee(View):
    def get(self,request,pk):               
        context = {'employee':get_object_or_404(EmployeesInfo, id = pk)}        
        return render(request,'edit_employee.html',context)

    def post(self,request,pk):
        try:
            instance = get_object_or_404(EmployeesInfo, id = pk)
            form = EditEmployeeForm(request.POST or None, instance=instance)
            if form.is_valid():            
                form.save()
                return  JsonResponse({"status":"OK"},status = 200)    
            return  JsonResponse({"errors":form.errors},status = 400)
        except Exception as e:
            print(str(e))
            return JsonResponse(SERVER_ERROR,status = 500)
        
class EmployeeSearch(View):
    def post(self,request):
        try:
            search_query = request.POST.get('search_query')
            employee = EmployeesInfo.objects.filter(employee_id = search_query)
            if employee.exists():
                return JsonResponse({"employess":list(employee.values())},status = 200)
            return JsonResponse({"errors":"Records Not Found"},status = 400)
        except Exception as e:
            return JsonResponse(SERVER_ERROR,status = 500)