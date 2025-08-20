from rest_framework import serializers
from . import models

def validate_non_empty_string(value):
    if not isinstance(value, str) or not value.strip():
        raise serializers.ValidationError("This field must be a non-empty string.")
    return value

def validate_dependencies(value):
    if not isinstance(value, list):
        raise serializers.ValidationError("Dependencies must be a list.")
    if not all(isinstance(dep, str) and dep.strip() for dep in value):
        raise serializers.ValidationError("Each dependency must be a non-empty string.")
    return value


from rest_framework import serializers

class ObjectDataValidator(serializers.Serializer):
    company = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Company name is a required field.",
            "null": "Company name cannot be null.",
            "blank": "Company name cannot be empty."
        }
    )

    module = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Module name is a required field.",
            "null": "Module name cannot be null.",
            "blank": "Module name cannot be empty."
        }
    )



    objectName = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Object name is a required field.",
            "null": "Object name cannot be null.",
            "blank": "Object name cannot be empty."
        }
    )

    dependencies = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=True,
        allow_null=False,
        error_messages={
            "required": "Dependencies is a required field.",
            "null": "Dependencies cannot be null.",
            "invalid": "Dependencies must be a list of strings."
        }
    )

    

    
# from rest_framework import serializers

class SpecsValidator(serializers.Serializer):
    # company = serializers.CharField(
    #     required=True,
    #     allow_null=False,
    #     allow_blank=False,
    #     error_messages={
    #         "required": "Company is a required field.",
    #         "null": "Company cannot be null.",
    #         "blank": "Company cannot be empty."
    #     }
    # )

    objectName = serializers.IntegerField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Object Name (DataObject ID) is required.",
            "null": "Object Name cannot be null.",
            "invalid": "Object Name must be a valid integer (DataObject ID)."
        }
    )

    tab = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Tab is a required field.",
            "null": "Tab cannot be null.",
            "blank": "Tab cannot be empty."
        }
    )

    field_id = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Field ID is a required field.",
            "null": "Field ID cannot be null.",
            "blank": "Field ID cannot be empty."
        }
    )

    mandatory = serializers.ChoiceField(
        choices=["Yes", "No"],
        required=True,
        error_messages={
            "required": "Mandatory field is required.",
            "invalid_choice": "Mandatory must be either 'Yes' or 'No'."
        }
    )

    allowed_values = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_null=True,
        error_messages={
            "null": "Allowed values cannot be null.",
            "invalid": "Allowed values must be a list of non-empty strings."
        }
    )

    sap_table = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Table must be a valid string."
        }
    )

    sap_field_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Field ID must be a valid string."
        }
    )

    sap_description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Description must be a valid string."
        }
    )

    def validate(self, data):
        object_id = data.get("objectName")
        tab = data.get("tab")
        field_id = data.get("field_id")

        if models.Specs.objects.filter(objectName_id=object_id, tab=tab, field_id=field_id).exists():
            obj = models.DataObject.objects.get(id=object_id)
            # print(obj.objectName)
            raise serializers.ValidationError(
                {"tab/field_id": f"'{field_id}' is already existed in '{tab}' Tab at '{obj.objectName}'"}
            )
        # print(models.DataObject.get(id=object_id))
        return data


class SpecsUpdateValidator(serializers.Serializer):
    # company = serializers.CharField(
    #     required=True,
    #     allow_null=False,
    #     allow_blank=False,
    #     error_messages={
    #         "required": "Company is a required field.",
    #         "null": "Company cannot be null.",
    #         "blank": "Company cannot be empty."
    #     }
    # )

    objectName = serializers.IntegerField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "Object Name (DataObject ID) is required.",
            "null": "Object Name cannot be null.",
            "invalid": "Object Name must be a valid integer (DataObject ID)."
        }
    )

    tab = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Tab is a required field.",
            "null": "Tab cannot be null.",
            "blank": "Tab cannot be empty."
        }
    )

    field_id = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "Field ID is a required field.",
            "null": "Field ID cannot be null.",
            "blank": "Field ID cannot be empty."
        }
    )

    mandatory = serializers.ChoiceField(
        choices=["Yes", "No"],
        required=True,
        error_messages={
            "required": "Mandatory field is required.",
            "invalid_choice": "Mandatory must be either 'Yes' or 'No'."
        }
    )

    allowed_values = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_null=True,
        error_messages={
            "null": "Allowed values cannot be null.",
            "invalid": "Allowed values must be a list of non-empty strings."
        }
    )

    sap_table = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Table must be a valid string."
        }
    )

    sap_field_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Field ID must be a valid string."
        }
    )

    sap_description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "invalid": "SAP Description must be a valid string."
        }
    )


