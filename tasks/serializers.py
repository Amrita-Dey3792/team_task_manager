from rest_framework import serializers
from .models import Task, Membership

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(slug_field='user__email', queryset=Membership.objects.all(), required=False, allow_null=True)
    created_by = serializers.SlugRelatedField(slug_field='user__email', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['team', 'created_by', 'is_deleted']