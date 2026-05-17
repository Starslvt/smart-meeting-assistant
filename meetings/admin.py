from django.contrib import admin
from .models import Meeting
#Holaquetal
# Register your models here.


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status']