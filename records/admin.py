from django.contrib import admin
from .models import StudentRecord   # 👈 IMPORTANT

@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'course', 'email', 'mobile', 'response_date')
    search_fields = ('first_name', 'last_name', 'email', 'mobile', 'course')
    list_filter = ('course', 'response_type', 'is_in_ndn_list')
