import re
from .dynamic_objects import process_values, process_conditional_elements


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

    def set(self, key, format_string):
        for item in self.dropdown_data:
            if isinstance(item, dict):
                processed_values = process_values([format_string], item)
                item[key] = processed_values[0] if processed_values else ""
