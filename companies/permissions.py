from rest_framework.permissions import BasePermission


class IsCompanyOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.created_by == request.user