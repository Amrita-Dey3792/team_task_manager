from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tasks.permissions import IsTaskTeamMember, IsTeamAdmin
from teams.models import Team, Membership
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to', 'due_date']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date']

    def get_queryset(self):
        return Task.objects.filter(team__memberships__user=self.request.user, is_deleted=False)
    
    @swagger_auto_schema(
        operation_summary="Create a new task",
        operation_description="Create a new task in a team. User must be a member of the team.",
        request_body=TaskSerializer,
        security=[{'Bearer': []}],
        responses={
            201: openapi.Response(
                description="Task created successfully",
                schema=TaskSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "User must be a team member"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="List tasks",
        operation_description="List all tasks in teams where the user is a member. Supports filtering by status, assigned_to, due_date and search by title/description.",
        security=[{'Bearer': []}],
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by task status", type=openapi.TYPE_STRING),
            openapi.Parameter('assigned_to', openapi.IN_QUERY, description="Filter by assigned membership ID", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
            openapi.Parameter('due_date', openapi.IN_QUERY, description="Filter by due date", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title and description", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (created_at, due_date)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="List of tasks",
                schema=TaskSerializer(many=True)
            ),
            401: "Authentication credentials were not provided"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve task details",
        operation_description="Get details of a specific task. User must be a team member.",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Task details",
                schema=TaskSerializer
            ),
            401: "Authentication credentials were not provided",
            404: "Task not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
    @swagger_auto_schema(
        operation_summary="Delete task",
        operation_description="Delete a task. Only team admins can delete tasks.",
        security=[{'Bearer': []}],
        responses={
            204: "Task deleted successfully",
            401: "Authentication credentials were not provided",
            403: "Only team admins can delete tasks",
            404: "Task not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        """
        Create task with proper validation:
        - Verify team exists
        - Verify user is a member of the team
        - assigned_to validation is already done by serializer.validate()
        """
        team = serializer.validated_data.get('team')
        
        if not team:
            raise ValidationError({"team": "This field is required."})
        
        try:
            membership = team.memberships.get(user=self.request.user)
        except Membership.DoesNotExist:
            raise PermissionDenied("You must be a member of the team to create tasks.")
        
        serializer.save(created_by=membership, team=team, assigned_to=None)

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsTeamAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsTaskTeamMember()]
        return [IsTaskTeamMember()]
    
    @swagger_auto_schema(
        operation_summary="Update task",
        operation_description="Update task details. Admins can update everything. Members can only update status and description.",
        request_body=TaskSerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=TaskSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Permission denied",
            404: "Task not found"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update task with field restrictions for members.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        membership = instance.team.memberships.filter(user=request.user).first()
        is_admin = membership and membership.role == 'admin'
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if not is_admin:
            allowed_fields = {'status', 'description'}
            provided_fields = set(request.data.keys())
            restricted_fields = provided_fields - allowed_fields
            
            if restricted_fields:
                raise ValidationError({
                    'detail': f'Members can only update status and description. Restricted fields: {", ".join(restricted_fields)}'
                })
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Partially update task",
        operation_description="Partially update task details. Admins can update everything. Members can only update status and description.",
        request_body=TaskSerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=TaskSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Permission denied",
            404: "Task not found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Handle partial update with field restrictions."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Assign task to a member",
        operation_description="Assign a task to a team member. Only team admins can assign tasks.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'assigned_to': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Membership ID (UUID) or user email of the team member to assign the task to'
                )
            },
            required=['assigned_to']
        ),
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Task assigned successfully",
                schema=TaskSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can assign tasks",
            404: "Task or membership not found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsTaskTeamMember])
    def assign(self, request, pk=None):
        """
        Assign task to a team member.
        Only team admins can assign tasks.
        """
        task = self.get_object()
        
        membership = task.team.memberships.filter(user=request.user).first()
        if not membership or membership.role != 'admin':
            raise PermissionDenied("Only team admins can assign tasks.")
        
        assigned_to_value = request.data.get('assigned_to')
        
        if not assigned_to_value:
            raise ValidationError({"assigned_to": "This field is required."})
        
        try:
            if '@' in str(assigned_to_value):
                assigned_membership = Membership.objects.get(
                    user__email=assigned_to_value,
                    team=task.team
                )
            else:
                assigned_membership = Membership.objects.get(
                    id=assigned_to_value,
                    team=task.team
                )
            
            if task.assigned_members.filter(id=assigned_membership.id).exists():
                raise ValidationError({
                    "assigned_to": f"User {assigned_membership.user.email} is already assigned to this task."
                })
            
            task.assigned_members.add(assigned_membership)
            task.save()
            
            from .models import ActivityLog
            ActivityLog.objects.create(
                action='task_assigned',
                performed_by=request.user,
                team=task.team,
                task=task,
                target_user=assigned_membership.user,
                details={'assigned_to': str(assigned_membership.user.id)}
            )
            
            serializer = self.get_serializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            raise ValidationError({
                "assigned_to": "Membership not found or does not belong to this team. Please provide a valid membership ID or user email."
            })
        except ValueError:
            raise ValidationError({
                "assigned_to": "Invalid format. Please provide a valid membership ID (UUID) or user email."
            })

