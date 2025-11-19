from rest_framework import serializers
from .models import Team, Membership
from companies.models import Company
from users.models import User


class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['joined_at']

    def validate_user_id(self, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist.")


class TeamSerializer(serializers.ModelSerializer):

    company_id = serializers.UUIDField(write_only=True)


    company = serializers.SerializerMethodField()


    members = MembershipSerializer(source='memberships', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'company_id',      
            'company',         
            'created_at',
            'members',
            'member_count'
        ]
        read_only_fields = ['created_at', 'company', 'members', 'member_count']

 
    def validate_company_id(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        try:
            company = Company.objects.get(id=value, created_by=request.user)
        except Company.DoesNotExist:
            raise serializers.ValidationError(
                "You can only create teams in companies you own."
            )


        self.context['validated_company'] = company
        return value


    def get_company(self, obj):
        if not obj.company:
            return None
        return {
            "id": str(obj.company.id),
            "name": obj.company.name
        }

    def get_member_count(self, obj):
        return obj.memberships.count()


    def create(self, validated_data):

        validated_data.pop('company_id', None)

   
        company = self.context.get('validated_company')
        if not company:
            raise serializers.ValidationError({"company_id": "Invalid or missing company."})


        return Team.objects.create(company=company, **validated_data)