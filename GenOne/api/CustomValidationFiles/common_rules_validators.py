# common_validators.py
from .validate_allowed_values import validate_allowed_values
from .validate_find_duplicates_in_each_sheet import find_duplicates_in_each_sheet
from .validate_mandatory import validate_mandatory
from .validate_primary_field_cross_sheets import validate_primary_field_cross_sheets


# Group all default validators in one place
DEFAULT_VALIDATORS = [
    validate_allowed_values,
    find_duplicates_in_each_sheet,
    validate_mandatory,
    validate_primary_field_cross_sheets,
]

import pandas as pd
from django.utils.timezone import now
# from api.views import update_progress

def run_default_validators(file_path, log_file_path, update_progress_fun, primary_field=None, task_id=None):
    """
    Run all default validators in sequence with a common primary_field argument.
    Updates progress in PROGRESS_STORE if task_id is provided.
    """
    results = []

    for i, validator in enumerate(DEFAULT_VALIDATORS):
        try:
            result = validator(file_path, primary_field)
            results.append(result)
        except Exception as e:
            print(f"[Validator ERROR] {validator.__name__}: {e}")
            pass

        # Update progress for each validator
        if task_id:
            # Calculate incremental progress contribution (40% for this function)
            total_validators = len(DEFAULT_VALIDATORS)
            progress = int((i + 1) / total_validators * 50) + 10  # +30 because this step starts after 30% from previous steps
            update_progress_fun(task_id, progress, f"Running default validator {i+1}/{total_validators}")

    # Read existing log file if exists
    try:
        with open(log_file_path, "rb") as f:
            existing_log = pd.read_excel(f)
    except FileNotFoundError:
        existing_log = pd.DataFrame(columns=["primary_field", "rule_data", "time"])

    # Flatten results: pick only non-empty child arrays
    flat_results = [item for sublist in results for item in sublist if sublist]

    # Convert into DataFrame
    if flat_results:
        new_log = pd.DataFrame(flat_results, columns=["primary_field", "rule_data", "time"])
    else:
        new_log = pd.DataFrame(columns=["primary_field", "rule_data", "time"])

    # Merge old + new logs
    final_log = pd.concat([existing_log, new_log], ignore_index=True)

    # Save to Excel
    with pd.ExcelWriter(log_file_path, engine="openpyxl", mode="w") as writer:
        final_log.to_excel(writer, index=False)

    return results


# def run_default_validators(file_path, log_file_path, primary_field=None):
#     """
#     Run all default validators in sequence with a common primary_field argument.
#     - Reads existing log file (if present).
#     - Appends results of each validator with timestamp.
#     - Saves back to the same log file.
#     Returns results as a list of arrays (one per validator).
#     """
    
#     results = []

    

#     # new_logs = []

#     for validator in DEFAULT_VALIDATORS:
#         try:
#             result = validator(file_path, primary_field)
#             results.append(result)

#         except Exception as e:
#             pass

#     try:
#         with open(log_file_path, "rb") as f:   # open for reading in binary
#             existing_log = pd.read_excel(f)
#     except FileNotFoundError:
#         existing_log = pd.DataFrame(columns=["primary_field", "rule_data", "time"])

#     # Flatten results: pick only non-empty child arrays
#     flat_results = [item for sublist in results for item in sublist if sublist]

#     # Convert into DataFrame
#     if flat_results:
#         new_log = pd.DataFrame(flat_results, columns=["primary_field", "rule_data", "time"])
#     else:
#         new_log = pd.DataFrame(columns=["primary_field", "rule_data", "time"])

#     # Merge old + new logs
#     final_log = pd.concat([existing_log, new_log], ignore_index=True)

#     # Always use ExcelWriter with context manager (ensures closing)
#     with pd.ExcelWriter(log_file_path, engine="openpyxl", mode="w") as writer:
#         final_log.to_excel(writer, index=False)

#     return results

