from __future__ import unicode_literals

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

class FileUpload(models.Model):
    CSVFile = models.FileField()

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(
        User,
        primary_key=True,
        on_delete= models.CASCADE)
    rollno = models.CharField(
        unique=True,
        max_length=11,
        verbose_name="Roll No")
    auth_token = models.CharField(default='notoken', max_length=256)
    auth_token_expiry = models.DateTimeField(
        default=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))

    def save(self, *args, **kwargs):
        saved_user = User.objects.get(username = self.user.username)
        saved_user.is_active= False
        saved_user.save()
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Students'


class Professor(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete= models.CASCADE)
    fullname = models.CharField(max_length=100, default = 'FULLNAME', verbose_name="Full Name")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Professors'

class Admin(models.Model):
    user = models.OneToOneField( User, primary_key=True, on_delete= models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Feedback Portal Admins'

class Course(models.Model):
    """
    Each course has many users and many tasks.
    """
    name = models.CharField(max_length=128, unique=True, verbose_name="Course Name")
    student = models.ManyToManyField(Student, through='CourseStudent')
    professor = models.ManyToManyField(Professor, through='CourseProfessor')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Courses'

class CourseProfessor(models.Model):
    """
    Many to many relation between Course and Professor
    """
    course = models.ForeignKey(Course)
    professor = models.ForeignKey(Professor)

    def __str__(self):
        return self.professor.fullname+'-'+self.course.name

    class Meta:
        verbose_name_plural = 'Course Professors'
        unique_together = ('course','professor')

class CourseStudent(models.Model):
    """
    Many to many relation between Course and User
    """
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student)

    def __str__(self):
        string = self.course.name
        string+= ' - '
        string+= self.student.user.username
        return string

    class Meta:
        verbose_name_plural = 'Course Students'
        unique_together = ('course','student')

class RequestFeedback(models.Model):
    course = models.ForeignKey(
        Course, verbose_name="Course Name")
    request_by = models.ForeignKey(
        User, verbose_name="Requested By")
    start_date = models.DateField(
        default= datetime.date.today(), verbose_name="Start Date")
    end_date = models.DateField(
        default= datetime.date.today() + datetime.timedelta(days=10), verbose_name="End Date")

    def __str__(self):
        return self.course.name

    class Meta:
        verbose_name_plural = 'Feedback Requisition Table'


class Feedback(models.Model):
    """
    Stores the feedback content of student, on overall course.
    Every task corresponds to a single course and a single
    student.
    """
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)
    #coursestudent = models.ForeignKey(CourseStudent)
    fid = models.ForeignKey(RequestFeedback)
    feedback = JSONField()
    analyzed_text = JSONField()
    is_analyzed = models.BooleanField(default=False)
    created_at = models.DateTimeField( auto_now_add = True, blank = True)

    def __str__(self):
        return self.student.user.username

    class Meta:
        verbose_name_plural = 'Feedback Responses'
