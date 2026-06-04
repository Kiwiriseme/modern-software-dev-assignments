from rest_framework import serializers

from notes.models import Note, Todo


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
