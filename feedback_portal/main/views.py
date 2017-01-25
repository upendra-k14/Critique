from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf

from .forms import UserForm


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
# index : Function generates the basic index page of the application.
# The index page displays ad introduction about the website/project
# Users are given the option to LogIn or SignUp. The page does not perform any functions other than linking the login and registration pages
# There is no need to be logged in to access the index page.
def index(request):
    context = dict()
    return render(request, 'main/index.html', context)

# ----------------------------------------------------------------------------------------
# register: Generates the page for a new user to register.
# Required fields for registration are: <username> <email> <password> [<confirm password>]
# Password field has certain restrictions that are displayed on the registration page
# If the user registration is correct it redirects the user to a confirmation page.
# Does not log in the user after registration process is complete. User must log in after registration.
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
