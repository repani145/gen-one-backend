import re
import pandas as pd
from datetime import datetime, timezone

def parse_allowed_values(allowed_values):
    """
    Normalize allowed_values to a list of string tokens.
    Accepts:
      - actual Python lists/tuples/sets
      - strings like "[BG,DZN,EA]" or "BG,DZN" or "BG|DZN" or "BG;DZN"
      - single scalar values
    Returns: list of trimmed strings (no empty items)
    """
    if pd.isna(allowed_values) or allowed_values is None:
        return []

    # If it's already a list/tuple/set from excel parsing, use it directly
    if isinstance(allowed_values, (list, tuple, set)):
        vals = list(allowed_values)
    else:
        s = str(allowed_values).strip()
        # remove surrounding brackets/parentheses if present
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            s = s[1:-1].strip()
        # split on comma, pipe or semicolon
        parts = re.split(r'[,\|;]+', s)
        vals = [p.strip().strip("'\"") for p in parts if p.strip() != ""]

    # convert everything to strings (trimmed)
    return [str(v).strip() for v in vals if str(v).strip() != ""]


def check_value_in_string_generic(allowed_values, value):
    """
    Return True if `value` is considered allowed according to allowed_values.
    - blank/NaN values are treated as valid (skip check).
    - compares by string, then numeric (float), then case-insensitive.
    """
    if pd.isna(value) or value is None or (isinstance(value, str) and value.strip() == ""):
        return True

    allowed_list = parse_allowed_values(allowed_values)
    if not allowed_list:
        # If there are no allowed values configured, consider everything allowed (or change to False if desired)
        return True

    val_str = str(value).strip()

    # 1) direct string match
    if val_str in allowed_list:
        return True

    # 2) numeric match (handle decimal comma)
    try:
        val_num = float(val_str.replace(",", "."))
        for a in allowed_list:
            try:
                a_num = float(a.replace(",", "."))
                if val_num == a_num:
                    return True
            except Exception:
                continue
    except Exception:
        pass

    # 3) case-insensitive string match
    val_low = val_str.lower()
    for a in allowed_list:
        if val_low == a.lower():
            return True

    return False

def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

# Example integrated validate_allowed_values using the helper above
def validate_allowed_values(file_path, primary_field):
    errors = []
    error_set = set()

    # ✅ Load mapping sheet with context manager
    with pd.ExcelFile(file_path) as xls:
        mapping_df = pd.read_excel(xls, sheet_name="mapping")

        # expected columns: C = tabName, D = fieldName, F = allowableValues
        fields_data = {}
        for _, row in mapping_df.iterrows():
            tab_name = row.iloc[2]  
            field_name = row.iloc[3] 
            allowable_values = row.iloc[5]
            if pd.isna(tab_name) or pd.isna(field_name):
                continue
            fields_data.setdefault(tab_name, []).append({
                "fieldName": str(field_name).strip(),
                "allowableValues": allowable_values
            })

        # Loop over all tabs defined in mapping
        for tab_name, rules in fields_data.items():
            try:
                df = pd.read_excel(xls, sheet_name=tab_name)  # ✅ also uses same context
            except Exception:
                continue
            if df.empty or primary_field not in df.columns:
                continue

            for rule in rules:
                field_name = rule["fieldName"]
                allowable_values = rule["allowableValues"]
                if not allowable_values or field_name not in df.columns:
                    continue

                for _, row in df.iterrows():
                    primary_value = row[primary_field]
                    cell_value = row[field_name]
                    # if primary exists and value not allowed -> error
                    if pd.notna(primary_value) and not check_value_in_string_generic(allowable_values, cell_value):
                        add_error(primary_value, f"{tab_name} - {field_name} - Invalid Data.", error_set, errors)

    return errors




# def validate_allowed_values(file_path, primary_field):
#     errors = []
#     error_set = set()
#     mapping_df = pd.read_excel(file_path, sheet_name="mapping")

#     # expected columns: C = tabName, D = fieldName, F = allowableValues  (0-based: 2,3,5)
#     fields_data = {}
#     for _, row in mapping_df.iterrows():
#         tab_name = row.iloc[2]  
#         field_name = row.iloc[3] 
#         allowable_values = row.iloc[5]
#         if pd.isna(tab_name) or pd.isna(field_name):
#             continue
#         fields_data.setdefault(tab_name, []).append({
#             "fieldName": str(field_name).strip(),
#             "allowableValues": allowable_values
#         })

#     for tab_name, rules in fields_data.items():
#         try:
#             df = pd.read_excel(file_path, sheet_name=tab_name)
#         except Exception:
#             continue
#         if df.empty or primary_field not in df.columns:
#             continue

#         for rule in rules:
#             field_name = rule["fieldName"]
#             allowable_values = rule["allowableValues"]
#             if not allowable_values or field_name not in df.columns:
#                 continue

#             for _, row in df.iterrows():
#                 primary_value = row[primary_field]
#                 cell_value = row[field_name]
#                 # if primary exists and value not allowed -> error
#                 if pd.notna(primary_value) and not check_value_in_string_generic(allowable_values, cell_value):
#                     add_error(primary_value, f"{tab_name} - {field_name} - Invalid Data.", error_set, errors)

#     return errors



## Usage of above code

# file_path = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# primary_col = "MATNR"

# errors = validate_allowed_values(file_path, primary_col)
# print(len(errors))
# for e in errors:
#     print(e)
