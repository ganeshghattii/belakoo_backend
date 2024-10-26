from django.contrib import admin
from .models import Campus, Subject, Grade, Proficiency, Lesson

admin.site.register(Campus)
admin.site.register(Subject)
admin.site.register(Grade)
admin.site.register(Proficiency)
admin.site.register(Lesson)