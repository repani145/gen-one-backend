import pandas as pd
from datetime import datetime, timezone


def add_error(valueA, valueB, error_set, errors):
    key = f"{valueA}|{valueB}"
    if key not in error_set:
        errors.append([valueA, valueB, datetime.now(timezone.utc).isoformat()])
        error_set.add(key)

def find_duplicates_in_each_sheet(file_path, primary_field):
    """
    Find duplicate rows in each sheet of an Excel file (ignoring 'mapping' sheet).

    Args:
        file_path (str): Path to the Excel file (.xlsx).
        primary_field (str): Column name used for duplicate reporting.

    Returns:
        list: List of errors in format [duplicate_value, message, timestamp].
    """
    errors = []
    error_set = set()

    # ✅ Use context manager to auto-close the ExcelFile
    with pd.ExcelFile(file_path) as all_sheets:
        for sheet_name in all_sheets.sheet_names:
            if sheet_name.lower() == "mapping":
                continue  # Skip mapping sheet

            # ✅ Each read_excel opens/closes independently
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            if df.empty or primary_field not in df.columns:
                continue

            # Create a "row signature" for duplicate detection
            df["_row_sig"] = df.astype(str).agg("|".join, axis=1)

            # Find duplicates based on the whole row
            duplicate_rows = df[df.duplicated("_row_sig", keep=False)]

            if not duplicate_rows.empty:
                grouped = duplicate_rows.groupby("_row_sig")
                for row_sig, group in grouped:
                    if len(group) > 1:  # Only log true duplicates
                        add_error(
                            group.iloc[0][primary_field],
                            f"Duplicate records found in sheet: {sheet_name}",
                            error_set,
                            errors
                        )

    # ✅ File auto-closed here
    return errors


# def find_duplicates_in_each_sheet(file_path, primary_field):
#     """
#     Find duplicate rows in each sheet of an Excel file (ignoring 'mapping' sheet).

#     Args:
#         file_path (str): Path to the Excel file (.xlsx).
#         primary_field (str): Column name used for duplicate reporting.

#     Returns:
#         list: List of errors in format [duplicate_value, message, timestamp].
#     """
#     errors = []
#     error_set = set()

#     # Load all sheets
#     all_sheets = pd.ExcelFile(file_path)

#     for sheet_name in all_sheets.sheet_names:
#         if sheet_name.lower() == "mapping":
#             continue  # Skip mapping sheet

#         df = pd.read_excel(file_path, sheet_name=sheet_name)

#         if df.empty or primary_field not in df.columns:
#             continue

#         # Create a "row signature" (like row.join('|')) for duplicate detection
#         df["_row_sig"] = df.astype(str).agg("|".join, axis=1)

#         # Find duplicates based on the whole row
#         duplicate_rows = df[df.duplicated("_row_sig", keep=False)]

#         if not duplicate_rows.empty:
#             grouped = duplicate_rows.groupby("_row_sig")
#             for row_sig, group in grouped:
#                 if len(group) > 1:  # Only log true duplicates
#                     #duplicate_value = group.iloc[0][primary_field]
#                     add_error(group.iloc[0][primary_field], f"Duplicate records found in sheet: {sheet_name}", error_set, errors)
#                     '''errors.append([
#                         duplicate_value,
#                         f"Duplicate records found in sheet: {sheet_name}",
#                         datetime.utcnow().isoformat()
#                     ])'''

#     return errors


## Usage of above code

# file_path = "D:/Learn/Py/files/Material_Data_Dallas_23June2025.xlsx"
# primary_field = "MATNR"

# errors = find_duplicates_in_each_sheet(file_path, primary_field)
# print(len(errors))
# for e in errors:
#     print(e)