from rest_framework import serializers

from apps.content.models import Content, ContentVersion


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = (
            "id",
            "content_type",
            "title",
            "body",
            "parent_content",
            "ai_provider_used",
            "tags",
            "is_favorite",
            "is_archived",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class ContentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVersion
        fields = ("id", "body", "change_note", "created_by", "created_at")
        read_only_fields = fields
