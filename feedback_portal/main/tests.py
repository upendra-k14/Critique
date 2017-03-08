from django.test import TestCase, Client
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Admin
from .models import Professor
from .models import Student
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import render

class ViewTestCase(TestCase):
    def setUp(self):

        self.client = Client()

    def test_viewStudents(self):
        response = self.client.get('/viewStudents/')
        self.assertEqual(response.status_code, 200)

    def test_viewAdmin(self):
        response = self.client.get('/viewAdmin/')
        self.assertEqual(response.status_code, 200)

    def test_viewPro(self):
        response = self.client.get('/viewProfessor/')
        self.assertEqual(response.status_code, 200)

class AddStudentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('admin', 'admin@gmail.com', 'admin.password')
        Admin.objects.create(user= User.objects.get(username = 'admin'))
        self.client.login(username = 'admin', password = 'admin.password')

    def test_addStudents_missing_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email\nemail1@email,12345')})
        template_name = 'main/error.html'
        context = {'err_at':'email@email','err_msg':'The csv file does not have required number of columns'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_empty_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email,\nemail1@email,12345')})
        template_name = 'main/error.html'
        context = {'err_at':'email@email, ','err_msg':'One of the fields seems to be empty'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_spclcharacter_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email,12345\nemail1@email,12!#$#$')})
        template_name = 'main/error.html'
        context = {'err_at':'email1@email, 12!#$#$','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_valid_example(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'stu1@iiits.in,is12\nstu2@iiits.in,is22\n')})
        template_name = 'main/tables.html'
        #context = {'model_name':'Students','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student')
        ### assert other context items as well
        self.assertTemplateUsed(response, template_name)

class AddAdminTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('admin', 'admin@gmail.com', 'admin.password')
        Admin.objects.create(user= User.objects.get(username = 'admin'))
        self.client.login(username = 'admin', password = 'admin.password')

    def test_addAdmin_empty_fields(self):
        response = self.client.post('/addAdmin/',{'CSVFile':SimpleUploadedFile('test.csv', '\nemail@email\n')})
        template_name = 'main/error.html'
        context = {'err_at':'','err_msg':'The csv file does not have required number of columns'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addAdmin_spclcharacter_fields(self):
        response = self.client.post('/addAdmin/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email\ner@#@#!@#@email')})
        template_name = 'main/error.html'
        context = {'err_at':'er@#@#!@#@email','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addAdmin_valid_example(self):
        response = self.client.post('/addAdmin/',{'CSVFile':SimpleUploadedFile('test.csv', 'adm1@iiits.in\nadm2@iiits.in\n')})
        template_name = 'main/tables.html'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        ### assert other context items as well
        self.assertTemplateUsed(response, template_name)

class AddProfessorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('admin', 'admin@gmail.com', 'admin.password')
        Admin.objects.create(user= User.objects.get(username = 'admin'))
        self.client.login(username = 'admin', password = 'admin.password')

    def test_addProfessor_empty_fields(self):
        response = self.client.post('/addProfessor/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email,\nemail1@email1,name')})
        template_name = 'main/error.html'
        context = {'err_at':'email@email, ','err_msg':'One of the fields seems to be empty'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addProfessor_spclcharacter_fields(self):
        response = self.client.post('/addProfessor/',{'CSVFile':SimpleUploadedFile('test.csv', 'email@email,name\ner@#@#!@#@email,name1')})
        template_name = 'main/error.html'
        context = {'err_at':'er@#@#!@#@email, name1','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addProfessor_valid_example(self):
        response = self.client.post('/addProfessor/',{'CSVFile':SimpleUploadedFile('test.csv', 'prof1@iiits.in,prof1\nprof2@iiits.in,prof2\n')})
        template_name = 'main/tables.html'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Professor')
        ### assert other context items as well
        self.assertTemplateUsed(response, template_name)
