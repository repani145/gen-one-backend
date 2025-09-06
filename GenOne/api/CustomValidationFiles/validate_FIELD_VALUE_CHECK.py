import pandas as pd
from datetime import datetime, timezone
import operator
import numpy as np

# --- Operator map ---
OP_MAP = {
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
}

def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

# --- Helper: convert string to number/date if possible ---
def try_convert(val):
    """
    - If val is already numeric/datetime, return as-is.
    - If string, try int -> float (with comma->dot) -> datetime.
    - Otherwise return stripped string.
    """
    if pd.isna(val) or val is None:
        return val

    # if already numeric types (numpy or python) or datetime, return as-is
    if isinstance(val, (int, float, np.integer, np.floating)):
        return val
    if isinstance(val, (pd.Timestamp, datetime)):
        return val

    s = str(val).strip()

    # Try integer (only if looks like integer)
    try:
        # allow signs and digits only
        if s.lstrip("+-").isdigit():
            return int(s)
    except Exception:
        pass

    # Try float (handle decimal comma)
    try:
        s_float = s.replace(",", ".")
        # avoid parsing things like "1,000" -> 1.0 incorrectly; if there's both dot and comma, remove commas
        if "," in s and "." in s:
            s_float = s.replace(",", "")
        return float(s_float)
    except Exception:
        pass

    # Try datetime
    try:
        return pd.to_datetime(s, errors="raise")
    except Exception:
        pass

    # fallback to string
    return s


# --- Field values validation ---
def validate_FIELD_VALUE_CHECK(json_spec, source_file, rule_name):
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    op = json_spec["source"].get("operator", "in").lower()
    values = json_spec["source"]["values"]   # always list

    if op not in OP_MAP:
        raise ValueError(f"Unsupported operator: {op}")

    # Load Excel safely
    with pd.ExcelFile(source_file) as xl:
        df = pd.read_excel(xl, sheet_name=source_tab)

    # Prepare comparison value
    if op in ("in", "not in"):
        cmp_value = [try_convert(v) for v in values]
    else:
        cmp_value = try_convert(values[0])

    def check_value(v):
        if pd.isna(v) or v is None:  # Skip blanks
            return True
        v_conv = try_convert(v)
        try:
            return OP_MAP[op](v_conv, cmp_value)
        except Exception:
            return False

    df["is_valid"] = df[src_field].apply(check_value)

    # Collect errors
    errors = []
    error_set = set()
    for idx, row in df.iterrows():
        if not row["is_valid"]:
            add_error(row[src_primary], rule_name, error_set, errors)

    return errors



# def validate_FIELD_VALUE_CHECK(json_spec, source_file, rule_name):
#     source_tab = json_spec["source"]["tab"]
#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     op = json_spec["source"].get("operator", "in").lower()
#     values = json_spec["source"]["values"]   # always list

#     # Load Excel tab
#     df = pd.read_excel(source_file, sheet_name=source_tab)

#     if op in ("in", "not in"):
#         cmp_value = [try_convert(v) for v in values]
#     else:
#         # pick first element for single comparison operators
#         cmp_value = try_convert(values[0])

#     if op not in OP_MAP:
#         raise ValueError(f"Unsupported operator: {op}")

#     def check_value(v):
#         if pd.isna(v) or v is None:   # Skip blanks
#             return True
#         v_conv = try_convert(v)
#         try:
#             return OP_MAP[op](v_conv, cmp_value)
#         except Exception:
#             return False

#     df["is_valid"] = df[src_field].apply(check_value)



#     # Collect errors
#     errors = []
#     error_set = set()
#     for idx, row in df.iterrows():
#         if not row["is_valid"]:
#             add_error(row[src_primary], rule_name, error_set, errors)

#     return errors


## Usage of above code

# json_spec = {
#   "source": {
#     "spec": "material",
#     "tab": "material_accounting_data",
#     "primary_field": "MATNR",
#     "field": "STPRS",
#     "operator": ">",
#     "values": [0]
#   }
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# rule_name = "material_accounting_data-STPRS should be greater than 0"

# errors = validate_FIELD_VALUE_CHECK(json_spec, source_file, rule_name)

# print(len(errors))
# for e in errors:
#     print(e)
