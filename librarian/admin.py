from django.contrib import admin
from .models import QuestionPaper

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('subject', 'semester', 'department', 'uploaded_at')
    list_filter = ('department', 'semester', 'subject')
    search_fields = ('subject',)