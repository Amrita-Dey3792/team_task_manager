from rest_framework import permissions

class IsTeamMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user).exists()


class IsTeamAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user, role='admin').exists()


class IsTeamAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.memberships.filter(user=request.user).exists()
        
        return obj.memberships.filter(user=request.user, role='admin').exists()