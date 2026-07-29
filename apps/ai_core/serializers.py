from rest_framework import serializers


class GenerateContentSerializer(serializers.Serializer):
    workspace_id = serializers.UUIDField()
    provider = serializers.CharField(max_length=50)
    prompt = serializers.CharField(max_length=8000)
