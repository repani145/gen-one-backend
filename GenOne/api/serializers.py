from rest_framework import serializers
from .models import DataObject
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

# from rest_framework import serializers
from .models import Specs

class SpecsSerializer(serializers.ModelSerializer):
    # Convert Boolean -> Yes/No for response
    # mandatory = serializers.SerializerMethodField()

    class Meta:
        model = Specs
        fields = "__all__"


