from django.test import TestCase
from django.contrib.auth.models import User
from .models import Student, Admin, Professor
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.test import Client

class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('student', 'student@gmail.com', 'student.password')
        Student.objects.create(user= User.objects.get(username = 'student'),
                               rollno='IS201401001')

        User.objects.create_user('admin', 'admin@gmail.com', 'admin.password')
        Admin.objects.create(user= User.objects.get(username = 'admin'))

        User.objects.create_user('professor', 'professor@gmail.com', 'professor.password')
        Professor.objects.create(user= User.objects.get(username = 'professor'))

        self.client = Client()

    def test_invalid_username(self):
        user = authenticate(username = 'Invalidname', password = 'student.password')
        self.assertFalse(user is not None)

        user = authenticate(username = 'STUDENT', password = 'student.password')
        self.assertFalse(user is not None)

        user = authenticate(username = 'stdent', password = 'student.password')
        self.assertFalse(user is not None)


    def test_invalid_password(self):
        user = authenticate(username = 'student', password = '12345678')
        self.assertFalse(user is not None)

        user = authenticate(username = 'student', password = 'student.Password')
        self.assertFalse(user is not None)

        user = authenticate(username = 'student', password = 'studentPassword')
        self.assertFalse(user is not None)

    def test_invalid_username_password(self):
        user = authenticate(username = 'student',password = 'student.password')
        self.assertFalse(user is not None)

    def test_valid_username_password(self):
        user = authenticate(username = 'admin',password = 'admin.password')
        self.assertTrue(user is not None)

        user = authenticate(username = 'professor',password = 'professor.password')
        self.assertTrue(user is not None)

    def test_login_reponse(self):
        response = self.client.post('/login/',{'username': 'UserName', 'password': 'Password'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        self.assertFalse(self.client.login(username='student', password='student.password'))

    def test_valid_login(self):
        self.assertTrue(self.client.login(username='admin', password='admin.password'))

        self.assertTrue(self.client.login(username='professor', password='professor.password'))
