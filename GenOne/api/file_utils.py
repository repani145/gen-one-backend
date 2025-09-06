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
