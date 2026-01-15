import copy
from .dynamic_objects import process_values, process_conditional_elements


class Table:
    def __init__(self, data):
        if not isinstance(data, list):
            data = [data]
        self.table_data = copy.deepcopy(data)

    def export_to_macro(self):
        table_data = []
        for row in self.table_data:
            table_row = []
            for key, value in row.items():
                processed_value = self._process_cell_value(value)
                table_row.append(processed_value)
            table_data.append(table_row)

        return table_data

    def _process_cell_value(self, value):
        if isinstance(value, list):
            return self._process_list_cell(value)
        elif isinstance(value, dict) and "type" in value:
            return [value]
        elif isinstance(value, dict) and "value" in value and "lang" in value:
            return [value]
        else:
            return [
                {
                    "type": "text",
                    "value": str(value) if value is not None else "",
                }
            ]

    def _process_list_cell(self, value):
        if not value:
            return [{"type": "text", "value": ""}]

        if isinstance(value[0], list):
            return [self._create_element(element_def) for element_def in value]
        else:
            return [self._create_element(value)]

    def _create_element(self, element_def):
        if not isinstance(element_def, list) or len(element_def) < 2:
            return {
                "type": "text",
                "value": str(element_def) if element_def is not None else "",
            }

        element_type = element_def[0]

        if element_type == "button":
            return self._create_button_element(element_def)
        elif element_type == "link":
            return self._create_link_element(element_def)
        elif element_type == "text":
            return self._create_text_element(element_def)
        else:
            return {
                "type": "text",
                "value": str(element_def[1]) if element_def[1] is not None else "",
            }

    def _create_button_element(self, element_def):
        return {
            "type": "button",
            "text": str(element_def[1]) if element_def[1] is not None else "",
            "href": str(element_def[2])
            if len(element_def) > 2 and element_def[2] is not None
            else "#",
            "icon": str(element_def[3])
            if len(element_def) > 3 and element_def[3] is not None
            else None,
            "class_name": str(element_def[4])
            if len(element_def) > 4 and element_def[4] is not None
            else None,
        }

    def _create_link_element(self, element_def):
        return {
            "type": "link",
            "text": str(element_def[1]) if element_def[1] is not None else "",
            "href": str(element_def[2]) if element_def[2] is not None else "#",
            "icon": str(element_def[3])
            if len(element_def) > 3 and element_def[3] is not None
            else None,
            "class_name": str(element_def[4])
            if len(element_def) > 4 and element_def[4] is not None
            else None,
        }

    def _create_text_element(self, element_def):
        if len(element_def) > 1 and isinstance(element_def[1], list):
            text_value = " ".join(str(v) for v in element_def[1] if v is not None)
        else:
            text_value = (
                str(element_def[1])
                if len(element_def) > 1 and element_def[1] is not None
                else ""
            )

        return {
            "type": "text",
            "value": text_value,
        }

    def remove_data(self, keys):
        keys = [keys] if isinstance(keys, str) else keys

        self.table_data = [
            {k: v for k, v in row.items() if k not in keys} for row in self.table_data
        ]

    def whitelist_data(self, keys):
        keys = [keys] if isinstance(keys, str) else keys

        self.table_data = [
            {k: v for k, v in row.items() if k in keys} for row in self.table_data
        ]

    def set_order(self, order):
        order = [order] if isinstance(order, str) else order

        new_data = []
        for row in self.table_data:
            ordered_row = {}
            for key in order:
                ordered_row[key] = row.get(key)
            new_data.append(ordered_row)

        self.table_data = new_data

    def set_type(self, key, element_type, values=None):
        values = values or []

        for row in self.table_data:
            if key in row:
                original_value = row[key]
                processed_values = process_values(values, row)

                if isinstance(original_value, dict) and "value" in original_value:
                    text_value = original_value["value"]
                    if element_type == "link":
                        row[key] = [element_type, text_value] + processed_values
                    elif element_type == "button":
                        row[key] = [element_type, text_value] + processed_values
                    else:
                        row[key] = [element_type] + processed_values + [original_value]
                else:
                    row[key] = [element_type] + processed_values + [original_value]

    def add_column(self, key, column_def):
        for row in self.table_data:
            column_value = process_conditional_elements(column_def, row)
            row[key] = column_value

    def set_column_lang(self, lang, keys):
        keys = [keys] if isinstance(keys, str) else keys

        for key in keys:
            for row in self.table_data:
                if key not in row or not row[key]:
                    continue

                value = row[key]
                if isinstance(value, dict) and "value" in value:
                    value["lang"] = lang
                else:
                    row[key] = {
                        "value": value,
                        "lang": lang,
                    }
