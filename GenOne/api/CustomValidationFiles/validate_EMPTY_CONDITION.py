from datetime import datetime, timezone
import pandas as pd
import operator

# mapping of operator string → python function
OP_MAP = {
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b
}

def validate_EMPTY_CONDITION(json_spec, source_file, target_files, rule_name):
    """
    Validate source field against multiple target fields based on conditions.
    """
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]

    # --- Load Source safely ---
    with pd.ExcelFile(source_file) as xl_source:
        source_df = pd.read_excel(xl_source, sheet_name=source_tab)

    # --- Load Targets safely ---
    target_maps = []
    for t in json_spec["target"]:
        tgt_file = target_files[t["spec"]]
        with pd.ExcelFile(tgt_file) as xl_target:
            tgt_df = pd.read_excel(xl_target, sheet_name=t["tab"])
            tgt_df = tgt_df.set_index(t["primary_field"])
            target_maps.append({"spec": t, "df": tgt_df})

    errors = []
    error_set = set()

    for idx, row in source_df.iterrows():
        primary_value = row[src_primary]
        source_value = row[src_field]

        is_valid = []
        for t in target_maps:
            tgt_df = t["df"]

            # --- CASE 1: Primary not found in target ---
            if primary_value not in tgt_df.index:
                add_error(
                    primary_value,
                    f"{source_tab} - {src_primary} not found in {t['spec']['tab']} - {t['spec']['primary_field']}",
                    error_set,
                    errors
                )
                is_valid.append(False)
                break

            # --- CASE 2: Primary exists, check field value ---
            tgt_val = tgt_df.loc[primary_value, t["spec"]["field"]]
            op = t["spec"]["operator"]
            values = t["spec"]["values"]

            if op not in OP_MAP:
                raise ValueError(f"Unsupported operator: {op}")

            if isinstance(values, (list, tuple, set)):
                is_valid.append(any(OP_MAP[op](tgt_val, v) for v in values))
            else:
                is_valid.append(OP_MAP[op](tgt_val, values))

        # --- Step 3: Validate source value ---
        if all(is_valid) and not (pd.isna(source_value) or source_value == ""):
            add_error(primary_value, rule_name, error_set, errors)

    return errors


# def validate_EMPTY_CONDITION(json_spec, source_file, target_files, rule_name):
#     """
#     Validate source field against multiple target fields based on conditions.

#     Args:
#         json_spec (dict): Validation spec (source + targets).
#         source_file (str): Path to source Excel file.
#         target_files (dict): Dict mapping spec name -> Excel file path.

#     Returns:
#         pd.DataFrame: Validation errors (if any).
#     """
#     # --- Load Source ---
#     source_tab = json_spec["source"]["tab"]
#     source_df = pd.read_excel(source_file, sheet_name=source_tab)

#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]

#     # Load targets with full row mapping
#     target_maps = []
#     for t in json_spec["target"]:
#         tgt_file = target_files[t["spec"]]
#         tgt_df = pd.read_excel(tgt_file, sheet_name=t["tab"])

#         #df_indexed = tgt_df.set_index(t["primary_field"])
#         #df_indexed.index = df_indexed.index.astype(str).str.strip()

#         target_maps.append({
#             "spec": t,
#             "df": tgt_df.set_index(t["primary_field"])  # full rows indexed by primary field
#             #"df":df_indexed
#         })

#     # Collect errors
#     errors = []
#     error_set = set()

#     for idx, row in source_df.iterrows():
#         primary_value = row[src_primary]
#         source_value = row[src_field]

#         is_valid = []   # initialize True if error occured
#         for t in target_maps:
#             tgt_df = t["df"]
#             # --- CASE 1: Primary not found in target ---
#             if primary_value not in tgt_df.index:
#             #if primary_value not in tgt_df[primary_col].values:
#                 #print(primary_value, "missing")
#                 add_error(primary_value, f"{source_tab} - {src_primary} not found in {t["spec"]['tab']} - {t["spec"]["primary_field"]}", error_set, errors)
#                 is_valid.append(False)
#                 break

#             # --- CASE 2: Primary exists, check field value ---
#             tgt_val = tgt_df.loc[primary_value, t["spec"]["field"]]

#             op = t["spec"]["operator"]
#             values = t["spec"]["values"]

#             if op not in OP_MAP:
#                 raise ValueError(f"Unsupported operator: {op}")

#             if isinstance(values, (list, tuple, set)):
#                 is_valid.append( any(OP_MAP[op](tgt_val, v) for v in values) )
#             else:
#                 is_valid.append( OP_MAP[op](tgt_val, values) )

#         if all(is_valid) and not (pd.isna(source_value) or source_value == ""):
#                 '''add_error(primary_value, source_value, error_set, errors, 
#                           reason=f"Condition failed: {tgt_val} {op} {values}", 
#                           rownum=idx+2)'''
#                 add_error(primary_value, rule_name, error_set, errors)

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
#     "field": "EXTWG"
#   },
#   "target": [
#     {
#       "spec": "material1",
#       "tab": "material_basic_data",
#       "primary_field": "MATNR",
#       "field": "MTART",
#       "operator": "=",
#       "values": ["ZSEM"]
#     },
#     {
#       "spec": "material1",
#       "tab": "material_basic_data",
#       "primary_field": "MATNR",
#       "field": "LOT-TRACKED",
#       "operator": "=",
#       "values": ["X"]
#     }
#   ]
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# target_files = {"material1": "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"}
# rule_name = "material_basic_data-EXTWG should be empty if material_basic_data- MTART=[ZSEM] AND LOT-TRACKED=[X]"

# errors = validate_EMPTY_CONDITION(json_spec, source_file, target_files,rule_name)

# for e in errors:
#     print(e)
