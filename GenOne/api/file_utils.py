import os
from django.conf import settings

def get_file_path_with_object_name(object_name):
    """
    Returns the full path of the file for a given objectName inside MEDIA_ROOT.
    Assumes there is always a single file in the folder.

    Args:
        object_name (str): Name of the object (folder under MEDIA_ROOT)

    Returns:
        str or None: Full file path if exists, else None
    """
    object_folder = os.path.join(settings.MEDIA_ROOT, object_name.lower())

    if not os.path.exists(object_folder):
        return None  # Folder doesn't exist

    # List all files in folder
    files = [f for f in os.listdir(object_folder) if os.path.isfile(os.path.join(object_folder, f))]

    if not files:
        return None  # No file found

    # Return full path of the single file
    return os.path.join(object_folder, files[0])


def get_target_specs(json_spec):
    targets = json_spec.get("target", [])
    if not isinstance(targets, list):
        return []
    return list(set([t.get("spec") for t in targets if "spec" in t]))


import os
import glob

BASE_DIR = os.path.join(settings.MEDIA_ROOT)  # adjust if absolute

def get_file_paths(object_name, file_name):
    # Data file path
    data_file_path = os.path.join(BASE_DIR, str(object_name).lower(), file_name)

    # Log folder path
    log_folder = os.path.join(BASE_DIR, str(object_name).lower(), "Log")

    log_file_path = None
    if os.path.exists(log_folder):
        log_files = glob.glob(os.path.join(log_folder, "*"))
        if log_files:
            # pick the latest log file by modified time
            log_file_path = max(log_files, key=os.path.getmtime)

    return data_file_path, log_file_path
