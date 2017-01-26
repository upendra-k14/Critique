from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    rollno = models.CharField(unique=True, max_length=11)
    def __str__(self):
        return self.user.username

class Professor(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    def __str__(self):
        return self.user.username

class Admin(models.Model):
    user = models.OneToOneField( User, primary_key=True)
    def __str__(self):
	return self.user.username

class Course(models.Model):
    """
    Each course has many users and many tasks.
    """
    name = models.CharField(max_length=128)
    student = models.ManyToManyField(Student, through='CourseStudent')
    professor = models.ManyToManyField(Professor, through='CourseProfessor')

    def __str__(self):
        return self.name

class CourseProfessor(models.Model):
    """
    Many to many relation between Course and Professor
    """
    course = models.ForeignKey(Course)
    professor = models.ForeignKey(Professor)

    def __str__(self):
        return self.professor.user.username

class CourseStudent(models.Model):
    """
    Many to many relation between Course and User
    """
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student)

    def __str__(self):
        string = self.course.name
        string+= " - "
        string+= self.student.user.username
        return string

class RequestFeedback(models.Model):
    course = models.ForeignKey(Course)
    request_by = models.ForeignKey(User)

    def __str__(self):
        return self.fid

class Feedback(models.Model):
    """
    Stores the feedback content of student, on overall course.
    Every task corresponds to a single course and a single
    student.
    """
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)
    coursestudent = models.ForeignKey(CourseStudent)
    fid = models.ForeignKey(RequestFeedback)
    feedback = JSONField()
    created_at = models.DateTimeField( auto_now_add = True, blank = True)

    def __str__(self):
        return self.student.user.username
