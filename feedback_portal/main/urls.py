from django.conf.urls import url
from . import views
import django.contrib.auth.views as auth_views

urlpatterns = [
    # Basic index page for the application
    url(r'^$', views.index , name='index'),
    #Page to register a new user
    url(r'^register/$', views.register, name='register'),
    # Login page
    url(r'^login/$', auth_views.login,{'template_name': 'main/login.html'}, name='login'),
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

]
