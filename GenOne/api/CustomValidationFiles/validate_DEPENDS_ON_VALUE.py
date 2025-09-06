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


def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

def validate_DEPENDS_ON_VALUE(json_spec, source_file, target_files, rule_name):
    """
    Validate: <Source Field> <op> [VALUE]
    IF all (<TargetX Field> <op> [VALUES]) are true.
    """
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    src_op = json_spec["source"]["operator"]
    src_values = json_spec["source"]["values"]

    if src_op not in OP_MAP:
        raise ValueError(f"Unsupported operator: {src_op}")

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

    # Collect errors
    errors = []
    error_set = set()

    for idx, row in source_df.iterrows():
        primary_value = row[src_primary]
        source_value = str(row[src_field]).strip()

        # --- Step 1: Check if all target conditions are satisfied ---
        targets_ok = []
        for t in target_maps:
            tgt_df = t["df"]
            spec = t["spec"]

            if primary_value not in tgt_df.index:
                targets_ok.append(False)
                add_error(
                    primary_value,
                    f"{source_tab}- {src_primary} not found in {spec['tab']} - {spec['primary_field']}",
                    error_set,
                    errors
                )
                break

            tgt_val = str(tgt_df.loc[primary_value, spec["field"]]).strip()
            op = spec["operator"]
            values = spec["values"]

            if op not in OP_MAP:
                raise ValueError(f"Unsupported operator: {op}")

            if isinstance(values, (list, tuple, set)):
                if not any(OP_MAP[op](tgt_val, v) for v in values):
                    targets_ok.append(False)
                    break
            else:
                if not OP_MAP[op](tgt_val, values):
                    targets_ok.append(False)
                    break

        # --- Step 2: If targets are satisfied, check source condition ---
        if all(targets_ok):
            if isinstance(src_values, (list, tuple, set)):
                if not any(OP_MAP[src_op](source_value, v) for v in src_values):
                    add_error(primary_value, rule_name, error_set, errors)
            else:
                if not OP_MAP[src_op](source_value, src_values):
                    add_error(primary_value, rule_name, error_set, errors)

    return errors


# def validate_DEPENDS_ON_VALUE(json_spec, source_file, target_files, rule_name):
#     """
#     Validate: <Source Field> <op> [VALUE]
#     IF all (<TargetX Field> <op> [VALUES]) are true.
#     """

#     # --- Load Source ---
#     source_tab = json_spec["source"]["tab"]
#     source_df = pd.read_excel(source_file, sheet_name=source_tab)

#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     src_op = json_spec["source"]["operator"]
#     src_values = json_spec["source"]["values"]

#     if src_op not in OP_MAP:
#         raise ValueError(f"Unsupported operator: {src_op}")

#     # Load targets with full row mapping
#     target_maps = []
#     for t in json_spec["target"]:
#         tgt_file = target_files[t["spec"]]
#         tgt_df = pd.read_excel(tgt_file, sheet_name=t["tab"])
#         tgt_df = tgt_df.set_index(t["primary_field"])
#         target_maps.append({"spec": t, "df": tgt_df})

#     # Collect errors
#     errors = []
#     error_set = set()

#     for idx, row in source_df.iterrows():
#         primary_value = row[src_primary]
#         source_value = str(row[src_field]).strip()

#         #print("#",source_value,"#")

#         # --- Step 1: Check if all target conditions are satisfied ---
#         targets_ok = []     # initialize True if error occured
#         for t in target_maps:
#             tgt_df = t["df"]
#             spec = t["spec"]

#             if primary_value not in tgt_df.index:
#                 # Target record missing
#                 targets_ok.append(False)
#                 add_error(primary_value, f"{source_tab}- {src_primary} not found in {t["spec"]['tab']} - {t["spec"]["primary_field"]}", error_set, errors)
#                 break

#             tgt_val = str(tgt_df.loc[primary_value, spec["field"]]).strip()

#             op = spec["operator"]
#             values = spec["values"]

#             if op not in OP_MAP:
#                 raise ValueError(f"Unsupported operator: {op}")

#             # Check condition
#             if isinstance(values, (list, tuple, set)):
#                 if not any(OP_MAP[op](tgt_val, v) for v in values):
#                     targets_ok.append(False)
#                     break
#             else:
#                 if not OP_MAP[op](tgt_val, values):
#                     targets_ok.append(False)
#                     break

#         # --- Step 2: If targets are satisfied, check source condition ---
#         if all(targets_ok):
#             if isinstance(src_values, (list, tuple, set)):
#                 if not any(OP_MAP[src_op](source_value, v) for v in src_values):
#                     add_error(primary_value, rule_name, error_set, errors)
#             else:
#                 if not OP_MAP[src_op](source_value, src_values):
#                     add_error(primary_value, rule_name, error_set, errors)
        

#     return errors



## Usage of above code

# json_spec = {
#   "source": {
#     "spec": "material1",
#     "tab": "material_plant_data",
#     "primary_field": "MATNR",
#     "field": "STRGR",
#     "operator": "=",
#     "values": ["40"]
#   },
#   "target": [
#     {
#       "spec": "material1",
#       "tab": "material_basic_data",
#       "primary_field": "MATNR",
#       "field": "MTART",
#       "operator": "=",
#       "values": ["ZFIN"]
#     },
#     {
#       "spec": "material1",
#       "tab": "material_plant_data",
#       "primary_field": "MATNR",
#       "field": "WERKS",
#       "operator": "=",
#       "values": ["4400"]
#     }
#   ]
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# target_files = {"material1": "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"}
# rule_name = "material_plant_data-STRGR=40 if material_basic_data- MTART=[FIN] AND WERKS=[4400]"

# errors = validate_DEPENDS_ON_VALUE(json_spec, source_file, target_files,rule_name)

# print(len(errors))
# for e in errors:
#     print(e)
