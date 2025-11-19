from rest_framework import permissions

class IsTaskTeamMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.team.memberships.filter(user=request.user).exists()


class IsTaskAssigneeOrAdmin(permissions.BasePermission):
   
    def has_object_permission(self, request, view, obj):
        membership = obj.team.memberships.filter(user=request.user).first()
        if not membership:
            return False
        if membership.role == 'admin':
            return True
        return obj.assigned_to == membership


class IsTeamAdmin(permissions.BasePermission):
   
    def has_object_permission(self, request, view, obj):
        membership = obj.team.memberships.filter(user=request.user).first()
        if not membership:
            return False
        return membership.role == 'admin'