from django.contrib import admin
from .models import Team, Membership


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at']
    list_filter = ['created_at', 'company']
    search_fields = ['name', 'company__name']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'company')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'user__name', 'team__name']
    readonly_fields = ['id', 'joined_at']
    date_hierarchy = 'joined_at'
    
    fieldsets = (
        ('Membership Information', {
            'fields': ('id', 'user', 'team', 'role')
        }),
        ('Metadata', {
            'fields': ('joined_at',)
        }),
    )
