from datetime import datetime, timezone
import pandas as pd

def validate_MUST_CONTAIN_SUBSTRING(json_spec, source_file, rule_name):
    source_tab = json_spec["source"]["tab"]
    src_primary = json_spec["source"]["primary_field"]
    src_field = json_spec["source"]["field"]
    values = json_spec["source"]["values"]

    # Load source safely
    with pd.ExcelFile(source_file) as xl:
        df = pd.read_excel(xl, sheet_name=source_tab)

    # Compute match condition (True if any value is found in the cell)
    def contains_any(cell):
        if pd.isna(cell):
            return True  # skip blanks
        cell_str = str(cell)
        return any(v in cell_str for v in values)

    df["is_valid"] = df[src_field].apply(contains_any)

    # Collect errors
    errors = []
    error_set = set()

    for idx, row in df.iterrows():
        if not row["is_valid"]:
            add_error(row[src_primary], rule_name, error_set, errors)

    return errors


# def validate_MUST_CONTAIN_SUBSTRING(json_spec, source_file, rule_name):
#     source_tab = json_spec["source"]["tab"]
#     src_primary = json_spec["source"]["primary_field"]
#     src_field = json_spec["source"]["field"]
#     values = json_spec["source"]["values"]

#     # Load source sheet
#     df = pd.read_excel(source_file, sheet_name=source_tab)

#     # Compute match condition (True if any value is found in the cell)
#     df["is_valid"] = df[src_field].astype(str).apply(
#         lambda cell: any(v in cell for v in values)
#     )

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



## Usage of above code

# json_spec = {
#   "source": {
#     "spec": "material",
#     "tab": "material_basic_data",
#     "primary_field": "MATNR",
#     "field": "MATKL",
#     "operator": "",
#     "values": ["L003","L004"]
#   }
# }


# source_file = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# rule_name = "material_basic_data-MATKL should contain [L003,L004]"

# errors = validate_MUST_CONTAIN_SUBSTRING(json_spec, source_file, rule_name)

# for e in errors:
#     print(e)
