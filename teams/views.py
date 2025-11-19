from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
from users.models import User
from companies.models import Company
from .models import Team, Membership
from .serializers import TeamSerializer, MembershipSerializer
from .permissions import IsTeamAdmin, IsTeamMember


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsTeamMember]

    def get_queryset(self):
        return Team.objects.filter(memberships__user=self.request.user).distinct()

    @swagger_auto_schema(
        operation_summary="Create a new team",
        operation_description="Create a new team under a company. User must own the company. Creator becomes team admin.",
        request_body=TeamSerializer,
        security=[{'Bearer': []}],
        responses={
            201: openapi.Response(
                description="Team created successfully",
                schema=TeamSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "You can only create teams in your own company"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="List teams",
        operation_description="List all teams where the user is a member",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="List of teams",
                schema=TeamSerializer(many=True)
            ),
            401: "Authentication credentials were not provided"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve team details",
        operation_description="Get details of a specific team. User must be a team member.",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Team details",
                schema=TeamSerializer
            ),
            401: "Authentication credentials were not provided",
            404: "Team not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update team",
        operation_description="Update team details. Only team admins can update.",
        request_body=TeamSerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Team updated successfully",
                schema=TeamSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can update",
            404: "Team not found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update team",
        operation_description="Partially update team details. Only team admins can update.",
        request_body=TeamSerializer,
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Team updated successfully",
                schema=TeamSerializer
            ),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can update",
            404: "Team not found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete team",
        operation_description="Delete a team. Only team admins can delete.",
        security=[{'Bearer': []}],
        responses={
            204: "Team deleted successfully",
            401: "Authentication credentials were not provided",
            403: "Only team admin can delete the team",
            404: "Team not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        # The serializer will handle company validation and creation
        # We just need to save the team and create the membership
        team = serializer.save()
        
        # Create membership for the creator as admin
        Membership.objects.create(user=self.request.user, team=team, role='admin')


    @swagger_auto_schema(
        operation_summary="Add member to team",
        operation_description="Add a user to the team. Only team admins can add members.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID to add'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'member'], default='member', description='Role for the member')
            },
            required=['user_id']
        ),
        security=[{'Bearer': []}],
        responses={
            201: openapi.Response(description="Member added successfully", schema=MembershipSerializer),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can add members",
            404: "User or team not found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeamAdmin])
    @transaction.atomic
    def add_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')

        if role not in ['admin', 'member']:
            raise ValidationError({"role": "Role must be 'admin' or 'member'"})

        user = get_object_or_404(User, id=user_id)

        if team.memberships.filter(user=user).exists():
            return Response(
                {"detail": f"User {user.email} is already in the team."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership = Membership.objects.create(user=user, team=team, role=role)
        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Remove member from team",
        operation_description="Remove a user from the team. Only team admins can remove members.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID to remove')
            },
            required=['user_id']
        ),
        security=[{'Bearer': []}],
        responses={
            204: "Member removed successfully",
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can remove members",
            404: "User or team not found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeamAdmin])
    @transaction.atomic
    def remove_member(self, request, pk=None):
        
        team = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            raise ValidationError({"user_id": "This field is required."})

        # Get the user - same approach as add_member
        user = get_object_or_404(User, id=user_id)

        # Check if user is trying to remove themselves
        if user.id == request.user.id:
            return Response(
                {"detail": "You cannot remove yourself from the team. Transfer ownership first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the membership - use same pattern as add_member (checking if exists)
        try:
            membership = Membership.objects.get(team=team, user=user)
        except Membership.DoesNotExist:
            raise ValidationError(
                {"user_id": f"User {user.email} is not a member of this team."}
            )

        # Check if removing the last admin
        if membership.role == 'admin':
            admin_count = team.memberships.filter(role='admin').count()
            if admin_count <= 1:
                return Response(
                    {"detail": "Cannot remove the last admin. Transfer ownership first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Store email before deletion for response
        user_email = membership.user.email
        
        # Delete the membership
        membership.delete()
        return Response(
            {"detail": f"Member {user_email} has been removed from the team."},
            status=status.HTTP_200_OK
        )


    @swagger_auto_schema(
        operation_summary="Change member role",
        operation_description="Change a team member's role. Only team admins can change roles.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='User ID'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'member'], description='New role')
            },
            required=['user_id', 'role']
        ),
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(description="Role changed successfully", schema=MembershipSerializer),
            400: "Validation Error",
            401: "Authentication credentials were not provided",
            403: "Only team admins can change roles",
            404: "User or team not found"
        }
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsTeamAdmin])
    @transaction.atomic
    def change_role(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')

        if new_role not in ['admin', 'member']:
            raise ValidationError({"role": "Role must be 'admin' or 'member'"})

        membership = get_object_or_404(Membership, team=team, user_id=user_id)

        if membership.user == request.user:
            return Response(
                {"detail": "You cannot change your own role. Ask another admin."},
                status=status.HTTP_400_BAD_REQUEST
            )


        if membership.role == 'admin' and new_role == 'member':
            admin_count = team.memberships.filter(role='admin').count()
            if admin_count <= 1:
                return Response(
                    {"detail": "Cannot remove the last admin. Transfer ownership first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        membership.role = new_role
        membership.save()
        return Response(MembershipSerializer(membership).data)

  
    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='admin').exists():
            raise PermissionDenied("Only team admin can delete the team.")
        return super().destroy(request, *args, **kwargs)