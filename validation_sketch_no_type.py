# 1 - Validation Rules (User Input)
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

# 2 - Validator Registry (Function Dispatch)
TYPE_MAP = {
    "integer": int,
    "number": (int, float),
    "string": str,
    "boolean": bool,
    "array": list,
    "object": dict
}

VALIDATORS = {
    "equals": lambda actual, expected: actual == expected,
    "in": lambda actual, expected: actual in expected,
    "range": lambda actual, expected: expected[0] <= actual <= expected[1],
    "type": lambda actual, expected: isinstance(actual, TYPE_MAP[expected])
}

# 3 - Path Resolution (Nested Fields)
def get_by_path(data, path):
    current = data
    for key in path.split("."):
        current = current[key]
    return current


def safe_get_by_path(data, path):
    try:
        return get_by_path(data, path)
    except (KeyError, TypeError):
        return None

# 4 - Validation Result Structure
def make_result(field, rule, passed, actual, expected, message):
    return {
        "field": field,
        "rule": rule,
        "passed": passed,
        "actual": actual,
        "expected": expected,
        "message": message
    }

# 5 - Field Validation Logic
def validate_field(response, field_path, rules):
    results = []

    actual_value = safe_get_by_path(response, field_path)

    if actual_value is None:
        results.append(
            make_result(
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

        try:
            passed = validator(actual_value, expected)
        except Exception as exc:
            passed = False
            message = f"Validator error: {exc}"
        else:
            message = "OK" if passed else "Validation failed"

        results.append(
            make_result(
                field=field_path,
                rule=rule_name,
                passed=passed,
                actual=actual_value,
                expected=expected,
                message=message
            )
        )

    return results

# 6 - Validation Engine (Coordinator)
def validate_response(response, validation_rules):
    all_results = []

    for field_path, rules in validation_rules.items():
        field_results = validate_field(response, field_path, rules)
        all_results.extend(field_results)

    return all_results

# 7 - Summary & Aggregation
def summarize(results):
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success": failed == 0
    }

# 8 - Example Usage
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

# 9 - Example Output
[
  {
    'field': 'id',
    'rule': 'type',
    'passed': True,
    'actual': 123,
    'expected': 'integer',
    'message': 'OK'
  },
  {
    'field': 'price',
    'rule': 'range',
    'passed': False,
    'actual': 50,
    'expected': [0, 10],
    'message': 'Validation failed'
  }
]