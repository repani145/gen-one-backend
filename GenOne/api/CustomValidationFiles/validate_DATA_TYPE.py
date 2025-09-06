import pandas as pd
from datetime import datetime, timezone

import pandas as pd
from datetime import datetime

def validate_DATA_TYPE(json_spec, source_file, rule_name):
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    expected_dtype = json_spec["source"]["values"][0]  # e.g., "int", "float", "str", "date"

    dtype_map = {
        "int": int,
        "float": float,
        "str": str,
        "string": str,
        "bool": bool,
        "date": "date"
    }

    if expected_dtype not in dtype_map:
        raise ValueError(f"Unsupported dtype: {expected_dtype}")

    # Load Excel tab safely
    with pd.ExcelFile(source_file) as xl:
        df = pd.read_excel(xl, sheet_name=source_tab)

    def check_dtype(value):
        if pd.isna(value):
            return True

        if expected_dtype == "date":
            if isinstance(value, (datetime, pd.Timestamp)):
                return True
            try:
                pd.to_datetime(value, errors="raise")
                return True
            except Exception:
                return False
        else:
            target_type = dtype_map[expected_dtype]
            try:
                target_type(value)
                return True
            except (ValueError, TypeError):
                return False

    df["is_valid"] = df[src_field].apply(check_dtype)

    # Collect errors
    errors = []
    error_set = set()
    for idx, row in df.iterrows():
        if not row["is_valid"]:
            add_error(row[src_primary], rule_name, error_set, errors)

    return errors


# def validate_DATA_TYPE(json_spec, source_file, rule_name):
#     source_tab = json_spec["source"]["tab"]
#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     expected_dtype = json_spec["source"]["values"][0]  # e.g., "int", "float", "str", "date"

#     # Load Excel tab
#     df = pd.read_excel(source_file, sheet_name=source_tab)

#     dtype_map = {
#         "int": int,
#         "float": float,
#         "str": str,
#         "string": str,
#         "bool": bool,
#         "date": "date"
#     }

#     if expected_dtype not in dtype_map:
#         raise ValueError(f"Unsupported dtype: {expected_dtype}")

#     def check_dtype(value):
#         if pd.isna(value):   # Skip blanks
#             return True

#         if expected_dtype == "date":
#             # Check if already datetime type
#             if isinstance(value, (datetime, pd.Timestamp)):
#                 return True
#             try:
#                 # Try parsing string/number to date
#                 pd.to_datetime(value, errors="raise")
#                 return True
#             except Exception:
#                 return False

#         else:
#             target_type = dtype_map[expected_dtype]
#             try:
#                 target_type(value)
#                 return True
#             except (ValueError, TypeError):
#                 return False

#     df["is_valid"] = df[src_field].apply(check_dtype)

#     # Collect errors
#     errors = []
#     error_set = set()
#     for idx, row in df.iterrows():
#         if not row["is_valid"]:
#             add_error(row[src_primary], rule_name, error_set, errors)

#     return errors


def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)



## Usage of above code

# json_spec = {
#   "source": {
#     "spec": "material",
#     "tab": "material_accounting_data",
#     "primary_field": "MATNR",
#     "field": "PEINH",
#     "operator": "=",
#     "values": ['int']
#   }
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# rule_name = "material_accounting_data-PEINH should be integer"

# errors = validate_DATA_TYPE(json_spec, source_file, rule_name)

# print(len(errors))
# for e in errors:
#     print(e)
