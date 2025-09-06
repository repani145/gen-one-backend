# import uuid
# from datetime import datetime

# # Global in-memory store for progress objects
# PROGRESS_STORE = {}

# def create_progress(task_name: str):
#     task_id = str(uuid.uuid4())
#     progress_obj = {
#         "id": task_id,
#         "task_name": task_name,
#         "progress": 0,
#         "message": "Started",
#         "created_at": datetime.now().isoformat(),
#         "updated_at": datetime.now().isoformat()
#     }
#     PROGRESS_STORE[task_id] = progress_obj
#     print(f"[PROGRESS] Created tracker: {task_id} for task: {task_name}")
#     return task_id, progress_obj

# def update_progress(task_id: str, progress: int, message: str = ""):
#     if task_id in PROGRESS_STORE:
#         PROGRESS_STORE[task_id]["progress"] = progress
#         if message:
#             PROGRESS_STORE[task_id]["message"] = message
#         PROGRESS_STORE[task_id]["updated_at"] = datetime.now().isoformat()
#         print(f"[PROGRESS] {task_id} -> {progress}% | {message}")

# def get_progress(task_id: str):
#     return PROGRESS_STORE.get(task_id, {"progress": 0, "message": ""})


# class PreValidationCheckAndValidationView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, data_object_id):
#         context = {"success": 0, "message": "Something went wrong.", "data": {}}
#         print("\n[1] >>> Validation API called with data_object_id:", data_object_id)

#         # Create progress tracker for this API call
#         task_id, tracker = create_progress(f"Validation-{data_object_id}")
#         update_progress(task_id, 0, "Validation API called")

#         try:
#             # 0. Get the DataObject and check its data file
#             update_progress(task_id, 5, "Fetching DataObject")
#             data_object = models.DataObject.objects.filter(id=data_object_id).first()
#             print(f"[2] DataObject fetched: {data_object}")
#             if not data_object:
#                 context["message"] = "DataObject not found."
#                 update_progress(task_id, 0, context["message"])
#                 print(f"[2.1] ERROR: {context['message']}")
#                 return Response(context, status=status.HTTP_404_NOT_FOUND)

#             # Check own file
#             update_progress(task_id, 10, "Checking main data file")
#             own_file_exists = models.DataFile.objects.filter(data_object=data_object, version=0).exists()
#             print(f"[3] Own file exists: {own_file_exists}")
#             if not own_file_exists:
#                 context["message"] = f"Data file for '{data_object.objectName}' not found. Please upload before validation."
#                 update_progress(task_id, 10, context["message"])
#                 print(f"[3.1] ERROR: {context['message']}")
#                 return Response(context, status=status.HTTP_400_BAD_REQUEST)

#             # Check dependencies
#             update_progress(task_id, 20, "Checking dependencies")
#             dependencies = data_object.dependencies or []
#             print(f"[4] Declared dependencies: {dependencies}")
#             rules_applied_qs = models.RuleApplied.objects.filter(spec__objectName=data_object.id)
#             print(f"[5] Rules applied count: {rules_applied_qs.count()}")
#             target_objects_dependencies = []
#             for rule in rules_applied_qs:
#                 targets = get_target_specs(rule.rule_applied_data)
#                 print(f"[5.1] Rule {rule.id} targets: {targets}")
#                 target_objects_dependencies.extend(targets)
#             dependencies = list(set(dependencies + target_objects_dependencies))
#             print(f"[6] Final dependencies: {dependencies}")

#             missing_files = []
#             for dep_name in dependencies:
#                 dep_object = models.DataObject.objects.filter(objectName=dep_name).first()
#                 if not dep_object or not models.DataFile.objects.filter(data_object=dep_object, version=0).exists():
#                     missing_files.append(dep_name)
#                     print(f"[7] Missing dependency: {dep_name}")
#             if missing_files:
#                 context["message"] = f"Validation not possible. Missing dependencies: {', '.join(missing_files)}"
#                 update_progress(task_id, 20, context["message"])
#                 print(f"[7.1] ERROR: {context['message']}")
#                 return Response(context, status=status.HTTP_400_BAD_REQUEST)

