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
