# apps/users/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

# ====================== REGISTER SERIALIZER ======================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password",
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'password', 'password2']
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
        }

    def to_representation(self, instance):
        return {
            "user": {
                "id": str(instance.id),
                "email": instance.email,
                "username": instance.username,
                "name": instance.name or ""
            },
            "message": "Registration successful!"
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data.get('name', ''),
            password=validated_data['password']
        )
        return user


# ====================== LOGIN SERIALIZER ======================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        style={'placeholder': 'amrita@example.com'}
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


    class Meta:
        swagger_schema_fields = {
            "example": {
                "email": "amrita@example.com",
                "password": "yourpassword123"
            }
        }

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password", code='authorization')
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled", code='authorization')
        else:
            raise serializers.ValidationError("Must include email and password")

        attrs['user'] = user
        return attrs