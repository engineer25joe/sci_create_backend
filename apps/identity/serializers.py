from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.identity.models import User, Workspace


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    display_name = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_password(self, value):
        validate_password(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "display_name",
            "preferred_language",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = fields


class WorkspaceSerializer(serializers.ModelSerializer):
    is_personal = serializers.BooleanField(read_only=True)

    class Meta:
        model = Workspace
        fields = ("id", "name", "organization", "is_personal", "is_default", "created_at")
        read_only_fields = ("id", "is_personal", "created_at")
