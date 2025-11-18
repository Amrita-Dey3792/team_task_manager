from rest_framework import serializers
from .models import Team, Membership
from companies.serializers import CompanySerializer

class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    user_id = serializers.UUIDField(write_only=True)  # for adding member

    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['joined_at']

class TeamSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True)
    members = MembershipSerializer(source='memberships', many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'company', 'company_id', 'created_at', 'members']
        read_only_fields = ['created_at']