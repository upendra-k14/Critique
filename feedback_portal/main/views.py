import csv
import re
import pdb
import hashlib
import datetime
import json

from io import TextIOWrapper
from random import choice
from string import ascii_uppercase

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
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.http import Http404


from .forms import *
from .models import *

# ----------------------------------------------------------------------------------------
# mylogin_required : It is an authentication function used to check whether a user is logged in or not
# Uses the request object to check the user attribute. If the attribute is null (no user logged in) then redirects to log in page
# Any function can be made into an authenticated function by using the
# "@mylogin_required" override.
def mylogin_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.id:
            return HttpResponseRedirect('/login')
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# ----------------------------------------------------------------------------------------
# NOTE: Create a good welcome page and link it to index. Till then,
# function can be used to test other pages


def index(request):
    context = dict()
    return render(request, 'main/home.html', context)

# ----------------------------------------------------------------------------------------
# NOTE: No register function needed, please remove
def register(request):
    template_name = 'main/register.html'
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'main/register_after.html', {})
    else:
        form = UserForm()
    token = {}
    token.update(csrf(request))
    token['form'] = form
    return render(request, template_name, token)

@mylogin_required
def req_feed(request):
    form = FeedbackRequestForm()
    context = dict()
    context['form'] = form
    template_name = "main/request.html"

    if request.method == 'POST':
        form = RequestFeedback()
        form.request_by = request.user
        try:
            print(request.POST['course'])
            form.course = Course.objects.filter(id = int(request.POST['course']))[0]
        except ValueError:
            context["inv_course"] = True
            return render(request, template_name, context)
        try:
            form.end_date = datetime.datetime.strptime(request.POST['end_date'], "%Y-%m-%d")
        except ValueError:
            context["inv_date"] = True
            return render(request, template_name, context)
        form.save()
        return render(request, 'main/tables.html', view_data('RequestFeedback'))
    else:
        return render(request, template_name, context)

def displayReq(request):
    return render(request, 'main/tables.html', view_data('RequestFeedback'))

@mylogin_required
def home(request):
    result = RequestFeedback.objects.all()
    data = []
    for obj in result:
        course_data = []
        course_data.append(obj.course.name)
        course_data.append(obj.request_by.username)
        course_data.append(obj.start_date)
        course_data.append(obj.end_date)
        data.append(course_data)
    return render(request, 'main/home.html', {"data": data})

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
            row_data.append(getattr(each, field))  # Ignore PEP8Bear
        required_data.append(row_data)
    context['data'] = required_data
    context['fields'] = required_fields
    context['model_name'] = model_name
    return context


def displayStu(request):
    return render(request, 'main/tables.html', view_data('Student'))


def displayAdm(request):
    return render(request, 'main/tables.html', view_data('Admin'))


def displayPro(request):
    return render(request, 'main/tables.html', view_data('Professor'))


def check_csv(row, field_nr):
    row = [val.strip(' ') for val in row]
    context = dict()
    if len(row) != field_nr:
        context['err_msg'] = 'The csv file does not have required number of columns'
    elif not all(isinstance(val, str) for val in row):
        context['err_msg'] = 'The csv file contains unexpected data'
    elif any(val in (None, '', ' ') for val in row):
        context['err_msg'] = 'One of the fields seems to be empty'
    elif any(re.search(r'[^A-Za-z0-9_@.]+', val) for val in row):
        context['err_msg'] = 'One of the fields seems to have special characters'
    context['err_at'] = ', '.join(row)
    if 'err_msg' in context:
        return context
    else:
        return False


