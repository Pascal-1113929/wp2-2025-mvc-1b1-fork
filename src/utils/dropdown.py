import re


class Dropdown:
    def __init__(self, data):
        self.dropdown_data = data

    def export_to_macro(self):
        options = []
        for item in self.dropdown_data:
            if isinstance(item, dict):
                options.append(
                    {
                        "value": str(item.get("value", "")),
                        "text": str(item.get("text", "")),
                        "selected": bool(item.get("selected", False)),
                    }
                )
            elif isinstance(item, list) and len(item) >= 2:
                options.append(
                    {
                        "value": str(item[0]) if item[0] is not None else "",
                        "text": str(item[1]) if item[1] is not None else "",
                        "selected": bool(item[2])
                        if len(item) > 2 and item[2] is not None
                        else False,
                    }
                )
            else:
                options.append(
                    {
                        "value": str(item) if item is not None else "",
                        "text": str(item) if item is not None else "",
                        "selected": False,
                    }
                )
        return options

    def _process_values(self, values, item):
        processed_values = []
        for val in values:
            if isinstance(val, str):
                result = val
                placeholders = re.findall(r"<([^>]+)>", val)
                for field_name in placeholders:
                    if isinstance(item, dict):
                        replacement = str(item.get(field_name, f"<{field_name}>"))
                    else:
                        replacement = f"<{field_name}>"
                    result = result.replace(f"<{field_name}>", replacement)
                processed_values.append(result)
            else:
                processed_values.append(val)
        return processed_values

    def set(self, key, format_string):
        for item in self.dropdown_data:
            if isinstance(item, dict):
                processed_values = self._process_values([format_string], item)
                item[key] = processed_values[0] if processed_values else ""
