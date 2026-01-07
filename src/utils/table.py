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
                if isinstance(value, list) and len(value) >= 2:
                    if value[0] == "button":
                        table_row.append(
                            {
                                "type": "button",
                                "text": str(value[1]) if value[1] is not None else "",
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
                        table_row.append(
                            {
                                "type": "link",
                                "text": str(value[1]) if value[1] is not None else "",
                                "href": str(value[2]) if value[2] is not None else "#",
                            }
                        )
                    else:
                        table_row.append(
                            {
                                "type": "text",
                                "value": str(value) if value is not None else "",
                            }
                        )
                else:
                    table_row.append(
                        {
                            "type": "text",
                            "value": str(value) if value is not None else "",
                        }
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

    def add_column(self, key, type, values):
        for row in self.table_data:
            processed_values = self._process_values(values, row)
            row[key] = [type] + processed_values
