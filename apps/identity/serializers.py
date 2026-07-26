from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.identity.models import BrandProfile, User, Workspace, WorkspaceMember


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


class CreateOrganizationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=220)


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["admin", "manager", "editor", "member"], default="member")


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ("id", "email", "role", "created_at")
        read_only_fields = fields


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = (
            "business_name",
            "industry",
            "target_audience",
            "preferred_tone",
            "writing_style",
            "languages",
            "brand_keywords",
            "brand_colors",
            "social_accounts",
            "goals",
            "preferred_ai_provider",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
