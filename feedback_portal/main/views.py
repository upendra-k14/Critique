import csv
import re
import pdb
import hashlib
import datetime
import json
import watson_developer_cloud

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
from django.urls import reverse

# Importing background task manager for analyzing feedback
from background_task import background

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

def permission_required(function):
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'admin'):
           return HttpResponseRedirect('/home')
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def index(request):
    if request.user.id:
         return HttpResponseRedirect('/home')
    return render(request, 'main/index.html', {})

def radar(request):

    return render(request, 'main/radar.html', {})

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
    return render(request,'main/tables.html',
        view_data('RequestFeedback', parent_view='displayReq'))

@mylogin_required
def home(request):
    context = dict()
    result = RequestFeedback.objects.filter(end_date__gte=datetime.datetime.today().date())
    context["students"] = len(Student.objects.all())
    context["courses"] = len(Course.objects.all())
    req_data = []
    submission_data = []
    submission_table = []
    total_pending = 0
    total_submitted = 0
    for obj in result:
        submitted = len(Feedback.objects.filter(fid=obj))
        pending = len(CourseStudent.objects.filter(course=obj.course)) - submitted
        total_submitted += submitted
        total_pending += pending
        name = obj.course.name
        fid = obj.id
        submission_data.append({
            "course": name,
            "submitted": submitted,
            "pending": pending,
        })
        submission_table.append([fid, name, submitted, pending])
        req_data.append([obj.course.name,obj.request_by.username, obj.start_date, obj.end_date])
    context["submission_table"] = submission_table
    context["submission_data"] = json.dumps(submission_data)
    context["req"] = len(req_data)
    context["req_data"] = req_data
    context["total_pending"] = json.dumps({"label":"Total pending feedback", "value":total_pending})
    context["total_submitted"] = json.dumps({"label": "Total submitted feedback", "value" : total_submitted})
    response_hist = []
    for i in range(1,8):
        date = (datetime.datetime.today() - datetime.timedelta(days=7-i)).date()
        fdb = Feedback.objects.filter(created_at__date = date)
        response_hist.append({
            "date":date.__str__(),
            "submissions": len(fdb)
        })
    context["sub_today"] = len(fdb)
    context["response_hist"] = json.dumps(response_hist)

    return render(request, 'main/home.html', context)

def view_data(model_name, **kwargs):
    if 'parent_view' in kwargs:
        if kwargs['parent_view'] == 'displayReq':
            context = dict()
            model = eval(model_name)
            field_names = model._meta.get_fields()
            required_fields = list()
            unimp_fields = []
            if 'fields' in kwargs:
                unimp_fields = kwargs.pop('fields')
            for field in field_names:
                if not field.auto_created and str(field).split('.')[-1] not in unimp_fields:
                    required_fields.append(field)
            data = model.objects.all()
            required_data = list()
            for each in data:
                row_data = list()
                for field in required_fields:
                    if field.name == "course":
                        row_data.append("""<a href="{}">{}</a>""".format(
                            reverse('viewFeedback', args=[each.id]),
                            getattr(each, field.name)))
                    else:
                        row_data.append(getattr(each, field.name))  # Ignore PEP8Bear
                if datetime.date.today() - each.end_date >= datetime.timedelta(days=1):
                    row_data.append("""<a href="{}">{}</a>""".format(
                        "#",
                        "<i class='fa fa-bar-chart-o fw'></i> <span>&nbsp</span> <span style='color:green'>Completed</span>"
                    ))
                else:
                    row_data.append("""<a href="{}">{}</a>""".format(
                        "#",
                        "<i class='fa fa-clock-o fw'></i> <span>&nbsp</span> <span style='color:red'>Pending</span>"
                    ))
                required_data.append(row_data)
            context['data'] = required_data
            context['fields'] = [f.verbose_name for f in required_fields]
            context['fields'].append('Visualize')
            context['model_name'] = model_name
            return context
    else:
        context = dict()
        model = eval(model_name)
        field_names = model._meta.get_fields()
        required_fields = list()
        unimp_fields = []
        if 'fields' in kwargs:
            unimp_fields = kwargs.pop('fields')
        for field in field_names:
            if not field.auto_created and str(field).split('.')[-1] not in unimp_fields:
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
    return render(request, 'main/tables.html', view_data('Student', fields=['auth_token', 'auth_token_expiry']))


def displayAdm(request):
    return render(request, 'main/tables.html', view_data('Admin'))


def displayPro(request):
    return render(request, 'main/tables.html', view_data('Professor'))

def displayCourse(request):
    return render(request, 'main/tables.html', view_data('Course', fields=['student', 'professor']))

def displayCourseStudent(request):
    return render(request, 'main/tables.html', view_data('CourseStudent'))

def displayCourseProfessor(request):
    return render(request, 'main/tables.html', view_data('CourseProfessor'))


def check_csv(row, field_nr):
    row = [val.strip(' ') for val in row]
    context = dict()
    if len(row) != field_nr:
        context['err_msg'] = 'The csv file does not have required number of columns'
    elif not all(isinstance(val, str) for val in row):
        context['err_msg'] = 'The csv file contains unexpected data'
    elif any(val in (None, '', ' ') for val in row):
        context['err_msg'] = 'One of the fields seems to be empty'
    elif any(re.search(r'[^A-Za-z0-9_@. -]+', val) for val in row):
        context['err_msg'] = 'One of the fields seems to have special characters'
    context['err_at'] = ', '.join(row)
    if 'err_msg' in context:
        return context
    else:
        return False


