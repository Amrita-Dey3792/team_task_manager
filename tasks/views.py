from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer


# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to__user', 'due_date']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date']

    def get_queryset(self):
        return Task.objects.filter(team__memberships__user=self.request.user, is_deleted=False)

