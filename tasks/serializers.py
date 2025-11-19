from rest_framework import serializers
from .models import Task, Membership
from teams.models import Team

class TaskSerializer(serializers.ModelSerializer):
    assigned_members = serializers.SerializerMethodField()
    team_members = serializers.SerializerMethodField()
    assigned_to_email = serializers.EmailField(write_only=True, required=False, allow_null=True)
    created_by = serializers.SerializerMethodField()
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.none(), required=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'is_deleted', 'assigned_to']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['team'].queryset = Team.objects.filter(memberships__user=request.user).distinct()
        else:
            self.fields['team'].queryset = Team.objects.none()
        
        self.fields.pop('assigned_to_email', None)
    
    def get_assigned_members(self, obj):
        """Return list of all assigned members with their details"""
        members = []
        for membership in obj.assigned_members.all():
            members.append({
                'id': str(membership.id),
                'user_id': str(membership.user.id),
                'email': membership.user.email,
                'role': membership.role,
                'joined_at': membership.joined_at.isoformat() if membership.joined_at else None
            })
        return members
    
    def get_team_members(self, obj):
        """Return list of all team members"""
        members = []
        for membership in obj.team.memberships.all():
            members.append({
                'id': str(membership.id),
                'user_id': str(membership.user.id),
                'email': membership.user.email,
                'role': membership.role,
                'joined_at': membership.joined_at.isoformat() if membership.joined_at else None
            })
        return members
    
    def get_created_by(self, obj):
        """Return email of creator"""
        if obj.created_by:
            return obj.created_by.user.email
        return None
    
    def validate_title(self, value):
        """Validate task title"""
        if not value or not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()
    
    def to_internal_value(self, data):
        """Reject assigned_to field - assignment must be done via assign endpoint"""
        if 'assigned_to' in data:
            raise serializers.ValidationError({
                'assigned_to': 'Tasks cannot be assigned during create or update. Use the assign endpoint (POST /api/tasks/{id}/assign/) to assign tasks.'
            })
        return super().to_internal_value(data)
    
    def validate(self, attrs):
        """Ensure assigned_to is not in attrs (should be read-only)"""
        attrs.pop('assigned_to', None)
        return attrs