@mylogin_required
def addStudents(request):
    context = dict()
    if request.method=='POST':
            if not (request.FILES):
                return self.construct_form(request, True, False)
            f = TextIOWrapper(request.FILES['CSVFile'].file, encoding=request.encoding)
            reader = csv.reader(f.read().splitlines())
            for row in reader:
                context = check_csv(row, 2)
                if context!=False:
                    return render(request,'main/error.html',context)

                try:
                    user_instance = User.objects.create(username=row[0])
                    Student.objects.create(user=user_instance, rollno = row[1])

                except IntegrityError:
                    continue
            return render(request,'main/tables.html',view_data('Student'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Student'
        return render(request,'main/upload.html',context)

@mylogin_required
def addProfessor(request):
    context = dict()
    if request.method == 'POST':
        if not (request.FILES):
            return self.construct_form(request, True, False)
        f = TextIOWrapper(request.FILES['CSVFile'].file, encoding=request.encoding)
        reader = csv.reader(f.read().splitlines())
        for row in reader:
            context = check_csv(row, 2)
            if context != False:
                return render(request, 'main/error.html', context)

            try:
                user_instance = User.objects.create(username=row[1])
                Professor.objects.create(user=user_instance, fullname=row[0])
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('Professor'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Professor'
        return render(request, 'main/upload.html', context)


@mylogin_required
def addAdmin(request):
    context = dict()
    if request.method == 'POST':
        if not (request.FILES):
            return self.construct_form(request, True, False)
        f = TextIOWrapper(request.FILES['CSVFile'].file, encoding=request.encoding)
        reader = csv.reader(f.read().splitlines())
        for row in reader:
            context = check_csv(row, 1)
            if context != False:
                return render(request, 'main/error.html', context)

            try:
                user_instance = User.objects.create(username=row[0])
                Admin.objects.create(user=user_instance)
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('Admin'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Adminstrator'
        return render(request, 'main/upload.html', context)  # Ignore PEP8Bear

@mylogin_required
def viewFeedback(request, f_id):
    if request.method == 'GET':
        fdb_req= RequestFeedback.objects.filter(pk=f_id)
        if len(fdb_req) == 0:
            raise Http404
        else:
            fdb_req = fdb_req[0]
            course = fdb_req.course.name
            fdb = Feedback.objects.filter(fid = f_id)
            feedbacks = list()
            for f in fdb:
                feedbacks.append( [str(f.id), f.fid.request_by.__str__(), f.created_at.__str__()] )
            return render(request, 'main/view.html', {"feedbacks" :feedbacks, "course":course })

@mylogin_required
def showFeedback(request, f_id):
    if request.method == 'GET':
        feedbacks = Feedback.objects.filter(pk=f_id)
        if len(feedbacks) == 0:
            raise Http404
        else:
            feedback = json.loads(feedbacks[0].feedback)
            answers = [(x, feedback[x]) for x in feedback.keys()]
            return render(request, 'main/feedback.html', {"feedbacks" : answers, "fid" : f_id })

def serialize_datetime(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def authenticate_from_android(username=None, password=None):
    """
    Function for creating a token based auth system
    """
    try:
        student = Student.objects.get(user__username=username)
        if student.user.check_password(password):
            token = hashlib.sha256(
                ''.join(choice(ascii_uppercase) for i in range(20)).encode('utf-8'))
            student.auth_token = token.hexdigest()
            student.auth_token_expiry = datetime.datetime.now() + datetime.timedelta(days=2)
            student.save()
            user_object = {
                'username' : student.user.username,
                'rollno' : student.rollno,
                'auth_token' : student.auth_token,
                'auth_expiry' : serialize_datetime(student.auth_token_expiry)
            }
            return user_object, 'success'
        else:
            return None, 'wrongpassword'

    except Student.DoesNotExist:
        return None, 'userdoesntexist'

def validate_token_session(token, username):
    """
    Function for checking whether token based session is active
    """

    try:
        student = Student.objects.get(auth_token=token, user__username=username)
        curr_time = timezone.now()
        if curr_time < student.auth_token_expiry:
            return True, 'activesession', student
        else:
            return False, 'expiredsession', None
    except Student.DoesNotExist:
        return False, 'wrongtoken', None


def invalidate_token_session(token, username):
    """
    Function for checking whether token based session is active
    """

    try:
        student = Student.objects.get(auth_token=token, user__username=username)
        student.auth_token_expiry = datetime.datetime(
            1970, 1, 1, tzinfo=datetime.timezone.utc)
        student.save()
        return True, 'successfullogout'
    except Student.DoesNotExist:
        return False, 'wrongtoken'

@csrf_exempt
def requested_feedbacks(request):
    """
    Function to send the requested feedbacks to a student
    """

    if request.method == "POST":
        #get username and auth token
        username = request.POST.get('username')
        auth_token = request.POST.get('auth_token')

        #check if session is valid
        valid, message, sobject = validate_token_session(auth_token, username)

        if valid:
            courses = sobject.course_set.all()
            rqst_feedbacks = []
            for crs in courses:
                coursename = crs.name
                print(coursename)
                feedbacks = RequestFeedback.objects.filter(course=crs)
                for x in feedbacks:
                    rqst_feedbacks.append({
                        'rqst_id' : x.id,
                        'course_name' : coursename,
                        'requested_by' : x.request_by.username,
                        'start_date' : serialize_datetime(x.start_date),
                        'end_date' : serialize_datetime(x.end_date),
                    })

            response_object = {
                'message' : message,
                'requested_feedbacks' : rqst_feedbacks,
            }
            return JsonResponse(response_object)

        else:
            return JsonResponse({'message':message})

    else:
        return JsonResponse({'message':'wrong request'})


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
        user, message = authenticate_from_android(
            username=username, password=password)
        if user is not None:
            user['login_status'] = message
            return JsonResponse(user)
        else:
            return JsonResponse({'login_status':message})
    else:
        return JsonResponse({'login_status':'wrong request'})

@csrf_exempt
def mobile_logout(request):
    """
    Function for deauthentication of user from Android app
    """

    if request.method == "POST":
        # get username and auth token
        username = request.POST.get('username')
        auth_token = request.POST.get('auth_token')

        # invalidate the session
        loggedout, message = invalidate_token_session(auth_token, username)

        if loggedout:
            return JsonResponse({'message':message})

        else:
            return JsonResponse({'message':message})

    else:
        return JsonResponse({'message':'wrong request'})

@csrf_exempt
def check_session(request):
    """
    Function to check the validity of session
    """

    if request.method == "POST":
        #get username and auth token
        username = request.POST.get('username')
        auth_token = request.POST.get('auth_token')

        #check if session is valid
        loggedin, message, sobject = validate_token_session(auth_token, username)

        if loggedin:
            return JsonResponse({'message' : message})
        else:
            return JsonResponse({'message' : message})

    else:
        return JsonResponse({'message':'wrong request'})


@csrf_exempt
def receive_feedback(request):
    """
    Function for recieving feedback
    """

    if request.method == "POST":
        # get username, coursename, requestid and jsonfeedback
        username = request.POST.get('username')
        coursename = request.POST.get('course_name')

        auth_token = request.POST.get('auth_token')
        request_id = request.POST.get('rqst_id')
        json_feedback = request.POST.get('json_feedback')

        print(request_id, coursename)

        loggedin, message, sobject = validate_token_session(auth_token, username)

        if loggedin:
            try:
                print(coursename)
                course_object = Course.objects.get(name=coursename)
                request_object = RequestFeedback.objects.get(
                    id=int(request_id),
                    course=course_object)

                feedback_object, created = Feedback.objects.update_or_create(
                    student = sobject,
                    course = course_object,
                    fid = request_object,
                    feedback = json_feedback)

                if created:
                    return JsonResponse({'message':'submitted feedback'})
                else:
                    return JsonResponse(
                        {'message':'server side error in feedback submission'})

            except RequestFeedback.DoesNotExist:
                return JsonResponse({'message':'incorrect request object'})

            except Course.DoesNotExist:
                return JsonResponse({'message':'incorrect course object'})

        else:
            return JsonResponse({'message':message})

    else:
        return JsonResponse({'message':'wrong request'})
    
def extract_lang_properties(data):
    combined_operations = ['keyword', 'concept', 'doc-sentiment']
    alchemy_language = watson_developer_cloud.AlchemyLanguageV1(api_key='ddc135d16a20f8e4a6b04bba9e60e8fde322d49f')
    return alchemy_language.combined(text=data, extract=combined_operations)
