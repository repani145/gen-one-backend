from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import DataObject, Specs, DataFile, RuleApplied

class DataObjectWriteLockPermission(BasePermission):
    """
    Blocks write operations on a DataObject and all related models
    if its related DataFile is marked as released OR request_progress=1.
    """

    def has_object_permission(self, request, view, obj):
        print("# ✅ Always allow safe (read-only) methods")
        if request.method in SAFE_METHODS:
            print(f"🔓 SAFE method {request.method} → allowed")
            return True

        related_obj = None
        print('--------------------------------------------->\n',obj,request)
        # Case 1: Direct DataObject
        if isinstance(obj, DataObject):
            related_obj = obj
            print(f"🟢 Case 1: Direct DataObject → {related_obj}")

        # Case 2: Specs has FK to DataObject
        elif hasattr(obj, "objectName") and isinstance(obj.objectName, DataObject):
            related_obj = obj.objectName
            print(f"🟢 Case 2: Specs → DataObject → {related_obj}")

        # Case 3: DataFile has FK to DataObject
        elif hasattr(obj, "data_object") and isinstance(obj.data_object, DataObject):
            related_obj = obj.data_object
            print(f"🟢 Case 3: DataFile → DataObject → {related_obj}")

        # Case 4: RuleApplied -> Spec -> DataObject
        elif hasattr(obj, "spec") and hasattr(obj.spec, "objectName"):
            related_obj = obj.spec.objectName
            print(f"🟢 Case 4: RuleApplied → Spec → DataObject → {related_obj}")

        if related_obj:
            # 🔒 Block if any related DataFile is locked
            locked = (
                related_obj.files.filter(version=0,release=True).exists() or
                related_obj.files.filter(version=0,request_progress=1).exists()
            )
            if locked:
                print(f"❌ Blocked {request.method} on {related_obj} "
                      f"(release=True or request_progress=1)")
                return False
            else:
                print(f"✅ Allowed {request.method} on {related_obj} (no lock)")
                return True

        print(f"⚠️ Unknown object type {obj.__class__.__name__}, default allow")
        return True
