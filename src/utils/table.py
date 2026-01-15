import copy
from .dynamic_objects import process_values, process_conditional_elements


class Table:
    def __init__(self, data):
        if not isinstance(data, list):
            data = [data]
        self.table_data = copy.deepcopy(data)

    def export_to_macro(self):
        table_data = []
        print(self.table_data)
        for row in self.table_data:
            table_row = []
            for key, value in row.items():
                if isinstance(value, list):
                    elements = self._process_list_value(value)
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

    def _process_list_value(self, value):
        elements = []

        if len(value) > 0 and isinstance(value[0], list):
            for element_def in value:
                elements.append(self._process_element_definition(element_def))
        elif len(value) >= 2:
            elements.append(self._process_simple_element(value))
        else:
            elements.append(self._create_text_element(value))

        return elements

    def _process_element_definition(self, element_def):
        if isinstance(element_def, list) and len(element_def) >= 2:
            element_type = element_def[0]

            if element_type == "button":
                return self._create_button_element(element_def)
            elif element_type == "link":
                return self._create_link_element(element_def)
            else:
                return self._process_other_element(element_def)
        else:
            return self._create_text_element(element_def)

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
        }

    def _process_other_element(self, element_def):
        if (
                isinstance(element_def, list)
                and len(element_def) >= 2
                and element_def[0] == "text"
        ):
            value_list = element_def[1] if len(element_def) > 1 else []
            if isinstance(value_list, list) and len(value_list) > 0:
                text_value = " ".join(str(v) for v in value_list)
            else:
                text_value = str(value_list)
            return {
                "type": "text",
                "value": text_value if text_value is not None else "",
            }
        else:
            return self._create_text_element(element_def)

    def _process_simple_element(self, value):
        if value[0] == "button":
            return self._create_simple_button_element(value)
        elif value[0] == "link":
            return self._create_simple_link_element(value)
        else:
            return self._create_text_element(value)

    def _create_simple_button_element(self, value):
        return {
            "type": "button",
            "text": str(value[1]) if value[1] is not None else "",
            "href": str(value[2]) if len(value) > 2 and value[2] is not None else "#",
            "icon": str(value[3]) if len(value) > 3 and value[3] is not None else None,
            "class_name": str(value[4])
            if len(value) > 4 and value[4] is not None
            else None,
        }

    def _create_simple_link_element(self, value):
        return {
            "type": "link",
            "text": str(value[1]) if value[1] is not None else "",
            "href": str(value[2]) if value[2] is not None else "#",
        }

    def _create_text_element(self, value):
        return {
            "type": "text",
            "value": str(value) if value is not None else "",
        }

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

    def set_type(self, key, type, values):
        for row in self.table_data:
            if key in row:
                original_value = row[key]
                processed_values = process_values(values, row)
                row[key] = [type, original_value] + processed_values

    def add_column(self, key, *args):
        for row in self.table_data:
            column_value = process_conditional_elements(args[0], row)
            row[key] = column_value

    def set_column_lang(self, lang, key):
        for row in self.table_data:
            if type(key) == list:
                for col in key:
                    row[key] = {
                        "value": row[key],
                        "lang": lang,
                    }
