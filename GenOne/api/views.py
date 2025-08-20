# views.py
from django.contrib.auth import authenticate
from rest_framework.views import View,APIView
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
from .models import DataObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# from . import serializers
# from . import validators
# from rest_framework.pagination import PageNumberPagination
# from rest_framework import status
from django.http import JsonResponse
from . import messages
from . import validators

# class LoginView(APIView):
    
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         # Validate input
#         if not username or not password:
#             return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

#         # Authenticate user
#         user = authenticate(username=username, password=password)
#         if user is None:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token)
#         }, status=status.HTTP_200_OK)


from rest_framework.response import Response

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from . import models, serializers, messages
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

from .exceptions import SerializerError

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

    def delete(self, request,id):
        context = {
            "success": 1,
            "message": messages.DATA_DELETED,
            "data": {},
        }
        try:
            record_id = id
            if not record_id:
                raise Exception("ID is required for delete")

            module_obj = models.DataObject.objects.get(id=record_id)
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
            dependencies = []
            for obj in models.DataObject.objects.all():
                if isinstance(obj.dependencies, list):
                    dependencies.extend(obj.dependencies)

            # Remove duplicates & sort
            unique_dependencies = sorted(set(dependencies))
            context['data'] = unique_dependencies

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from . import models, serializers, validators
from .exceptions import SerializerError  # if you already used it
from rest_framework import status
from collections import defaultdict

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
            req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

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
            if isinstance(req_params.get("mandatory"), str):
                req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

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
                    print(field_id,position,'.......................')

            return Response({"success": 1, "message": "Reordering saved successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success": 0, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def get(self, request, *args, **kwargs):
    #     context = {
    #         "success": 1,
    #         "message": messages.DATA_FOUND,
    #         "data": {}
    #     }
    #     try:
    #         object_id = kwargs.get("id")   # extract `id` from URL
    #         print(object_id) # returning None
    #         specs = models.Specs.objects.filter(objectName_id=object_id)  # use filter
            
    #         context["data"] = serializers.SpecsSerializer(specs, many=True).data
    #     except Exception as e:
    #         context["success"] = 0
    #         context["message"] = str(e)

    #     return Response(context)


    # def get(self, request, *args, **kwargs):
    #     context = {"success": 1, "message": messages.DATA_FOUND, "data": {}}
    #     try:
    #         specs = models.Specs.objects.select_related("objectName").all().order_by(
    #             "objectName__objectName", "tab", "field_id"
    #         )

    #         grouped_data = defaultdict(lambda: defaultdict(list))

    #         for spec in specs:
    #             grouped_data[spec.objectName.objectName][spec.tab].append({
    #                 "id": spec.id,
    #                 "company":spec.company,
    #                 "field_id": spec.field_id,
    #                 "mandatory": spec.mandatory,
    #                 "allowed_values": spec.allowed_values,
    #                 "sap_table": spec.sap_table,
    #                 "sap_field_id": spec.sap_field_id,
    #                 "sap_description": spec.sap_description,
    #             })

    #         response_data = []
    #         for obj_name, tabs in grouped_data.items():
    #             tab_data = []
    #             for tab_name, fields in tabs.items():
    #                 tab_data.append({
    #                     "tab": tab_name,
    #                     "fields": fields
    #                 })
    #             response_data.append({
    #                 "objectName": obj_name,
    #                 "tabs": tab_data
    #             })

    #         context["success"] = 1
    #         context["message"] = "Data fetched successfully"
    #         context["data"] = response_data
    #         return Response(context, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         context["success"] = 0
    #         context["message"] = str(e)
    #         context["data"] = {}
    #         return Response(context, status=status.HTTP_400_BAD_REQUEST)

    
    # def post(self, request, *args, **kwargs):
    #     context = {"success": 1, "message": "Data saved successfully", "data": {}}
    #     try:
    #         validator = validators.SpecsValidator(data=request.data)
    #         if not validator.is_valid():
    #             raise SerializerError(validator.errors)

    #         req_params = validator.validated_data

    #         # Convert Yes/No to Boolean
    #         req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

    #         # Convert objectName ID → DataObject instance
    #         data_object = get_object_or_404(DataObject, pk=req_params["objectName"])
    #         req_params["objectName"] = data_object  

    #         spec_instance = models.Specs.objects.create(**req_params)
    #         context["data"] = serializers.SpecsSerializer(spec_instance).data

    #     except Exception as e:
    #         context["success"] = 0
    #         context["message"] = str(e)
    #     return Response(context)
    
    # def put(self, request, pk=None, *args, **kwargs):
    #     context = {
    #         "success": 1, 
    #         "message": messages.DATA_UPDATED, 
    #         "data": {}
    #         }
    #     try:
    #         spec_instance = get_object_or_404(models.Specs, pk=pk)

    #         validator = validators.SpecsValidator(data=request.data)
    #         if not validator.is_valid():
    #             raise SerializerError(validator.errors)

    #         req_params = validator.validated_data
    #         req_params["mandatory"] = True if req_params["mandatory"] == "Yes" else False

    #         for field, value in req_params.items():
    #             setattr(spec_instance, field, value)
    #         spec_instance.save()

    #         context["data"] = serializers.SpecsSerializer(spec_instance).data

    #     except Exception as e:
    #         context["success"] = 0
    #         context["message"] = str(e)
    #     return Response(context)

    # def delete(self, request, pk=None, *args, **kwargs):
    #     context = {
    #         "success": 1, 
    #         "message": messages.DATA_DELETED, 
    #         "data": {}
    #         }
    #     try:
    #         spec_instance = get_object_or_404(models.Specs, pk=pk)
    #         spec_instance.delete()
    #     except Exception as e:
    #         context["success"] = 0
    #         context["message"] = str(e)
    #     return Response(context)

import openpyxl
from django.http import HttpResponse, JsonResponse
from openpyxl.worksheet.datavalidation import DataValidation
from rest_framework.views import APIView

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

