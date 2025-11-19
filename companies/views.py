from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Company
from .serializers import CompanySerializer
from .permissions import IsCompanyOwner


class CompanyPagination(PageNumberPagination):
    """
    Custom pagination class that supports page_size query parameter.
    Usage: ?page=1&page_size=20
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company CRUD operations.
    
    Requirements:
    - Create company: Authenticated user becomes owner
    - List companies: Shows companies where user is owner or team member
    - Update/Delete: Only company owners can modify/delete
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = CompanyPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    # Set default permission to allow create action
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Permission configuration:
        - Create: Requires authentication (user becomes owner)
        - List/Retrieve/Update/Delete: Requires authentication + ownership check for modifications
        """
        # For create action, only authentication is needed
        if self.action == 'create':
            return [IsAuthenticated()]
        # For other actions (list, retrieve, update, delete), use IsCompanyOwner
        # which handles both authentication and ownership checks
        return [IsCompanyOwner()]

    def get_queryset(self):
        """
        Filter companies to show only:
        1. Companies owned by the user
        2. Companies where user is a member of at least one team
        """
        user = self.request.user
        
        return Company.objects.filter(
            Q(created_by=user) |                         
            Q(teams__memberships__user=user)             
        ).distinct()

    @swagger_auto_schema(
        operation_summary="Create a new company",
        operation_description="Create a new company. The authenticated user automatically becomes the owner.",
        request_body=CompanySerializer,
        security=[{'Bearer': []}],
        responses={
            201: openapi.Response(
                description="Company created successfully",
                schema=CompanySerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="List companies",
        operation_description="List all companies where the user is owner or team member",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="List of companies",
                schema=CompanySerializer(many=True)
            ),
            401: "Authentication credentials were not provided"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve company details",
        operation_description="Get details of a specific company. User must be owner or team member.",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Company details",
                schema=CompanySerializer
            ),
            401: "Authentication credentials were not provided",
            404: "Company not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update company",
        operation_description="Update company details. Only company owners can update.",
        request_body=CompanySerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Company updated successfully",
                schema=CompanySerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only company owners can update",
            404: "Company not found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update company",
        operation_description="Partially update company details. Only company owners can update.",
        request_body=CompanySerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Company updated successfully",
                schema=CompanySerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only company owners can update",
            404: "Company not found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete company",
        operation_description="Delete a company. Only company owners can delete.",
        security=[{'Bearer': []}],
        responses={
            204: "Company deleted successfully",
            401: "Authentication credentials were not provided",
            403: "Only company owners can delete",
            404: "Company not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create company and set the authenticated user as owner.
        """
        serializer.save(created_by=self.request.user)