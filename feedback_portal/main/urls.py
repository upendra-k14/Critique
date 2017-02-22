from django.conf.urls import url
from . import views
import django.contrib.auth.views as auth_views
from django.contrib.auth.decorators import user_passes_test

login_forbidden =  user_passes_test(lambda u: u.is_anonymous(), '/home/')

urlpatterns = [
    # Basic index page for the application
    url(r'^$', views.index , name='index'),
    # Login page
    url(r'^login/$', login_forbidden(auth_views.login),{'template_name': 'main/login.html'}, name='login'),
    # Logout URL, redirects to index
    url(r'^logout/$', auth_views.logout,{'template_name': 'main/index.html'}, name='logout'),
    # Page to change password
    url(r'^passwordchange/$', views.mylogin_required(auth_views.password_change),{'template_name': 'main/pchange.html'}, name='password_change'),
    # Page to give success response of change
    url(r'^changedone/$', views.mylogin_required(auth_views.password_change_done),{'template_name': 'main/pdone.html'}, name='password_change_done'),

    url(r'^addStudents/$', views.addStudents, name='addStudents'),

    url(r'^addAdmin/$', views.addAdmin, name='addAdmin'),

    url(r'^addProfessor/$', views.addProfessor, name='addProfessor'),

    url(r'^home/$', views.home, name='home'),

    url(r'viewStudents/$', views.displayStu, name='home'),

    url(r'^viewAdmin/$', views.displayAdm, name='home'),

    url(r'^viewProf/$', views.displayPro, name='home'),

]
