from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework_simplejwt.authentication import JWTAuthentication  


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        
        # Add security definitions for OpenAPI 2.0 (Swagger)
        if not hasattr(schema, 'securityDefinitions'):
            schema.securityDefinitions = {}
        
        schema.securityDefinitions['Bearer'] = {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"\n\nSteps:\n1. Login at /api/auth/login/ to get your token\n2. Copy the "access" token from response\n3. Click "Authorize" button above\n4. Enter: Bearer <your_access_token>'
        }
        
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="Team Task Manager API",
        default_version='v1',
        description="JWT Auth + Task Management API\n\n**Authentication Required:**\n1. First, register or login at `/api/auth/register/` or `/api/auth/login/`\n2. Copy the `access` token from the response\n3. Click the **Authorize** button (lock icon) at the top right\n4. Enter: `Bearer <your_access_token>`\n5. Click **Authorize** and then **Close**\n6. Now you can use all authenticated endpoints!",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,),
    generator_class=CustomOpenAPISchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),     # register + login
    path('api/companies/', include('companies.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/tasks/', include('tasks.urls')),    # task CRUD
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)