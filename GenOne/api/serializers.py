from rest_framework import serializers
from .models import DataObject,CustomRuleTemplateUI,RuleApplied,Specs
from .validators import validate_non_empty_string, validate_dependencies

class DataObjectSerializer(serializers.ModelSerializer):
    company = serializers.CharField(validators=[validate_non_empty_string])
    dependencies = serializers.ListField(
    child=serializers.CharField(),
    validators=[validate_dependencies],
    required=False,
    allow_null=True,
    allow_empty=True,
    default=list
)

    module = serializers.CharField(validators=[validate_non_empty_string])
    objectName = serializers.CharField(validators=[validate_non_empty_string])

    class Meta:
        model = DataObject
        fields = ["id", "company", "dependencies", "module", "objectName"]


class SpecsSerializer(serializers.ModelSerializer):
    # Convert Boolean -> Yes/No for response
    # mandatory = serializers.SerializerMethodField()

    class Meta:
        model = Specs
        fields = "__all__"


class CustomRuleTemplateUISerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomRuleTemplateUI
        fields = ["id", "rule_name", "schema", "version", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_schema(self, value):
        """
        Basic validation: ensure schema is a dict and contains 'version' and 'title' keys.
        You can extend this to JSON Schema validation if you want strict checks.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("schema must be a JSON object")
        if "version" not in value:
            raise serializers.ValidationError("schema must include 'version' key")
        if "title" not in value:
            raise serializers.ValidationError("schema should include 'title' key")
        return value


class RuleAppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleApplied
        fields = "__all__"

# class RuleAppliedTableSerializer(serializers.ModelSerializer):
#     objectName = serializers.CharField(source="specs.objectName.objectName", read_only=True)
#     tab = serializers.CharField(source="specs.tab", read_only=True)
#     field = serializers.CharField(source="specs.field_id", read_only=True)

#     class Meta:
#         model = RuleApplied
#         fields = ["id", "objectName", "tab", "field", "rule_applied", "description", "created_at"]

class RuleAppliedTableSerializer(serializers.ModelSerializer):
    objectName = serializers.CharField(source="spec.objectName.objectName", read_only=True)
    tab = serializers.CharField(source="spec.tab", read_only=True)
    field_id = serializers.CharField(source="spec.field_id", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)


    class Meta:
        model = RuleApplied
        fields = ["id","objectName", "tab", "field_id", "rule_applied", "description","created_at"]
    

# serializers.py
class RuleAppliedNameSerializer(serializers.Serializer):
    rule_applied = serializers.CharField()

from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    objectName = serializers.CharField()
    file = serializers.FileField()


from . import models
class DataFileSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = models.DataFile
        fields = "__all__"
