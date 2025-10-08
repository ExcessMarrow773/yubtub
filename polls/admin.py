from django.contrib import admin

from .models import Question, Choice

# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    pass

class ChoiceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)