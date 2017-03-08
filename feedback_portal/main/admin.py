from django.contrib import admin
from main.models import ( Student,
                          Professor,
                          Admin,
                          Course,
              Feedback,
              CourseStudent,
              CourseProfessor,
              RequestFeedback)


# Register your models here.
admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Course)
admin.site.register(Feedback)
admin.site.register(Admin)
admin.site.register(CourseStudent)
admin.site.register(CourseProfessor)
admin.site.register(RequestFeedback)
