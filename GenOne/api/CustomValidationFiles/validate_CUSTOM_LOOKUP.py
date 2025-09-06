import pandas as pd
from datetime import datetime, timezone

def get_column_index(df, field_name):
    try:
        return df.columns.get_loc(field_name)
    except KeyError:
        raise ValueError(f"Field '{field_name}' not found in dataframe columns.")

def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

import pandas as pd

def validate_CUSTOM_LOOKUP(source_file, target_files, json_spec, rule_name):
    errors = []
    error_set = set()

    source_tab = json_spec['source'][0]['tab']
    target_tab = json_spec['target'][0]['tab']

    source_primary_field = json_spec['source'][0]['primary_field']
    source_check_field = json_spec['source'][0]['field']
    target_primary_field = json_spec['target'][0]['primary_field']
    target_check_field = json_spec['target'][0]['field']

    # --- Load Source ---
    with pd.ExcelFile(source_file) as src_xl:
        source_df = pd.read_excel(src_xl, sheet_name=source_tab)

    # --- Load Target ---
    with pd.ExcelFile(target_files) as tgt_xl:
        target_df = pd.read_excel(tgt_xl, sheet_name=target_tab)

    # Create lookup dictionary
    target_dict = target_df.set_index(target_primary_field)[target_check_field].to_dict()

    for _, row in source_df.iterrows():
        primary_val = row.get(source_primary_field)

        if pd.notna(primary_val):
            check_val = row.get(source_check_field)
            target_val = target_dict.get(primary_val)

            if target_val is None:
                add_error(
                    primary_val,
                    f"{source_tab}-{source_primary_field} not found in {target_tab}-{target_primary_field}",
                    error_set,
                    errors
                )
            elif str(target_val) != str(check_val):
                add_error(primary_val, rule_name, error_set, errors)

    return errors




# ## Usage of above code
# dataJSON = {
#   "source": [
#     {
#       "spec": "material_master",
#       "tab": "Prices",
#       "primary_field": "MATNR",
#       "field": "STPRS"
#     }
#   ],
#   "target": [
#     {
#       "spec": "material_master",
#       "tab": "material_accounting_data",
#       "primary_field": "MATNR",
#       "field": "STPRS"
#     }
#   ]
# }

# source_file = 'D:/Learn/Py/files/Prices.xlsx'
# target_files = 'D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx'
# rule_name = "Price should match/found in material_accounting_data-STPRS"

# errors = validate_CUSTOM_LOOKUP(source_file, target_file, dataJSON, rule_name)

# for e in errors:
#     print(e)
