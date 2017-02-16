from django.test import TestCase, Client
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Student, Admin, Professor
from django.contrib.auth import authenticate, login
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
        response = self.client.get('/viewProf/')
        self.assertEqual(response.status_code, 200)

class AddTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('admin', 'admin@gmail.com', 'admin.password')
        Admin.objects.create(user= User.objects.get(username = 'admin'))
        self.client.login(username = 'admin', password = 'admin.password')

    def test_addStudents_missing_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'b,c\nd,e,f')})
        template_name = 'main/error.html'
        context = {'err_at':'b, c','err_msg':'The csv file does not have required number of columns'}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context['err_msg'])
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_empty_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'b,c,d\nd,e,')})
        template_name = 'main/error.html'
        context = {'err_at':'d,e,','err_msg':'One of the fields seems to be empty'}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context['err_msg'])
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_empty_fields(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'b,c,d\nd,e,er@#@#!@#\n')})
        template_name = 'main/error.html'
        context = {'err_at':'d, e, er@#@#!@#','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context['err_msg'])
        self.assertEqual(response.context['err_msg'], context['err_msg'])
        self.assertEqual(response.context['err_at'], context['err_at'])
        self.assertTemplateUsed(response, template_name)

    def test_addStudents_valid_example(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'stu1,stu1@iiits.in,is12\nstu2,stu2@iiits.in,is22\n')})
        template_name = 'main/view.html'
        context = {'model_name':'Students','err_msg':'One of the fields seems to have special characters'}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context['Students'])
        ### assert other context items as well
        self.assertTemplateUsed(response, template_name)

    # add testcase to handle if no file is uploaded but upload button clicked, also add check for it views.py
    #repeat the same for admin and professor as well
    def test_viewAdmin(self):
        response = self.client.post('/addAdmin/',{'CSVFile':SimpleUploadedFile('test.csv', 'b\n,d')})
        self.assertEqual(response.status_code, 200)

    def test_viewPro(self):
        response = self.client.post('/addProfessor/',{'CSVFile':SimpleUploadedFile('test.csv', 'b\n,d')})
        self.assertEqual(response.status_code, 200)
