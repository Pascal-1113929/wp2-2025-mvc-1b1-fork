import re


class Table:
    def __init__(self, data):
        if not isinstance(data, list):
            data = [data]
        self.table_data = data

    def export_to_macro(self):
        table_data = []
        for row in self.table_data:
            table_row = []
            for key, value in row.items():
                if isinstance(value, list):
                    elements = []

                    if len(value) > 0 and isinstance(value[0], list):
                        for element_def in value:
                            if isinstance(element_def, list) and len(element_def) >= 2:
                                element_type = element_def[0]
                                if element_type == "button":
                                    elements.append(
                                        {
                                            "type": "button",
                                            "text": str(element_def[1])
                                            if element_def[1] is not None
                                            else "",
                                            "href": str(element_def[2])
                                            if len(element_def) > 2
                                            and element_def[2] is not None
                                            else "#",
                                            "icon": str(element_def[3])
                                            if len(element_def) > 3
                                            and element_def[3] is not None
                                            else None,
                                            "class_name": str(element_def[4])
                                            if len(element_def) > 4
                                            and element_def[4] is not None
                                            else None,
                                        }
                                    )
                                elif element_type == "link":
                                    elements.append(
                                        {
                                            "type": "link",
                                            "text": str(element_def[1])
                                            if element_def[1] is not None
                                            else "",
                                            "href": str(element_def[2])
                                            if element_def[2] is not None
                                            else "#",
                                        }
                                    )
                                else:
                                    elements.append(
                                        {
                                            "type": "text",
                                            "value": str(element_def)
                                            if element_def is not None
                                            else "",
                                        }
                                    )
                            else:
                                elements.append(
                                    {
                                        "type": "text",
                                        "value": str(element_def)
                                        if element_def is not None
                                        else "",
                                    }
                                )
                    elif len(value) >= 2:
                        if value[0] == "button":
                            elements.append(
                                {
                                    "type": "button",
                                    "text": str(value[1])
                                    if value[1] is not None
                                    else "",
                                    "href": str(value[2])
                                    if len(value) > 2 and value[2] is not None
                                    else "#",
                                    "icon": str(value[3])
                                    if len(value) > 3 and value[3] is not None
                                    else None,
                                    "class_name": str(value[4])
                                    if len(value) > 4 and value[4] is not None
                                    else None,
                                }
                            )
                        elif value[0] == "link":
                            elements.append(
                                {
                                    "type": "link",
                                    "text": str(value[1])
                                    if value[1] is not None
                                    else "",
                                    "href": str(value[2])
                                    if value[2] is not None
                                    else "#",
                                }
                            )
                        else:
                            elements.append(
                                {
                                    "type": "text",
                                    "value": str(value) if value is not None else "",
                                }
                            )
                    else:
                        elements.append(
                            {
                                "type": "text",
                                "value": str(value) if value is not None else "",
                            }
                        )

                    table_row.append(elements)
                else:
                    table_row.append(
                        [
                            {
                                "type": "text",
                                "value": str(value) if value is not None else "",
                            }
                        ]
                    )
            table_data.append(table_row)
        return table_data

    def remove_data(self, keys):
        if not isinstance(keys, list):
            keys = [keys]

        new_data = []
        for row in self.table_data:
            filtered_row = {k: v for k, v in row.items() if k not in keys}
            new_data.append(filtered_row)

        self.table_data = new_data

    def whitelist_data(self, keys):
        if not isinstance(keys, list):
            keys = [keys]

        new_data = []
        for row in self.table_data:
            filtered_row = {k: v for k, v in row.items() if k in keys}
            new_data.append(filtered_row)

        self.table_data = new_data

    def set_order(self, order):
        if not isinstance(order, list):
            order = [order]

        new_data = []
        for row in self.table_data:
            ordered_row = {}
            for key in order:
                if key in row:
                    ordered_row[key] = row[key]
                else:
                    ordered_row[key] = None
            new_data.append(ordered_row)

        self.table_data = new_data

    def _process_values(self, values, row):
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

    def set_type(self, key, type, values):
        for row in self.table_data:
            if key in row:
                original_value = row[key]
                processed_values = self._process_values(values, row)
                row[key] = [type, original_value] + processed_values

    def add_column(self, key, *args):
        for row in self.table_data:
            column_value = []
            for definition in args[0]:
                if isinstance(definition, list) and len(definition) >= 2:
                    element_type = definition[0]
                    element_values = definition[1] if len(definition) > 1 else []
                    processed_values = self._process_values(element_values, row)
                    column_value.append([element_type] + processed_values)
                else:
                    # Handle simple definition
                    column_value.append(definition)
            row[key] = column_value
