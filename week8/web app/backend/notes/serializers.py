from rest_framework import serializers

from notes.ai_service import encrypt_api_key
from notes.models import AISettings, Note, Todo


class BaseItemSerializer(serializers.ModelSerializer):
    """共享验证逻辑的基类"""

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("标题不能为空")
        if len(value) > 200:
            raise serializers.ValidationError("标题不能超过200个字符")
        return value.strip()

    def validate_category(self, value):
        if value is not None:
            value = value.strip() if value else value
            if len(value) > 50:
                raise serializers.ValidationError("分类名称不能超过50个字符")
        return value

    def validate_content(self, value):
        if value and len(value) > 10000:
            raise serializers.ValidationError("内容不能超过10000个字符")
        return value


class TodoSerializer(BaseItemSerializer):
    class Meta:
        model = Todo
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NoteSerializer(BaseItemSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AISettingsSerializer(serializers.ModelSerializer):
    is_configured = serializers.SerializerMethodField()

    class Meta:
        model = AISettings
        fields = ["api_key", "base_url", "model", "updated_at", "is_configured"]
        read_only_fields = ["updated_at", "is_configured"]

    def get_is_configured(self, obj):
        return obj.is_configured()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Mask the API key in responses
        if instance.api_key:
            data["api_key"] = "***"
        else:
            data["api_key"] = ""
        return data

    def update(self, instance, validated_data):
        api_key = validated_data.get("api_key", "***")
        # If the user sent "***", keep the existing key
        if api_key == "***":
            validated_data.pop("api_key", None)
        else:
            validated_data["api_key"] = encrypt_api_key(api_key)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        api_key = validated_data.get("api_key", "")
        if api_key and api_key != "***":
            validated_data["api_key"] = encrypt_api_key(api_key)
        return super().create(validated_data)
