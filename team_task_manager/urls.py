from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework_simplejwt.authentication import JWTAuthentication  


security_definition = {
    'type': 'apiKey',
    'name': 'Authorization',
    'in': 'header',
    'description': '⚠️ IMPORTANT: Enter "Bearer " (with space) followed by your token.\nExample: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\n\nSteps:\n1. Login at /api/auth/login/ to get your token\n2. Copy the "access" token from response\n3. Enter here: Bearer <paste_your_token>'
}

class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
       
        if not hasattr(schema, 'securityDefinitions'):
            schema.securityDefinitions = {}
        
        schema.securityDefinitions['Bearer'] = security_definition
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="Team Task Manager API",
        default_version='v1',
        description="JWT Auth + Task Management",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,),
    generator_class=CustomOpenAPISchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),


    path('api/auth/', include('users.urls')),     # register + login
    path('api/tasks/', include('tasks.urls')),    # task CRUD
    path('api/companies/', include('companies.urls')),

   
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),

]