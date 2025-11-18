from rest_framework import permissions

class IsTeamAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user, role='admin').exists()

class IsTeamMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user).exists()