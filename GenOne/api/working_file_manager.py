import os
import io
import shutil
import pandas as pd
from django.conf import settings
from . import models
from django.utils.timezone import now
from time import time

# def create_and_get_working_file_path(object_id):
#     """
#     Create a working copy of the latest file for the given object_id.
#     - Copies all existing sheets.
#     - Adds a 'mapping' tab with Specs data.
#     Returns the path to the new working file, or None if not found.
#     """
#     # Get latest version=0 file
#     latest_file = models.DataFile.objects.filter(data_object_id=object_id, version=0).first()
#     if not latest_file:
#         return None

#     # Extract file details
#     file_name = str(latest_file.file_name)
#     object_name = file_name.split(".")[0]

#     # Base dir inside MEDIA_ROOT
#     base_dir = os.path.join(settings.MEDIA_ROOT, str(object_name).lower())
#     original_file_path = os.path.normpath(os.path.join(base_dir, file_name))

#     if not os.path.exists(original_file_path):
#         return None

#     # Create working directory
#     working_dir = os.path.join(settings.MEDIA_ROOT, "working")
#     os.makedirs(working_dir, exist_ok=True)

#     # Define new working file path
#     working_file_path = os.path.join(working_dir, f"{object_name}_working.xlsx")

#     # Copy original file sheets + add mapping
#     xls = pd.ExcelFile(original_file_path)
#     with pd.ExcelWriter(working_file_path, engine="openpyxl") as writer:
#         # Copy existing sheets
#         for sheet in xls.sheet_names:
#             df = xls.parse(sheet)
#             df.to_excel(writer, sheet_name=sheet, index=False)

#         # Add mapping tab
#         data_object = models.DataObject.objects.filter(objectName=object_name).first()
#         if data_object:
#             spec_data = models.Specs.objects.filter(objectName=data_object.id).values()
#             if spec_data:
#                 spec_df = pd.DataFrame(spec_data)
#                 spec_df = spec_df.drop(columns=["id", "position"], errors="ignore")
#                 spec_df = spec_df.rename(columns={"objectName_id": "objectName"})
#                 spec_df["objectName"] = object_name
#                 spec_df.to_excel(writer, sheet_name="mapping", index=False)
    
#     # Build file name with timestamp
#     timestamp = now().strftime("%Y%m%d_%H%M%S")
#     file_name = f"{object_name}_Log_{timestamp}.xlsx"
#     file_path = os.path.join(base_dir, file_name)

#     # Create an empty DataFrame with required log structure
#     df = pd.DataFrame(columns=["primary_field", "rule_data", "time"])
#     df.to_excel(file_path, index=False)

#     return working_file_path




def create_and_get_working_file_path(object_id, retries=3, delay=1):
    """
    Create a working copy of the latest file for the given object_id.
    - Copies all existing sheets.
    - Adds a 'mapping' tab with Specs data.
    - Creates a log file with timestamp.
    Retries a few times if the file is locked.
    Returns the path to the new working file, or None if not found.
    """
    # Get latest version=0 file
    latest_file = models.DataFile.objects.filter(data_object_id=object_id, version=0).first()
    if not latest_file:
        return None

    # Extract file details
    file_name = str(latest_file.file_name)
    object_name = file_name.split(".")[0]

    # Base dir inside MEDIA_ROOT
    base_dir = os.path.join(settings.MEDIA_ROOT, str(object_name).lower())
    original_file_path = os.path.normpath(os.path.join(base_dir, file_name))

    if not os.path.exists(original_file_path):
        return None

    # Create working directory
    working_dir = os.path.join(settings.MEDIA_ROOT, "working")
    os.makedirs(working_dir, exist_ok=True)

    # Define new working file path
    working_file_path = os.path.join(working_dir, f"{object_name}_working.xlsx")
    working_log_file_path = os.path.join(working_dir, f"{object_name}_working_log.xlsx")

    with pd.ExcelWriter(working_log_file_path, engine="openpyxl") as writer:
        pd.DataFrame(columns=["primary_field", "rule_data", "time"]).to_excel(writer, index=False)

    # Retry loop in case of Windows file lock
    for attempt in range(retries):
        try:
            # Copy original file sheets + add mapping
            with pd.ExcelFile(original_file_path) as xls:
                with pd.ExcelWriter(working_file_path, engine="openpyxl") as writer:
                    # Copy existing sheets
                    for sheet in xls.sheet_names:
                        df = xls.parse(sheet)
                        df.to_excel(writer, sheet_name=sheet, index=False)

                    # Add mapping tab
                    data_object = models.DataObject.objects.filter(objectName=object_name).first()
                    if data_object:
                        spec_data = models.Specs.objects.filter(objectName=data_object.id).values()
                        if spec_data:
                            spec_df = pd.DataFrame(spec_data)
                            spec_df = spec_df.drop(columns=["id", "position"], errors="ignore")
                            spec_df = spec_df.rename(columns={"objectName_id": "objectName"})
                            spec_df["objectName"] = object_name
                            spec_df.to_excel(writer, sheet_name="mapping", index=False)
            break  # ✅ success, exit retry loop

        except PermissionError as e:
            if attempt < retries - 1:
                time.sleep(delay)  # wait before retry
            else:
                raise e

    # Ensure base_dir exists
    os.makedirs(base_dir, exist_ok=True)

    # Create logging directory inside base_dir
    logging_dir = os.path.join(base_dir, 'Log')
    os.makedirs(logging_dir, exist_ok=True)

    # Build file name with timestamp (for log file)
    timestamp = now().strftime("%Y%m%d_%H%M%S")
    log_file_name = f"{object_name}_Log_{timestamp}.xlsx"
    # log_file_path = os.path.join(logging_dir, log_file_name)

    # Create an empty DataFrame with required log structure
    # pd.DataFrame(columns=["primary_field", "rule_data", "time"]).to_excel(log_file_path, index=False)
    # with pd.ExcelWriter(log_file_path, engine="openpyxl") as writer:
    #     pd.DataFrame(columns=["primary_field", "rule_data", "time"]).to_excel(writer, index=False)

    return {'working_file_path':working_file_path,'working_log_file_path':working_log_file_path,"logging_dir":logging_dir,"log_file_name":log_file_name}


def delete_working_directory(working_file_path):
    """
    Deletes the 'working' directory inside MEDIA_ROOT after task completion.
    Returns True if deleted, False if not found.
    """
    # print("working_file_path =>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>at delete dir\n",working_file_path)

    working_dir = os.path.dirname(working_file_path)  # get directory path
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
        # shutil.rmtree(working_file_path)   # Recursively delete folder + contents
        return True
    return False

