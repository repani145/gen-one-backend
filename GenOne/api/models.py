from django.db import models
from .validators import validate_non_empty_string, validate_dependencies

DEFAULT_COMPANY = "GenOne"

class DataObject(models.Model):
    company = models.CharField(
        max_length=255,
        validators=[validate_non_empty_string],
        default=DEFAULT_COMPANY
    )
    dependencies = models.JSONField(validators=[validate_dependencies],default=list)
    module = models.CharField(max_length=255, validators=[validate_non_empty_string],unique=True)
    objectName = models.CharField(max_length=255, validators=[validate_non_empty_string],unique=True)

    def __str__(self):
        return f"{self.company} - {self.objectName}"

class Specs(models.Model):
    company = models.CharField(
        max_length=255,
        validators=[validate_non_empty_string],
        default=DEFAULT_COMPANY
    )
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    objectName = models.ForeignKey(DataObject, on_delete=models.CASCADE, related_name="field_mappings")
    tab = models.CharField(max_length=100)
    field_id = models.CharField(max_length=100)
    mandatory = models.CharField(
        max_length=5,
        choices=YES_NO_CHOICES,
        default='No'
    )
    allowed_values = models.JSONField(blank=True, null=True)
    sap_table = models.CharField(max_length=100, blank=True, null=True)
    sap_field_id = models.CharField(max_length=100, blank=True, null=True)
    sap_description = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)  # 👈 new field

    class Meta:
        unique_together = ('objectName', 'tab', 'field_id')
        ordering = ['objectName__objectName', 'tab', 'position']  # 👈 now based on position

    def __str__(self):
        return f"{self.objectName.objectName} - {self.field_id}"

# from django.contrib.postgres.fields import JSONField  # if using older Django/Postgres
# For Django 3.1+ use models.JSONField

class CustomRuleTemplateUI(models.Model):
    rule_name = models.CharField(max_length=150, unique=True)  # e.g., "ALLOWED_ONLY_IF"
    schema = models.JSONField()   # JSON structure describing groups/fields
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "custom_rule_template_ui"
        ordering = ["rule_name"]

    def __str__(self):
        return f"{self.rule_name} (v{self.version})"
    
class RuleApplied(models.Model):
    spec = models.ForeignKey("Specs", on_delete=models.CASCADE)  # ForeignKey to your Spec model
    rule_applied = models.CharField(max_length=255)  # e.g., "rule1"
    description = models.TextField(blank=True, null=True)  # store generated description
    rule_applied_data = models.JSONField()  # stores the full JSON you showed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["spec", "rule_applied", "rule_applied_data"],
                name="unique_spec_rule_data"
            )
        ]

    def __str__(self):
        return f"{self.rule_applied} (Spec ID: {self.spec})"

