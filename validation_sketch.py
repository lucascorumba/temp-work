"""
Overview

- Input
    - response body (dict)
    - swagger model (dict)
    - validation rules (dict, user-defined)

- Validation Engine
    - field extraction (dot paths)
    - rule execution (function registry)
    - type and presence checks (optional)
    - result aggregation

- Structured Results
    - per-field result
    - global summary
"""

# 2 - Validation rule format (user input)
rules = {
    "id": {
        "type": "integer",
        "equals": 123
    },
    "status": {
        "in": ["ACTIVE", "PENDING"]
    },
    "price": {
        "range": [0, 100]
    },
    "user.address.city": {
        "equals": "São Paulo"
    }
}

# 3- Validator Registry (Core Strategy Pattern)
from typing import Any, Callable

Validator = Callable[[Any, Any], bool]

VALIDATORS: dict[str, Validator] = {
    "equals": lambda actual, expected: actual == expected,
    "in": lambda actual, expected: actual in expected,
    "range": lambda actual, expected: expected[0] <= actual <= expected[1],
    "type": lambda actual, expected: isinstance(actual, _TYPE_MAP[expected])
}
# Type mapping
_TYPE_MAP = {
    "integer": int,
    "number": (int, float),
    "string": str,
    "boolean": bool,
    "array": list,
    "object": dicts
}

# 4 - Path resolution
def get_by_path(data: dict, path: str):
    current = data
    for key in path.split("."):
        current = current[key]
    return current

# -- Optional safety version
def safe_get_by_path(data: dict, path: str):
    try:
        return get_by_path(data, path)
    except (KeyError, TypeError):
        return None

# 5 - Validation result Model
from dataclass import dataclass

@dataclass
class ValidationResult:
    field: str
    rule: str
    passed: bool
    actual: Any
    expected: Any
    message: str

# 6 - Field validation logic
def validate_field(
    response: dict,
    field_path: str,
    rules: dict
) -> list[ValidationResult]:

    results = []

    actual_value = safe_get_by_path(response, field_path)

    if actual_value is None:
        results.append(
            ValidationResult(
                field=field_path,
                rule="exists",
                passed=False,
                actual=None,
                expected="field present",
                message="Field not found in response"
            )
        )
        return results
    
    for rule_name, expected in rules.items():
        validator = VALIDATORS.get(rule_name)

        if not validator:
            raise ValueError(f"Unknown validation rule: {rule_name}")

        passed = validator(actual_value, expected)

        results.append(
            ValidationResult(
                field=field_path,
                rule=rule_name,
                passed=passed,
                actual=actual_value,
                expected=expected,
                message="OK" if passed else "Validation failed"
            )
        )

    return results

# 7 - Validation Engine (coordinator)
def validate_response(
    response: dict,
    validation_rules: dict
) -> list[ValidationResult]:

    all_results = []

    for field_path, rules in validation_rules.items():
        field_results = validate_field(response, field_path, rules)
        all_results.extend(field_results)

    return all_results

# 8 - Summary and Reporting
def summarize(results: list[ValidationResult]) -> dict:
    total = len(results)
    passed = sum(r.passed for r in results)
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success": failed == 0
    }


# 9 - Example Usage

response = {
    "id": 123,
    "status": "ACTIVE",
    "price": 50,
    "user": {
        "address": {
            "city": "São Paulo"
        }
    }
}

results = validate_response(response, rules)
summary = summarize(results)


"""
Example output

id equals 123
status in ["ACTIVE", "PENDING"]
price range [0, 10]
user.address.city equals São Paulo

Summary:
- Total checks: 4
- Passed: 3
- Failed: 1
"""