@mylogin_required
@permission_required
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
                    user_instance = User.objects.create_user(username=row[0], password='iiits@123')
                    Student.objects.create(user=user_instance, rollno = row[1])

                except IntegrityError:
                    continue
            return render(request,'main/tables.html',view_data('Student', fields=['auth_token', 'auth_token_expiry']))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Student'
        return render(request,'main/upload.html',context)

@mylogin_required
@permission_required
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
                user_instance = User.objects.create_user(username=row[1], password='iiits@123')
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
@permission_required
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
                user_instance = User.objects.create_user(username=row[0], password='iiits@123')
                Admin.objects.create(user=user_instance)
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('Admin'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Adminstrator'
        return render(request, 'main/upload.html', context)

@mylogin_required
@permission_required
def addCourse(request):
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
                Course.objects.create(name=row[0])
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('Course', fields=['professor', 'student']))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Course'
        return render(request, 'main/upload.html', context)

@mylogin_required
@permission_required
def addCourseStudent(request):
    context = dict()
    if request.method == 'POST':
        if not (request.FILES):
            return self.construct_form(request, True, False)
        f = TextIOWrapper(request.FILES['CSVFile'].file, encoding=request.encoding)
        reader = csv.reader(f.read().splitlines())
        for row in reader:
            try:
                student= Student.objects.filter(user__username=row[0])[0]
                for each in row[1:]:
                    if each!='':
                        course = Course.objects.filter(name=each)[0]
                        CourseStudent.objects.create(course=course, student=student)
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('CourseStudent'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Course'
        return render(request, 'main/upload.html', context)

@mylogin_required
@permission_required
def addCourseProfessor(request):
    context = dict()
    if request.method == 'POST':
        if not (request.FILES):
            return self.construct_form(request, True, False)
        f = TextIOWrapper(request.FILES['CSVFile'].file, encoding=request.encoding)
        reader = csv.reader(f.read().splitlines())
        for row in reader:
            try:
                prof = Professor.objects.filter(fullname=row[0])[0]
                # prof = Professor.objects.filter(user__username=row[0])[0]
                for each in row[1:]:
                    if each!='':
                        course = Course.objects.filter(name=each)[0]
                        CourseProfessor.objects.create(course=course, professor=prof)
            except IntegrityError:
                continue
        return render(request, 'main/tables.html', view_data('CourseProfessor'))
    else:
        form = FileForm()
        context['form'] = form
        context['name'] = 'Course Professor relations'
        return render(request, 'main/upload.html', context)

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

def visualiseFeedback(request, f_id):
    if request.method == "GET":
        req_object_list = RequestFeedback.objects.filter(id=f_id)
        if len(req_object)==0:
            raise Http404
        else:
            requested_fobject = req_object_list[0]
            feedbacks = Feedback.objects.filter(fid=requested_fobject)
            responses = [json.loads(feedback.feedback) for feedback in feedbacks]
            data = {}
            return render(request, 'main/visualize.html', context=data)

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
                    feedback = json_feedback,
                    analyzed_text = "\{\}")
                feed_id = feedback_object.id
                if created:
                    # Run a background task when feedback is recieved
                    print("created..getting text")
                    #get_analyzed_text((request_object.id,1))
                    f_object = Feedback.objects.get(id=feed_id)
                    if f_object!=None:
                        key_text = "Anything else you care to share or get off your chest?"
                        print(f_object)
                        feedback_text = json.loads(f_object.feedback)[key_text]
                        print(feedback_text)
                        analyzed_text = extract_lang_properties(feedback_text)
                        print(analyzed_text)
                        if analyzed_text != None:
                            f_object.analyzed_text = analyzed_text
                            f_object.is_analyzed = True
                            f_object.save()
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
    try:
        alchemy_language = watson_developer_cloud.AlchemyLanguageV1(api_key='b373f7d8d360b566822a018ad5b048a19bc9d1c9')
        return alchemy_language.combined(text=data, extract=combined_operations)
    except:
        return None

# @background(schedule=0)
# def get_analyzed_text(args):
#     request_id = args[0]
#     print(request_id)
#     counter = args[1]
#     print(counter)
#     response_feedback_object = Feedback.objects.filter(fid__id=request_id)
#     print(len(response_feedback_object))
#     if response_feedback_object!=None:
#         key_text = "Anything else you care to share or get off your chest?"
#         f_object = response_feedback_object[0]
#         print(f_object)
#         feedback_text = f_object.feedback[key_text]
#         print(feedback_text)
#         analyzed_text = extract_lang_properties(feedback_text)
#         print(analyzed_text)
#         if analyzed_text != None:
#             f_object.analyzed_text = analyzed_text
#             f_object.is_analyzed = True
#             f_object.save()
#         else:
#             if counter<6:
#                 get_analyzed_text((request_id, counter+1), schedule=timedelta(days=1))

@csrf_exempt
def mobile_changee_password(request):
    if request.method == 'POST':
        # get username and password
        username = request.POST.get('username')
        password = request.POST.get('oldpass')
        newpassword = request.POST.get('newpass')
        # authenticate user
        print(username, password, newpassword)
        try:
            student = Student.objects.get(user__username=username)
            if student.user.check_password(password):
                student.user.set_password(newpassword)
                student.user.save()
                return JsonResponse({'message':'success'})
            else:
                return JsonResponse({'message':'Incorrect'})

        except Student.DoesNotExist:
            return None, 'userdoesntexist'
