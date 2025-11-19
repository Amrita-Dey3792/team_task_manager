from django.contrib import admin
from .models import Task, ActivityLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'status', 'created_by', 'due_date', 'is_deleted', 'created_at']
    list_filter = ['status', 'is_deleted', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'team__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    filter_horizontal = ['assigned_members']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'status', 'due_date')
        }),
        ('Relations', {
            'fields': ('team', 'created_by', 'assigned_to', 'assigned_members')
        }),
        ('Metadata', {
            'fields': ('is_deleted', 'deleted_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'performed_by', 'team', 'task', 'target_user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['performed_by__email', 'team__name', 'task__title']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('action', 'performed_by', 'timestamp')
        }),
        ('Related Objects', {
            'fields': ('team', 'task', 'target_user')
        }),
        ('Details', {
            'fields': ('details',)
        }),
    )
