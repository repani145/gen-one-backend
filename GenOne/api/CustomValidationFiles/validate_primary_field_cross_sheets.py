import pandas as pd
from datetime import datetime, timezone

def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

def validate_primary_field_cross_sheets(file_path, primary_field):
    """
    Validate primary field across multiple sheets in a local Excel file.
    Primary values in all the tabs should be available in base/main tab.

    Args:
        file_path (str): Path to Excel file (.xlsx).
        primary_field (str): Primary column name to validate (e.g., "MATNR").

    Returns:
        list: Validation errors [value, reason, timestamp].
    """
    errors = []
    error_set = set()

    # ✅ Open Excel safely
    with pd.ExcelFile(file_path) as xls:
        # Load mapping sheet
        try:
            mapping_df = xls.parse("mapping")
        except ValueError:
            return errors

        # Step 1: Get unique tab names from Column C (from row 3 downward)
        tab_names_raw = mapping_df.iloc[2:, 2].dropna().unique().tolist()
        tab_names = [name for name in tab_names_raw if str(name).strip()]

        if len(tab_names) < 2:
            return errors

        # Step 2: Get base tab values (first tab in mapping)
        try:
            first_df = xls.parse(tab_names[0])
        except ValueError:
            return errors

        if primary_field not in first_df.columns:
            return errors

        base_values = set(first_df[primary_field].dropna().astype(str))

        # Step 3: Validate other tabs
        for sheet_name in tab_names[1:]:
            if sheet_name not in xls.sheet_names:
                continue

            df = xls.parse(sheet_name)
            if primary_field not in df.columns:
                continue

            for val in df[primary_field].dropna().astype(str):
                if val not in base_values:
                    add_error(
                        val,
                        f"{sheet_name} {primary_field} not found in base tab {tab_names[0]}",
                        error_set,
                        errors
                    )

    # ✅ File closed here automatically
    return errors




# def validate_primary_field_cross_sheets(file_path, primary_field):
#     """
#     Validate primary field across multiple sheets in a local Excel file.
#     Primary values in all the tabs should be available in base/main tab

#     Args:
#         file_path (str): Path to Excel file (.xlsx).
#         primary_field (str): Primary column name to validate (e.g., "MATNR").

#     Returns:
#         list: Validation errors [value, reason, timestamp].
#     """

#     # Load mapping sheet (must exist)
#     try:
#         mapping_df = pd.read_excel(file_path, sheet_name="mapping")
#     except Exception:
#         return []

#     # Step 1: Get unique tab names from Column C (from row 3 downward)
#     tab_names_raw = mapping_df.iloc[2:, 2].dropna().unique().tolist()
#     tab_names = [name for name in tab_names_raw if str(name).strip()]

#     if len(tab_names) < 2:
#         return []

#     # Step 2: Get MATNR values from the first tab
#     try:
#         first_df = pd.read_excel(file_path, sheet_name=tab_names[0])
#     except Exception:
#         return []

#     if primary_field not in first_df.columns:
#         return []

#     matnr_set = set(first_df[primary_field].dropna().astype(str))

#     errors = []
#     error_set = set()

#     # Step 3: Validate against other tabs
#     for sheet_name in tab_names[1:]:
#         try:
#             df = pd.read_excel(file_path, sheet_name=sheet_name)
#         except Exception:
#             continue

#         if primary_field not in df.columns:
#             continue

#         for val in df[primary_field].dropna().astype(str):
#             if val not in matnr_set:
#                 add_error(val, f"{sheet_name} {primary_field} not found in base tab {tab_names[0]}", error_set, errors)
#                 '''errors.append([
#                     val,
#                     f"{sheet_name} {primary_field} not found in base tab {tab_names[0]}",
#                     datetime.utcnow().isoformat()
#                 ])'''

#     return errors



## Usage of above code

# file_path = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# primary_field = "MATNR"

# errors = validate_primary_field_cross_sheets(file_path, primary_field)
# print(len(errors))
# for e in errors:
#     print(e)
