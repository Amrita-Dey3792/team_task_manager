# apps/companies/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company
from .serializers import CompanySerializer
from .permissions import IsCompanyOwner  

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    

    permission_classes = [IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        return Company.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)