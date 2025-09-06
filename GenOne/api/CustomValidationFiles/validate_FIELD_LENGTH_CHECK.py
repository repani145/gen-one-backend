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

def validate_FIELD_LENGTH_CHECK(json_spec, source_file, rule_name):
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    op = json_spec["source"]["operator"]
    max_length = int(json_spec["source"]["values"][0])

    if op not in OP_MAP:
        raise ValueError(f"Unsupported operator: {op}")

    def compute_length(cell):
        # Return None for blanks or NaN
        if pd.isna(cell) or (isinstance(cell, str) and cell.strip() == "") or str(cell) in ["", "NaN"]:
            return None
        return len(str(cell))

    # Load source sheet safely
    with pd.ExcelFile(source_file) as xl:
        df = pd.read_excel(xl, sheet_name=source_tab)

    # Compute lengths
    df["length"] = df[src_field].apply(compute_length).astype("object")

    # Apply operator
    df["is_valid"] = df["length"].apply(lambda d: True if pd.isna(d) else OP_MAP[op](d, max_length))

    # Collect errors
    errors = []
    error_set = set()
    for idx, row in df.iterrows():
        if not row["is_valid"]:
            add_error(row[src_primary], rule_name, error_set, errors)

    return errors


# def validate_FIELD_LENGTH_CHECK(json_spec, source_file, rule_name):
#     source_tab = json_spec["source"]["tab"]
#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     op = json_spec["source"]["operator"]
#     max_length = int(json_spec["source"]["values"][0])

#     if op not in OP_MAP:
#         raise ValueError(f"Unsupported operator: {op}")
    
#     def compute_length(cell):
#     # If cell is NaN or empty string after stripping → return None
#         if pd.isna(cell) or (isinstance(cell, str) and cell.strip() == "") or str(cell) == "" or str(cell) == "NaN"  :
#             return None
#         return len(str(cell))

#     # Load source sheet
#     df = pd.read_excel(source_file, sheet_name=source_tab)    

#     # Compute length (only for non-blanks)
#     #df["length"] = df[src_field].astype(str).apply(lambda x: len(str(x)) if pd.notna(x) and str(x).strip() != "" else None)
#     df["length"] = df[src_field].apply(compute_length).astype("object")

#     #print(df["length"])

#     # Apply operator
#     df["is_valid"] = df["length"].apply(lambda d: True if pd.isna(d) else OP_MAP[op](d, max_length))

#     #print(df["is_valid"])

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
#     "tab": "material_basic_data",
#     "primary_field": "MATNR",
#     "field": "EAN11",
#     "operator": "=",
#     "values": [10]
#   }
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# rule_name = "material_accounting_data-EAN11 length should be equal to 10"

# errors = validate_FIELD_LENGTH_CHECK(json_spec, source_file, rule_name)

# print(len(errors))
# #for e in errors:
# #    print(e)
