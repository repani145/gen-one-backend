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
from rest_framework import status
from collections import defaultdict
import openpyxl
from django.http import HttpResponse, JsonResponse
from openpyxl.worksheet.datavalidation import DataValidation
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

# from rest_framework.serializers


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
            print(request.data,'<<<<<<<<<--------')
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
