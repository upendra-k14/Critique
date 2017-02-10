from django.test import TestCase, Client
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Student, Admin, Professor
from django.contrib.auth import authenticate, login

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

    def test_addStudents(self):
        response = self.client.post('/addStudents/',{'CSVFile':SimpleUploadedFile('test.csv', 'b,c\n,d,e,f')})
        self.assertEqual(response.status_code, 200)

    def test_viewAdmin(self):
        response = self.client.post('/addAdmin/',{'CSVFile':SimpleUploadedFile('test.csv', 'b\n,d')})
        self.assertEqual(response.status_code, 200)

    def test_viewPro(self):
        response = self.client.post('/addProfessor/',{'CSVFile':SimpleUploadedFile('test.csv', 'b\n,d')})
        self.assertEqual(response.status_code, 200)
