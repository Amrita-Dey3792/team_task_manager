from rest_framework.permissions import BasePermission

class IsCompanyOwner(BasePermission):
    
    def has_permission(self, request, view):

        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        if request.method in ['PATCH', 'PUT', 'DELETE']:
            return obj.created_by == request.user
        
        return False