#             update_progress(task_id, 30, "Dependencies validated")
#             print("[8] Dependencies validated successfully.")

#             # Start default validations
#             paths = create_and_get_working_file_path(request.data.get("dataObjectId"))
#             update_progress(task_id, 40, "Running default validations")
#             print(f"[9] Working paths: {paths}")
#             resultLog1 = run_default_validators(
#                 file_path=paths.get('working_file_path'),
#                 log_file_path=paths.get('log_file_path'),
#                 primary_field=request.data.get("fieldId")
#             )
#             print(f"[10] Default validation logs: {resultLog1}")
#             delete_working_directory(paths.get('working_file_path'))
#             print("[11] Deleted working directory.")

#             # Prepare logs
#             update_progress(task_id, 60, "Processing logs")
#             source_file = get_file_path_with_object_name(data_object.objectName)
#             log_file_path = paths.get('log_file_path')
#             print(f"[12] Source file: {source_file}, Log file path: {log_file_path}")
#             try:
#                 with open(log_file_path, "rb") as f:
#                     existing_log = pd.read_excel(f)
#                 print(f"[13] Existing log loaded. Rows: {len(existing_log)}")
#             except FileNotFoundError:
#                 existing_log = pd.DataFrame(columns=["primary_field", "rule_data", "time"])
#                 print("[13.1] No existing log found, created empty log.")

#             # Run custom rule validations
#             update_progress(task_id, 70, "Running custom rule validations")
#             new_logs_list = []
#             rules_applied_qs = models.RuleApplied.objects.filter(spec__objectName=data_object.id)
#             print(f"[14] Custom rules count: {rules_applied_qs.count()}")
#             targets_obj = {}
#             for rule in rules_applied_qs:
#                 targets = get_target_specs(json_spec=rule.rule_applied_data)
#                 for obj in targets:
#                     targets_obj[obj] = get_file_path_with_object_name(obj)
#                 print(f"[14.1] Running custom rule {rule.id} on targets: {targets_obj}")
#                 resultLog2 = run_custom_rule_validation(
#                     rule_name=rule.rule_applied,
#                     json_spec=rule.rule_applied_data,
#                     source_file=source_file,
#                     target_files=targets_obj,
#                     rule_description=rule.description or ""
#                 )
#                 print(f"[14.2] Custom rule {rule.id} produced {len(resultLog2)} logs.")
#                 new_logs_list.append(pd.DataFrame(resultLog2, columns=["primary_field", "rule_data", "time"]))

#             if new_logs_list:
#                 all_new_logs = pd.concat(new_logs_list, ignore_index=True)
#                 final_log = pd.concat([existing_log, all_new_logs], ignore_index=True)
#             else:
#                 final_log = existing_log

#             with pd.ExcelWriter(log_file_path, engine="openpyxl", mode="w") as writer:
#                 final_log.to_excel(writer, index=False)
#             print("[16] Final log written to Excel.")

#             # Update DataFile validation status
#             data_file = models.DataFile.objects.filter(data_object=data_object, version=0).first()
#             if data_file:
#                 data_file.validation = 1
#                 data_file.validated_at = timezone.now()
#                 data_file.save()
#                 print("[17] DataFile validation updated.")

#             # Mark progress complete
#             update_progress(task_id, 100, "Validation completed successfully")
#             print("[18] Validation completed successfully.")

#             context["success"] = 1
#             context["message"] = "Validation completed successfully."
#             context["data"]["task_id"] = task_id  # return UUID to frontend if needed
#             return Response(context, status=status.HTTP_200_OK)

#         except Exception as e:
#             update_progress(task_id, 0, f"Error: {str(e)}")
#             print("[ERROR]", str(e))
#             context["message"] = str(e)
#             return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

