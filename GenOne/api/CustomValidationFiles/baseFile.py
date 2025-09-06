# baseFile.py
# This file imports all custom validation functions to make them accessible from a single module.

# CUSTOM VALIDATORS
from .validate_ALLOWED_ONLY_IF import validate_ALLOWED_ONLY_IF
from . validate_ALLOWED_TYPE_CONDITION import validate_ALLOWED_TYPE_CONDITION
from .validate_CUSTOM_LOOKUP import validate_CUSTOM_LOOKUP
from . validate_DATA_TYPE import validate_DATA_TYPE
from .validate_DEPENDS_ON_VALUE import validate_DEPENDS_ON_VALUE
from .validate_EMPTY_CONDITION import validate_EMPTY_CONDITION
from . validate_FIELD_LENGTH_CHECK import validate_FIELD_LENGTH_CHECK
from . validate_FIELD_VALUE_CHECK import validate_FIELD_VALUE_CHECK
from .validate_MAX_DECIMALS import validate_MAX_DECIMALS
from .validate_MUST_CONTAIN_SUBSTRING import validate_MUST_CONTAIN_SUBSTRING
from .validate_MUST_NOT_CONTAIN_SUBSTRING import validate_MUST_NOT_CONTAIN_SUBSTRING
from .validate_NOT_ALLOWED_TYPE_CONDITION import validate_NOT_ALLOWED_TYPE_CONDITION
from .validate_NOT_EMPTY_CONDITION import validate_NOT_EMPTY_CONDITION


# ✅ Registry (rule_name → function)
VALIDATION_RULES = {
    "ALLOWED_ONLY_IF": validate_ALLOWED_ONLY_IF,
    "ALLOWED_TYPE_CONDITION": validate_ALLOWED_TYPE_CONDITION,
    "CUSTOM_LOOKUP": validate_CUSTOM_LOOKUP,
    "DATA_TYPE": validate_DATA_TYPE,
    "DEPENDS_ON_VALUE": validate_DEPENDS_ON_VALUE,
    "EMPTY_CONDITION": validate_EMPTY_CONDITION,
    "FIELD_LENGTH_CHECK": validate_FIELD_LENGTH_CHECK,
    "FIELD_VALUE_CHECK": validate_FIELD_VALUE_CHECK,
    "MAX_DECIMALS": validate_MAX_DECIMALS,
    "MUST_CONTAIN_SUBSTRING": validate_MUST_CONTAIN_SUBSTRING,
    "MUST_NOT_CONTAIN_SUBSTRING": validate_MUST_NOT_CONTAIN_SUBSTRING,
    "NOT_ALLOWED_TYPE_CONDITION": validate_NOT_ALLOWED_TYPE_CONDITION,
    "NOT_EMPTY_CONDITION": validate_NOT_EMPTY_CONDITION,
}


