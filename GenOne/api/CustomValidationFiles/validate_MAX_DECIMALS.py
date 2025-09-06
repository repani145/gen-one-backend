from datetime import datetime, timezone
import operator
import pandas as pd

# Mapping of operators
OP_MAP = {
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

def validate_MAX_DECIMALS(json_spec, source_file, rule_name):
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    op = json_spec["source"]["operator"]
    max_decimals = int(json_spec["source"]["values"][0])

    if op not in OP_MAP:
        raise ValueError(f"Unsupported operator: {op}")

    # Load source safely
    with pd.ExcelFile(source_file) as xl:
        df = pd.read_excel(xl, sheet_name=source_tab)

    # Function to count decimals
    def count_decimals(x):
        if pd.isna(x):
            return None
        try:
            s = str(x)
            return len(s.split(".")[1]) if "." in s else 0
        except:
            return 0

    # Count decimals
    df["decimals"] = df[src_field].apply(count_decimals)

    # Apply operator
    df["is_valid"] = df["decimals"].apply(lambda d: True if d is None else OP_MAP[op](d, max_decimals))

    # Collect errors
    errors = []
    error_set = set()
    for idx, row in df.iterrows():
        if not row["is_valid"]:
            add_error(row[src_primary], rule_name, error_set, errors)

    return errors


# def validate_MAX_DECIMALS(json_spec, source_file, rule_name):
#     source_tab = json_spec["source"]["tab"]
#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     op = json_spec["source"]["operator"]
#     max_decimals = int(json_spec["source"]["values"][0])

#     if op not in OP_MAP:
#         raise ValueError(f"Unsupported operator: {op}")

#     # Load source sheet
#     df = pd.read_excel(source_file, sheet_name=source_tab)    

#     # Function to count decimals
#     def count_decimals(x):
#         try:
#             s = str(x)
#             if "." in s:
#                 return len(s.split(".")[1])
#             return 0
#         except:
#             return 0
        
#     # Count decimals
#     df["decimals"] = df[src_field].apply(count_decimals)

#     # Apply operator
#     df["is_valid"] = df["decimals"].apply(lambda d: True if d is None else OP_MAP[op](d, max_decimals))

#     # Collect errors
#     errors = []
#     error_set = set()

#     for idx, row in df.iterrows():
#         if not row["is_valid"]:  # only invalids
#             add_error(row[src_primary], rule_name, error_set, errors)

#     return errors


def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)



# ## Usage of above code

# json_spec = {
#   "source": {
#     "spec": "material",
#     "tab": "material_accounting_data",
#     "primary_field": "MATNR",
#     "field": "STPRS",
#     "operator": "<=",
#     "values": [2]
#   }
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# rule_name = "material_accounting_data-STPRS should have less than or equal to 2 decimals only."

# errors = validate_MAX_DECIMALS(json_spec, source_file, rule_name)

# for e in errors:
#     print(e)
