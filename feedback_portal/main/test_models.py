from django.test import TestCase
from django.contrib.auth.models import User
from .models import *

class StudentModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(Student._meta.verbose_name_plural), 'Students')


class ProfessorModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(Professor._meta.verbose_name_plural), 'Professors')


class AdminModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(Admin._meta.verbose_name_plural), 'Feedback Portal Admins')


class CourseModelTest(TestCase):
    """
    Test Student model
    """

    def test_string_representation(self):
        course = Course(name='ITS')
        self.assertEqual(str(course), course.name)


    def test_verbose_name_plural(self):
        self.assertEqual(str(Course._meta.verbose_name_plural), 'Courses')


class CourseProfessorModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(CourseProfessor._meta.verbose_name_plural), 'Course Professors')


class CourseStudentModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(CourseStudent._meta.verbose_name_plural), 'Course Students')


class RequestFeedbackModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(RequestFeedback._meta.verbose_name_plural), 'Feedback Requisition Table')


class FeedbackModelTest(TestCase):
    """
    Test Student model
    """

    def test_verbose_name_plural(self):
        self.assertEqual(str(Feedback._meta.verbose_name_plural), 'Feedback Responses')
