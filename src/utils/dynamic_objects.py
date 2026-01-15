import re


def process_values(values, row):
    processed_values = []
    for val in values:
        if isinstance(val, str):
            result = val
            placeholders = re.findall(r"<([^>]+)>", val)
            for field_name in placeholders:
                replacement = str(row.get(field_name, f"<{field_name}>"))
                result = result.replace(f"<{field_name}>", replacement)
            processed_values.append(result)
        else:
            processed_values.append(val)
    return processed_values


def evaluate_condition(condition_str, row):
    match = re.search(r"^\{(.+)\}$", condition_str.strip())
    if not match:
        return False

    expr = match.group(1)

    placeholders = re.findall(r"<([^>]+)>", expr)
    for field_name in placeholders:
        field_value = row.get(field_name)
        if isinstance(field_value, str):
            replacement = f'"{field_value}"'
        else:
            replacement = str(field_value)
        expr = expr.replace(f"<{field_name}>", replacement)

    try:
        return eval(expr, {"__builtins__": {}}, {})
    except Exception:
        return False


def process_conditional_elements(definitions, row):
    column_value = []
    for definition in definitions:
        if isinstance(definition, list) and len(definition) >= 2:
            if (
                isinstance(definition[0], str)
                and definition[0].startswith("{")
                and definition[0].endswith("}")
            ):
                condition_str = definition[0]
                if evaluate_condition(condition_str, row):
                    element_type = definition[1]
                    element_values = definition[2] if len(definition) > 2 else []
                    processed_values = process_values(element_values, row)
                    column_value.append([element_type] + processed_values)
                else:
                    continue
            else:
                element_type = definition[0]
                element_values = definition[1] if len(definition) > 1 else []
                processed_values = process_values(element_values, row)
                column_value.append([element_type] + processed_values)
        else:
            column_value.append(definition)
    return column_value


def collapse_conditions(data):
    new_data = []
    for row in data:
        new_row = {}
        conditional_fields = {}

        for field_name, field_value in row.items():
            if (
                isinstance(field_name, str)
                and field_name.startswith("{")
                and field_name.endswith("}")
            ):
                conditional_fields[field_name] = field_value
            else:
                new_row[field_name] = field_value

        for condition_str, conditional_data in conditional_fields.items():
            if evaluate_condition(condition_str, new_row):
                if isinstance(conditional_data, dict):
                    for cond_key, cond_value in conditional_data.items():
                        new_row[cond_key] = cond_value
                else:
                    new_row[f"conditional_{len(new_row)}"] = conditional_data

        new_data.append(new_row)

    return new_data
