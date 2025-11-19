from rest_framework import permissions

class IsTaskTeamMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the task's team.
    """
    def has_object_permission(self, request, view, obj):
        return obj.team.memberships.filter(user=request.user).exists()


class IsTaskAssigneeOrAdmin(permissions.BasePermission):
    """
    Permission for task updates.
    - Admins can update everything
    - Members can only update tasks assigned to them
    """
    def has_object_permission(self, request, view, obj):
        membership = obj.team.memberships.filter(user=request.user).first()
        if not membership:
            return False
        if membership.role == 'admin':
            return True
        return obj.assigned_to == membership


class IsTeamAdmin(permissions.BasePermission):
    """
    Permission for task deletion.
    - Only team admins can delete tasks
    """
    def has_object_permission(self, request, view, obj):
        membership = obj.team.memberships.filter(user=request.user).first()
        if not membership:
            return False
        return membership.role == 'admin'