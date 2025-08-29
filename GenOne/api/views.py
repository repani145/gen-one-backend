# views.py
from django.contrib.auth import authenticate
from rest_framework.views import View,APIView
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
from .models import DataObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from . import models, serializers, messages,validators
from .exceptions import SerializerError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from collections import defaultdict
import openpyxl
from django.http import HttpResponse, JsonResponse
from openpyxl.worksheet.datavalidation import DataValidation
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import FilterSet
from . import models, serializers
from .pagination import StandardResultsSetPagination


# Define a filterset for RuleApplied
import django_filters
from . import models
from django.db.models import Q


class RuleAppliedFilter(django_filters.FilterSet):
    # create a custom alias for the long FK chain
    objectName = django_filters.CharFilter(
        field_name="spec__objectName__objectName", lookup_expr="exact"
    )

     # ✅ New filter for spec_id
    spec_id = django_filters.NumberFilter(
        field_name="spec__id", lookup_expr="exact"
    )

    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = models.RuleApplied
        fields = ["objectName", "rule_applied", "created_after", "created_before"]

class RuleAppliedGetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = models.RuleApplied.objects.select_related("spec").all()

        # Apply filters manually
        filterset = RuleAppliedFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        queryset = filterset.qs


        # Apply ordering
        ordering = request.GET.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")  # default ordering

        # ✅ Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request, view=self)

        serializer = serializers.RuleAppliedTableSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)


class AllDataObjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            "success": 1,
            "message": messages.DATA_FOUND,
            "data": {}
        }
        try:
            modules = models.DataObject.objects.all()
            module_ser = serializers.DataObjectSerializer(modules, many=True)
            context['data'] = module_ser.data
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

class DataObjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination  # Replace with your actual pagination class if different

    def get(self, request, id):
        context = {
            "success": 1,
            "message": messages.DATA_FOUND,
            "data": [],
        }
        try:
            
            record_id = id
            print('iddddddddddddd',id)
            # Single record fetch
            module = models.DataObject.objects.get(id=record_id)
            module_ser = serializers.DataObjectSerializer(module)
            context["data"] = module_ser.data
            context["count"] = 1

        except models.DataObject.DoesNotExist:
            context["success"] = 0
            context["message"] = "Record not found"
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)

    def post(self, request, *args, **kwargs):
        context = {
            "success": 1,
            "message": messages.DATA_SAVED,
            "data": {},
        }
        try:
            validator = validators.ObjectDataValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            req_params = validator.validated_data
            module_instance = models.DataObject(**req_params)
            module_instance.clean()
            module_instance.save()

            context["data"] = serializers.DataObjectSerializer(module_instance).data

        except IntegrityError as e:
            context["success"] = 0
            if "Duplicate entry" in str(e):
                # Extract field causing error
                err_msg = str(e)
                duplicate_value = err_msg.split("'")[1]
                field_name = err_msg.split("for key")[1].split("'")[1]
                context["message"] = f"❌ '{duplicate_value}' already exists."
            else:
                context["message"] = "❌ Database Integrity Error."

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)

    def put(self, request, id):
        context = {
            "success": 1,
            "message": messages.DATA_UPDATED,
            "data": {},
        }
        try:
            data = request.data
            record_id = id
            if not record_id:
                raise Exception("ID is required for update")
            
            validator = validators.ObjectDataValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            
            module_obj = models.DataObject.objects.get(id=record_id)
            for field in ["company", "dependencies", "module", "objectName"]:
                if field in data:
                    setattr(module_obj, field, data[field])
            
            # module_obj.full_clean()
            # print(request.data,'<<<<<<<<<--------')
            module_obj.save()

            context["data"] = serializers.DataObjectSerializer(module_obj).data

        except models.DataObject.DoesNotExist:
            context["success"] = 0
            context["message"] = "Record not found"
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)

    def patch(self, request, *args, **kwargs):
        context = {
            "success": 1,
            "message": messages.DATA_UPDATED,
            "data": {},
        }
        try:
            data = request.data
            record_id = data.get("id")
            if not record_id:
                raise Exception("ID is required for partial update")

            module_obj = models.DataObject.objects.get(id=record_id)

            for field in ["company", "dependencies", "module", "objectName"]:
                if field in data:
                    setattr(module_obj, field, data[field])

            module_obj.full_clean()
            module_obj.save()

            context["data"] = serializers.DataObjectSerializer(module_obj).data

        except models.DataObject.DoesNotExist:
            context["success"] = 0
            context["message"] = "Record not found"
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)

    def delete(self, request, id):
        context = {
            "success": 1,
            "message": messages.DATA_DELETED,
            "data": {},
        }
        try:
            if not id:
                raise Exception("ID is required for delete")

            module_obj = models.DataObject.objects.get(id=id)

            # 🔍 Check if this object is a dependency in other objects
            dependent_objects = models.DataObject.objects.filter(dependencies__contains=[module_obj.objectName])

            if dependent_objects.exists():
                raise Exception(
                    f"Cannot delete '{module_obj.objectName}' because it is a dependency of other objects."
                )

            module_obj.delete()

        except models.DataObject.DoesNotExist:
            context["success"] = 0
            context["message"] = "Record not found"
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)



class AllDependenciesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            "success": 1,
            "message": messages.DATA_FOUND,
            "data": []
        }
        try:
            # Collect all objectName values
            dependencies = list(models.DataObject.objects.values_list("objectName", flat=True))

            # Remove duplicates & sort
            unique_dependencies = sorted(set(dependencies))

            context["data"] = unique_dependencies

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)



class SpecsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        context = {"success": 1, "message": messages.DATA_FOUND, "data": {}}
        try:
            object_id = kwargs.get("id")   # Get objectName_id from URL
            if not object_id:
                context["success"] = 0
                context["message"] = "objectName_id is required"
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

            # Filter only that objectName_id and order by tab + position
            specs = (
                models.Specs.objects
                .select_related("objectName")
                .filter(objectName_id=object_id)
                .order_by("tab", "position")
            )
            # print(models.DataObject.objects.get(id=object_id).objectName)

            if not specs.exists():
                context["success"] = 1
                context["message"] = "No specs data exists"
                context["data"] = {
                    'objectName':models.DataObject.objects.get(id=object_id).objectName
                }
                return Response(context, status=status.HTTP_200_OK)

            grouped_data = defaultdict(list)
            for spec in specs:
                grouped_data[spec.tab].append({
                    "id": spec.id,
                    "company": spec.company,
                    "field_id": spec.field_id,
                    "mandatory": spec.mandatory,
                    "allowed_values": spec.allowed_values,
                    "sap_table": spec.sap_table,
                    "sap_field_id": spec.sap_field_id,
                    "sap_description": spec.sap_description,
                    "position": spec.position,   # include position
                })

            tab_data = [
                {"tab": tab_name, "fields": fields}
                for tab_name, fields in grouped_data.items()
            ]

            response_data = {
                "objectName": specs.first().objectName.objectName,
                "tabs": tab_data,
            }

            context["success"] = 1
            context["message"] = "Data fetched successfully"
            context["data"] = response_data
            return Response(context, status=status.HTTP_200_OK)

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
            context["data"] = {}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, *args, **kwargs):
        context = {"success": 1, "message": "Data saved successfully", "data": {}}
        try:
            validator = validators.SpecsValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            req_params = validator.validated_data

            # Convert Yes/No to Boolean
            # req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

            # Convert objectName ID → DataObject instance
            data_object = get_object_or_404(DataObject, pk=req_params["objectName"])
            req_params["objectName"] = data_object  

            # ✅ Auto-assign position based on tab
            existing_fields = models.Specs.objects.filter(
                objectName=data_object, tab=req_params["tab"]
            ).order_by("position")

            if existing_fields.exists():
                # Get last field position and increment
                last_position = existing_fields.last().position or 0
                req_params["position"] = last_position + 1
            else:
                # No fields in this tab → start at 0
                req_params["position"] = 0

            # Create new Specs record
            spec_instance = models.Specs.objects.create(**req_params)
            print(req_params,'--------------->>>>>>')
            context["data"] = serializers.SpecsSerializer(spec_instance).data
            

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
        return Response(context)

    def put(self, request, id=None, *args, **kwargs):
        context = {"success": 1, "message": "Data updated successfully", "data": {}}
        try:
            # ✅ validate incoming data"
            validator = validators.SpecsUpdateValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            req_params = validator.validated_data

            # ✅ convert Yes/No to Boolean (if coming as text)"
            # if isinstance(req_params.get("mandatory"), str):
            #     req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

            # ✅ fetch the Specs record at respective id--",id
            spec_instance = get_object_or_404(models.Specs, pk=id)

            # ✅ update objectName foreign key if passed"
            if "objectName" in req_params:
                data_object = get_object_or_404(DataObject, pk=req_params["objectName"])
                req_params["objectName"] = data_object

            # ✅ handle allowed_values (list or string)"
            if "allowed_values" in req_params:
                if isinstance(req_params["allowed_values"], str):
                    req_params["allowed_values"] = [
                        v.strip() for v in req_params["allowed_values"].split(",") if v.strip()
                    ]

            # ✅ update fields"
            for key, value in req_params.items():
                setattr(spec_instance, key, value)
            spec_instance.save()

            # ✅ return updated record"
            context["data"] = serializers.SpecsSerializer(spec_instance).data

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
        return Response(context)
    
    def delete(self, request,id=None):
        context = {
            "success": 1,
            "message": messages.DATA_DELETED,
            "data": {},
        }
        try:
            record_id = id
            if not record_id:
                raise Exception("ID is required for delete")

            module_obj = models.Specs.objects.get(id=record_id)
            module_obj.delete()

        except models.Specs.DoesNotExist:
            context["success"] = 0
            context["message"] = "Record not found"
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)


class ReorderSpecsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            object_id = request.data.get("objectName_id")
            tab = request.data.get("tab")
            fields = request.data.get("fields", [])

            if not object_id or not tab or not fields:
                return Response({"success": 0, "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

            # update positions
            for field in fields:
                field_id = field.get("id")
                position = field.get("position")
                if field_id is not None and position is not None:
                    models.Specs.objects.filter(
                        id=field_id,
                        objectName_id=object_id,
                        tab=tab
                    ).update(position=position)

            return Response({"success": 1, "message": "Reordering saved successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success": 0, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SpecsTemplateDownloadAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        context = {"success": 1, "message": "Template generated successfully", "data": {}}
        try:
            # ✅ Create workbook & sheet
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Specs Template"

            # ✅ Define Specs model fields (exclude id/auto fields if required)
            fields = [
                "company",
                "objectName_id",
                "tab",
                "field_id",   
                "mandatory",        # Yes / No
                "allowed_values",   # Comma separated            
                "sap_table",
                "sap_field_id",
                "sap_description",
            ]

            # ✅ Write header row
            ws.append(fields)

            # ✅ Add dropdown validation for "mandatory" column
            # Column H = 8th column (mandatory field)
            dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
            ws.add_data_validation(dv)

            # Apply dropdown for a reasonable number of rows (say 1000)
            dv.add(f"E2:E1000")

            # (Optional) Example row for user guidance
            # ws.append([
            #     "f101", "38", "GenOne", "tab1",
            #     "t11", "s11", "desc...", "Yes",
            #     "11,22,33", "1",
            # ])

            # ✅ Prepare Excel response
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="SpecsTemplate.xlsx"'
            wb.save(response)

            return response

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
            return JsonResponse(context, status=500)


class SpecsTemplateUploadAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        context = {"success": 1, "message": "Data uploaded successfully", "data": []}
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                raise Exception("No file uploaded")

            wb = openpyxl.load_workbook(file_obj)
            ws = wb.active

            # ✅ Expected header row
            expected_headers = [
                "field_id",
                "objectName_id",
                "company",
                "tab",
                "sap_table",
                "sap_field_id",
                "sap_description",
                "mandatory",
                "allowed_values",
                "position",
            ]

            headers = [cell.value for cell in ws[1]]
            if headers != expected_headers:
                raise Exception("Invalid template format. Please use the downloaded template.")

            # ✅ Iterate rows and save
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row):  # skip empty rows
                    continue

                (
                    field_id,
                    objectName_id,
                    company,
                    tab,
                    sap_table,
                    sap_field_id,
                    sap_description,
                    mandatory,
                    allowed_values,
                    position,
                ) = row

                # ✅ handle mandatory Yes/No → Boolean
                mandatory_val = True if str(mandatory).lower() == "yes" else False

                # ✅ handle allowed_values → list
                allowed_list = (
                    [v.strip() for v in str(allowed_values).split(",") if v.strip()]
                    if allowed_values
                    else None
                )

                # ✅ ensure DataObject exists
                try:
                    data_object = models.DataObject.objects.get(objectName=objectName_id)
                except ObjectDoesNotExist:
                    data_object = models.DataObject.objects.create(objectName=objectName_id)

                # ✅ create or update Specs
                spec_obj, created = models.Specs.objects.update_or_create(
                    field_id=field_id,
                    defaults={
                        "objectName": data_object,
                        "company": company,
                        "tab": tab,
                        "sap_table": sap_table,
                        "sap_field_id": sap_field_id,
                        "sap_description": sap_description,
                        "mandatory": mandatory_val,
                        "allowed_values": allowed_list,
                        "position": position,
                    },
                )

                context["data"].append(serializers.SpecsSerializer(spec_obj).data)

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return JsonResponse(context)


class CustomRuleTemplateUIViewSet(viewsets.ModelViewSet):
    """
    Provides: list, retrieve (by pk), create, update, partial_update, destroy
    Extra action: retrieve_by_rule (GET /api/rules/schema/<rule_name>/)
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = models.CustomRuleTemplateUI.objects.all()
    serializer_class = serializers.CustomRuleTemplateUISerializer
    lookup_field = "pk"

    @action(detail=False, methods=["get"], url_path=r"schema/(?P<rule_name>[^/.]+)")
    def retrieve_by_rule(self, request, rule_name=None):
        """
        GET /api/rules/schema/<rule_name>/
        returns the schema JSON for the given rule_name
        """
        obj = get_object_or_404(models.CustomRuleTemplateUI, rule_name=rule_name)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllRulesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            "success": 1,
            "message": "Rule names fetched successfully",
            "data": []
        }
        try:
            rules = models.CustomRuleTemplateUI.objects.all()
            rule_names = rules.values_list("rule_name", flat=True)  # gives QuerySet
            context["data"] = list(rule_names)  # convert to list for JSON response
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)

        return Response(context)



# class RuleAppliedView(APIView):

#     def post(self, request):
#         serializer = serializers.RuleAppliedSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"success": 1, "message": "Rule saved successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({"success": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         rules = models.RuleApplied.objects.all()
#         serializer = serializers.RuleAppliedSerializer(rules, many=True)
#         return Response({"success": 1, "data": serializer.data}, status=status.HTTP_200_OK)
class RuleAppliedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # CREATE (POST)
    def post(self, request):
        context = {
            "success": 1,
            "message": "Rule saved successfully",
            "data": {}
        }
        try:
            data = request.data
            # 1️⃣ Extract source_fields from payload
            source_fields = data.get("rule_applied_data", {}).get("source_fields", {})
            spec_id = models.DataObject.objects.get(objectName=source_fields.get("spec")).id

            # 2️⃣ Find matching Specs record
            spec_obj = models.Specs.objects.filter(
                objectName=spec_id,
                tab=source_fields.get("tab"),
                field_id=source_fields.get("field"),
            ).first()

            if not spec_obj:
                context["success"] = 0
                context["message"] = "Spec not found for given source_fields"
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

            # 3️⃣ Inject spec_field_id before serializer validation
            data["spec"] = spec_obj.id

            serializer = serializers.RuleAppliedSerializer(
                data=data,
                context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                context["data"] = serializer.data
            else:
                context["success"] = 0
                context["message"] = "Validation failed"
                context["errors"] = serializer.errors
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(context, status=status.HTTP_201_CREATED)

    # READ (GET Single Rule by ID)
    def get(self, request, pk=None):
        try:
            rule = models.RuleApplied.objects.select_related("spec").get(id=pk)
            serializer = serializers.RuleAppliedSerializer(rule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.RuleApplied.DoesNotExist:
            return Response(
                {"success": 0, "message": "Rule not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # UPDATE (PUT/PATCH)
    def put(self, request, pk=None):
        context = {"success": 1, "message": "Rule updated successfully", "data": {}}
        try:
            rule = models.RuleApplied.objects.get(id=pk)
            serializer = serializers.RuleAppliedSerializer(
                rule, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                context["data"] = serializer.data
            else:
                context["success"] = 0
                context["message"] = "Validation failed"
                context["errors"] = serializer.errors
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except models.RuleApplied.DoesNotExist:
            return Response(
                {"success": 0, "message": "Rule not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            context["success"] = 0
            context["message"] = str(e)
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(context, status=status.HTTP_200_OK)

    # DELETE
    def delete(self, request, pk=None):
        try:
            rule = models.RuleApplied.objects.get(id=pk)
            rule.delete()
            return Response(
                {"success": 1, "message": "Rule deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except models.RuleApplied.DoesNotExist:
            return Response(
                {"success": 0, "message": "Rule not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": 0, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from . import models, serializers


class RuleAppliedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            queryset = models.RuleApplied.objects.select_related("spec").all()

            # --- Filtering ---
            object_name = request.GET.get("objectName")
            if object_name:
                queryset = queryset.filter(spec__objectName__objectName=object_name)

            rule_applied = request.GET.get("rule_applied")
            if rule_applied:
                queryset = queryset.filter(rule_applied__icontains=rule_applied)

            created_after = request.GET.get("created_after")
            if created_after:
                queryset = queryset.filter(created_at__gte=created_after)

            created_before = request.GET.get("created_before")
            if created_before:
                queryset = queryset.filter(created_at__lte=created_before)

            # --- Search ---
            search = request.GET.get("search")
            if search:
                queryset = queryset.filter(
                    Q(description__icontains=search)
                    | Q(spec__tab__icontains=search)
                    | Q(spec__field_id__icontains=search)
                )

            # --- Ordering ---
            ordering = request.GET.get("ordering")
            if ordering:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by("-created_at")

            serializer = serializers.RuleAppliedTableSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# views.py
# class RuleAppliedBySpecView(APIView):
#     def get(self, request, spec_id):
#         context = {
#             "success": 1,
#             "message": "Rules fetched successfully",
#             "data": []
#         }
#         try:
#             # Get queryset filtered by spec_id
#             queryset = models.RuleApplied.objects.filter(spec_id=spec_id).distinct("rule_applied")

#             # Serialize queryset
#             serializer = serializers.RuleAppliedNameSerializer(queryset, many=True)

#             # Convert from list of dicts → list of values
#             context["data"] = [item["rule_applied"] for item in serializer.data]
#         except Exception as e:
#             context["success"] = 0
#             context["message"] = f"Failed to fetch rules: {str(e)}"

#         return Response(context, status=status.HTTP_200_OK)
# views.py
class RuleAppliedBySpecView(APIView):
    def get(self, request, spec_id):
        context = {
            "success": 1,
            "message": "Rules fetched successfully",
            "data": []
        }
        try:
            # SQLite-safe: values() + distinct()
            queryset = (
                models.RuleApplied.objects.filter(spec_id=spec_id)
                .values("rule_applied")
                .distinct()
            )

            serializer = serializers.RuleAppliedNameSerializer(queryset, many=True)

            # Extract only values → ["rule1", "rule2", ...]
            context["data"] = [item["rule_applied"] for item in serializer.data]

        except Exception as e:
            context["success"] = 0
            context["message"] = f"Failed to fetch rules: {str(e)}"

        return Response(context, status=status.HTTP_200_OK)
