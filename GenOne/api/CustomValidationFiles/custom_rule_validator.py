from .baseFile import VALIDATION_RULES

# ✅ Universal runner function
def run_custom_rule_validation(
    rule_name,
    json_spec={},
    source_file={},
    target_files=[],
    rule_description=''
):
    """
    Runs the appropriate validation function based on rule_name.
    Handles different argument signatures automatically.
    """

    if rule_name not in VALIDATION_RULES:
        raise ValueError(f"Unknown rule: {rule_name}")

    func = VALIDATION_RULES[rule_name]

    try:
        # ✅ Map available arguments dynamically
        return func(
            json_spec=json_spec,
            source_file=source_file,
            target_files=target_files,
            rule_name=rule_description,
        )
    except TypeError as e:
        # Call with only supported arguments
        import inspect

        sig = inspect.signature(func)
        valid_args = {
            k: v
            for k, v in {
                "json_spec": json_spec,
                "source_file": source_file,
                "target_files": target_files,
                "rule_name": rule_description,
            }.items()
            if k in sig.parameters
        }
        return func(**valid_args)

# result1 = run_validation("DATA_TYPE", json_spec=spec, source_file=src, rule_name="DATA_TYPE")
# result2 = run_validation("CUSTOM_LOOKUP", source_file=src, target_files=[tgt], dataJSON=my_data, rule_name="CUSTOM_LOOKUP")
# result3 = run_validation("ALLOWED_ONLY_IF", json_spec=spec, source_file=src, target_files=[tgt], rule_name="ALLOWED_ONLY_IF")




# # runner.py
# from .baseFile import VALIDATION_RULES

# def run_validation(rule_name, **kwargs):
#     """
#     Run validation rule dynamically with correct args.
    
#     Example:
#         run_validation("DATA_TYPE", json_spec=spec, source_file=src, rule_name="check_data")
#     """
#     rule = VALIDATION_RULES.get(rule_name)
#     if not rule:
#         return False, f"Validation rule '{rule_name}' not found"

#     func = rule["func"]
#     arg_names = rule["args"]

#     try:
#         # Pick only the required args from kwargs
#         call_args = [kwargs.get(arg) for arg in arg_names]
#         return func(*call_args)
#     except Exception as e:
#         return False, f"Error running {rule_name}: {str(e)}"


# # # Example 1
# # result = run_validation(
# #     "ALLOWED_ONLY_IF",
# #     json_spec=spec,
# #     source_file=src,
# #     target_files=tgt,
# #     rule_name="rule_1"
# # )

# # # Example 2
# # result = run_validation(
# #     "CUSTOM_LOOKUP",
# #     source_file=src,
# #     target_file=tgt,
# #     dataJSON=data,
# #     rule_name="lookup_rule"
# # )

# # # Example 3
# # result = run_validation(
# #     "MANDATORY",
# #     file_path="data.xlsx",
# #     primary_field="EmployeeID"
# # )
