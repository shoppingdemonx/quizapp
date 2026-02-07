from django.contrib import admin
from .models import Profile,Question,Quiz,Result

# Register your models here.

admin.site.register(Profile)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Result)