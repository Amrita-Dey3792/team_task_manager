# apps/users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== REGISTER ====================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new account and get JWT tokens immediately",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                            "email": "amrita@example.com",
                            "name": "Amrita",
                            "username": "amrita"
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "message": "Registration successful!"
                    }
                }
            ),
            400: "Validation Error"
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name or "",
                    "username": user.username
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Registration successful!"
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== LOGIN ====================
class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Login with email and password to receive JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                            "email": "amrita@example.com",
                            "name": "Amrita",
                            "username": "amrita"
                        }
                    }
                }
            ),
            401: "Invalid credentials"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name or "",
                    "username": user.username
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            "detail": "Invalid email or password"
        }, status=status.HTTP_401_UNAUTHORIZED)


# ==================== PROFILE ====================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get logged-in user profile",
        operation_description="Returns current authenticated user's details",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="User profile",
                examples={
                    "application/json": {
                        "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                        "email": "amrita@example.com",
                        "name": "Amrita Roy",
                        "username": "amrita"
                    }
                }
            )
        }
    )
    def get(self, request):
        user = request.user
        return Response({
            "id": str(user.id),
            "email": user.email,
            "name": user.name or "",
            "username": user.username
        })