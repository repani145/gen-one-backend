import pandas as pd
from datetime import datetime, timezone



def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

def validate_mandatory(file_path, primary_field):
    """
    Validate mandatory fields across sheets using mapping tab.

    Args:
        file_path (str): Path to Excel file.
        primary_field (str): Primary field column name (e.g., "LIFNR").

    Returns:
        list: Errors in format [primary_value, message, timestamp].
    """
    errors = []
    error_set = set()

    # ✅ Open Excel file safely
    with pd.ExcelFile(file_path) as xls:
        # Load mapping sheet
        try:
            mapping_df = xls.parse("mapping")
        except ValueError:
            # No mapping sheet
            return errors

        # Expected mapping columns: tabName = col[2], fieldName = col[3], mandatory = col[4]
        fields_data = {}
        for _, row in mapping_df.iterrows():
            tab_name = row.iloc[2]
            field_name = row.iloc[3]
            mandatory = row.iloc[4]
            if pd.isna(tab_name) or pd.isna(field_name):
                continue
            fields_data.setdefault(tab_name, []).append({
                "fieldName": str(field_name).strip(),
                "mandatory": str(mandatory).strip()
            })

        # Validate per tab
        for tab_name, fields in fields_data.items():
            if tab_name not in xls.sheet_names:
                continue  # Skip if sheet not found

            df = xls.parse(tab_name)

            if df.empty or primary_field not in df.columns:
                continue

            for field in fields:
                field_name = field["fieldName"]
                mandatory = field["mandatory"]

                if mandatory.lower() == "yes" and field_name in df.columns:
                    for _, row in df.iterrows():
                        primary_value = row[primary_field]
                        field_value = row[field_name]

                        if pd.notna(primary_value) and (pd.isna(field_value) or str(field_value).strip() == ""):
                            add_error(
                                primary_value,
                                f"{tab_name} - {field_name} - Missing mandatory field",
                                error_set,
                                errors
                            )

    # ✅ File auto-closed here
    return errors


# def validate_mandatory(file_path, primary_field):
#     """
#     Validate mandatory fields across sheets using mapping tab.

#     Args:
#         file_path (str): Path to Excel file.
#         primary_field (str): Primary field column name (e.g., "LIFNR").

#     Returns:
#         list: Errors in format [primary_value, message, timestamp].
#     """
#     errors = []
#     error_set = set()

#     # Load mapping sheet
#     mapping_df = pd.read_excel(file_path, sheet_name="mapping")

#     # Expected mapping columns: [ignored, ignored, tabName, fieldName, mandatory]
#     # Assuming tabName = col[2], fieldName = col[3], mandatory = col[4]
#     fields_data = {}
#     for _, row in mapping_df.iterrows():
#         tab_name = row.iloc[2]
#         field_name = row.iloc[3]
#         mandatory = row.iloc[4]
#         if pd.isna(tab_name) or pd.isna(field_name):
#             continue
#         if tab_name not in fields_data:
#             fields_data[tab_name] = []
#         fields_data[tab_name].append({
#             "fieldName": str(field_name).strip(),
#             "mandatory": str(mandatory).strip()
#         })

#     # Validate per tab
#     for tab_name, fields in fields_data.items():
#         try:
#             df = pd.read_excel(file_path, sheet_name=tab_name)
#         except ValueError:
#             # Sheet doesn't exist
#             continue

#         if df.empty or primary_field not in df.columns:
#             continue

#         # Check each field
#         for field in fields:
#             field_name = field["fieldName"]
#             mandatory = field["mandatory"]

#             if mandatory.lower() == "yes" and field_name in df.columns:
#                 for idx, row in df.iterrows():
#                     primary_value = row[primary_field]
#                     field_value = row[field_name]

#                     if pd.notna(primary_value) and (pd.isna(field_value) or str(field_value).strip() == ""):
#                         add_error(primary_value, f"{tab_name} - {field_name} - Missing mandatory field", error_set, errors)
#                         '''errors.append([
#                             primary_value,
#                             f"{tab_name} - {field_name} - Missing mandatory field",
#                             datetime.utcnow().isoformat()
#                         ])'''

#     return errors


## Usage of above code

# file_path = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# primary_col = "MATNR"

# errors = validate_mandatory(file_path, primary_col)
# print(len(errors))
# for e in errors:
#     print(e)
