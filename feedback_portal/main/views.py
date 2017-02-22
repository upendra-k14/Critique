import csv
import tempfile
import pandas
import re

from django.shortcuts import render
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.exceptions import *
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.conf import settings
from django.contrib.auth.views import logout
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url,render
from django.template.response import TemplateResponse
from django.core.mail import send_mail
import json


from .forms import *
from .models import Student, Professor, Admin

# ----------------------------------------------------------------------------------------
# mylogin_required : It is an authentication function used to check whether a user is logged in or not
# Uses the request object to check the user attribute. If the attribute is null (no user logged in) then redirects to log in page
# Any function can be made into an authenticated function by using the "@mylogin_required" override.
def mylogin_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.id:
            return HttpResponseRedirect("/login")
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# ----------------------------------------------------------------------------------------
# NOTE: Create a good welcome page and link it to index. Till then, function can be used to test other pages
def index(request):
    context = dict()
    return render(request, 'main/home.html', context)

# ----------------------------------------------------------------------------------------
# NOTE: No register function needed, please remove
def register(request):
    template_name = "main/register.html"
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "main/register_after.html", {})
    else:
        form = UserForm()
    token = {}
    token.update(csrf(request))
    token['form'] = form
    return render(request, template_name, token)

# @login_required
def home(request):
    return render(request, 'main/home.html', {})

def view_data(model_name):
    context = dict()
    model = eval(model_name)
    field_names = model._meta.get_fields()
    required_fields = list()
    for field in field_names:
        if not field.auto_created:
           required_fields.append(field.name)
    data = model.objects.all()
    required_data = list()
    for each in data:
        row_data = list()
        for field in required_fields:
               row_data.append(getattr(each,field))
        required_data.append(row_data)
    context['data'] = required_data
    context['fields'] = required_fields
    context['model_name'] = model_name
    return context

def displayStu(request):
    return render(request,'main/tables.html',view_data('Student'))

def displayAdm(request):
    return render(request,'main/tables.html',view_data('Admin'))

def displayPro(request):
    return render(request,'main/tables.html',view_data('Professor'))

def check_csv(row,field_nr):
    row = [val.strip(' ') for val in row ]
    context = dict()
    if len(row) != field_nr:
        context['err_msg'] = 'The csv file does not have required number of columns'
    elif not all(isinstance(val, str) for val in  row):
        context['err_msg'] = 'The csv file contains unexpected data'
    elif any(val in (None, "", " ") for val in row):
        context['err_msg'] = 'One of the fields seems to be empty'
    elif any(re.search(r'[^A-Za-z0-9_@.]+', val) for val in row):
        context['err_msg'] = 'One of the fields seems to have special characters'
    context['err_at'] = ', '.join(row)
    if context.has_key('err_msg'):
        return context
    else:
        return False

# @login_required
def addStudents(request):
    context = dict()
    if request.method=='POST':
            if not (request.FILES):
                return self.construct_form(request, True, False)
            f = request.FILES['CSVFile']
            reader = csv.reader(f.read().splitlines())
            for row in reader:
                context = check_csv(row, 3)
                if context!=False:
                    return render(request,'main/error.html',context)

                try:
                    user_instance = User.objects.create(username=row[0])
                    Student.objects.create(user=user_instance, rollno = row[1])

                except IntegrityError:
                        continue
            return render(request,'main/view.html',view_data('Student'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Student'
        return render(request,"main/upload.html",context)

# @login_required
def addProfessor(request):
    context = dict()
    if request.method=='POST':
            if not (request.FILES):
                return self.construct_form(request, True, False)
            f = request.FILES['CSVFile']
            reader = csv.reader(f.read().splitlines())
            for row in reader:
                    context = check_csv(row, 2)
                    if context!=False:
                        return render(request,'main/error.html',context)

                    try:
                        user_instance = User.objects.create(username=row[1])
                        Professor.objects.create(user=user_instance, fullname = row[0])
                    except IntegrityError:
                        continue
            return render(request,'main/view.html',view_data('Professor'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Professor'
        return render(request,"main/upload.html",context)

# @login_required
def addAdmin(request):
    context = dict()
    if request.method=='POST':
            if not (request.FILES):
                return self.construct_form(request, True, False)
            f = request.FILES['CSVFile']
            reader = csv.reader(f.read().splitlines())
            for row in reader:
                    context = check_csv(row, 2)
                    if context!=False:
                        return render(request,'main/error.html',context)

                    try:
                         user_instance = User.objects.create(username=row[0])
                         Admin.objects.create(user=user_instance)
                    except IntegrityError:
                        continue
            return render(request,'main/view.html',view_data('Admin'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Adminstrator'
        return render(request,"main/upload.html",context)


@csrf_exempt
def mobile_login(request):
    """
    Function for authentication of user from Android app
    """

    if request.method == 'POST':
        # get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')
        # authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'login_status':'success','id':user.id})
        else:
            return JsonResponse({'login_status':'failed'})
    else:
        return JsonResponse({'login_status':'wrong request'})
