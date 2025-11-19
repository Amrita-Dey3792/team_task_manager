from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='created_by.email', read_only=True)
    owner_id = serializers.UUIDField(source='created_by.id', read_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'owner', 'owner_id', 'created_at']
        read_only_fields = ['owner', 'owner_id', 'created_at']
        extra_kwargs = {
            'name': {'required': True}
        }
    
    def validate_name(self, value):

        if not value or not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        return value.strip()