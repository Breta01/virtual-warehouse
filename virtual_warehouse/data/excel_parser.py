"""Parser of Excel data files."""
from datetime import datetime

import xlsxio
from xlrd import open_workbook

from virtual_warehouse.data.data_model import (
    Inventory,
    Item,
    ItemUnit,
    Location,
    Order,
    RackLocation,
)
from virtual_warehouse.data.utils import convert_date, convert_type, estimate_sheet_type


class Document:
    """Document class which loads xls or xlsx file and parse different data objects."""

    def __init__(self, file_path):
        # Determines backend for loading documents (xlsx files uses openpyxl)
        self.is_xlsx = Document.check_xlsx(file_path)
        self.locations = {}
        self.items = {}
        self.balance = {}
        self.orders = {}
        if self.is_xlsx:
            self.doc = xlsxio.XlsxioReader(file_path)
        else:
            self.doc = open_workbook(file_path)

    @staticmethod
    def check_xlsx(file_path):
        """Check if document is .xlsx document (required for openpyxl library)."""
        return file_path[-5:] == ".xlsx"

    @staticmethod
    def get_sheet_names(file_path):
        """Get names of all sheets in document."""
        if Document.check_xlsx(file_path):
            with xlsxio.XlsxioReader(file_path) as reader:
                names = reader.get_sheet_names()
        else:
            doc = open_workbook(file_path, on_demand=True)
            names = doc.sheet_names()
        return [[n, estimate_sheet_type(n)] for n in names]

    def close(self):
        """Release resources owned by the document."""
        if self.is_xlsx:
            self.doc.close()

    def parse_locations(self, sheet_name="LOCATIONmaster"):
        """Parse LOCATIONmaster sheet."""
        if self.is_xlsx:
            types = [str, str, str, str, float, float, float, str, float, str, str]
            with self.doc.get_sheet(sheet_name, types=types) as sheet:
                sheet.read_header()
                for row in sheet.iter_rows():
                    if len(row) == 0 or not row[0]:
                        continue

                    location_id = row[0]
                    if convert_type(row[1]) == "rack":
                        self.locations[location_id] = RackLocation.create(*row[:11])
                    else:
                        self.locations[location_id] = Location.create(*row[:11])

        else:
            sheet = self.doc.sheet_by_name(sheet_name)

            for row in range(1, sheet.nrows):
                location_id = str(sheet.cell(row, 0).value)
                if not location_id:
                    continue

                values = [sheet.cell(row, i).value for i in range(11)]
                if convert_type(values[1]) == "rack":
                    self.locations[location_id] = RackLocation.create(*values)
                else:
                    self.locations[location_id] = Location.create(*values)

        return self.locations

    def parse_coordinates(self, sheet_name="XYZ_coordinates"):
        """Parse XYZ_coordinates sheet."""
        if self.is_xlsx:
            types = [str, float, float, float]
            with self.doc.get_sheet(sheet_name, types=types) as sheet:
                sheet.read_header()
                for row in sheet.iter_rows():
                    if len(row) == 0 or not row[0]:
                        continue
                    location_id = row[0]
                    self.locations[location_id].set_coord(*row[1:4])

        else:
            sheet = self.doc.sheet_by_name(sheet_name)

            for row in range(1, sheet.nrows):
                location_id = str(sheet.cell(row, 0).value)
                if not location_id:
                    continue

                self.locations[location_id].set_coord(
                    *(sheet.cell(row, i).value for i in range(1, 4))
                )

        return self.locations

    def parse_items(self, sheet_name="ITEMmaster"):
        """Parse ITEMmaster sheet."""
        if self.is_xlsx:
            types = [str, str, str, str] + 5 * [
                int,
                str,
                float,
                float,
                float,
                str,
                float,
                str,
            ]
            with self.doc.get_sheet(sheet_name, types=types) as sheet:
                sheet.read_header()
                for row in sheet.iter_rows():
                    if len(row) == 0 or not row[0]:
                        continue

                    item_id, description, gtype, zone = row[:4]
                    unit_levels = []
                    for col in range(4, len(row), 8):
                        unit_levels.append(
                            ItemUnit.create(f"{item_id}-u{col}", *row[col : col + 8],)
                        )
                    self.items[item_id] = Item.create(
                        item_id, description, gtype, zone, unit_levels[0], unit_levels
                    )

        else:
            sheet = self.doc.sheet_by_name(sheet_name)

            for row in range(1, sheet.nrows):
                item_id, description, gtype, zone = (
                    sheet.cell(row, i).value for i in range(4)
                )
                item_id = str(item_id)
                if not item_id:
                    continue

                unit_levels = []
                for col in range(4, sheet.ncols, 8):
                    unit_levels.append(
                        ItemUnit.create(
                            f"{item_id}-u{col}",
                            *(sheet.cell(row, col + i).value for i in range(8)),
                        )
                    )
                self.items[item_id] = Item.create(
                    item_id, description, gtype, zone, unit_levels[0], unit_levels
                )

        return self.items

    def parse_inventory_balance(self, sheet_name="Inventory Ballance"):
        """Parse Inventory Balance sheet  ('balance' in final version, most likely)."""
        if self.is_xlsx:
            types = [datetime, str, str, str, datetime, int, int, int, int, int]
            with self.doc.get_sheet(sheet_name, types=types) as sheet:
                sheet.read_header()
                for row in sheet.iter_rows():
                    if len(row) == 0 or not row[0]:
                        continue
                    date, location_id = row[:2]
                    if date not in self.balance:
                        self.balance[date] = {location_id: []}
                    elif location_id not in self.balance[date]:
                        self.balance[date][location_id] = []

                    self.balance[date][location_id].append(Inventory.create(*row[:10]))

        else:
            sheet = self.doc.sheet_by_name(sheet_name)

            for row in range(1, sheet.nrows):
                date = convert_date(sheet.cell(row, 0).value, "%d.%m.%Y")
                location_id = str(sheet.cell(row, 1).value)
                if not date:
                    continue

                if date not in self.balance:
                    self.balance[date] = {location_id: []}
                elif location_id not in self.balance[date]:
                    self.balance[date][location_id] = []

                self.balance[date][location_id].append(
                    Inventory.create(
                        date, *(sheet.cell(row, i).value for i in range(1, 10))
                    )
                )

        return self.balance

    def parse_orders(self, sheet_name="Order"):
        """Parse Order sheet."""
        if self.is_xlsx:
            types = [str, str, str, str, str, str, int, str, int, int, str]
            with self.doc.get_sheet(sheet_name, types=types) as sheet:
                sheet.read_header()
                for row in sheet.iter_rows():
                    if len(row) == 0 or not row[0]:
                        continue

                    order_id = row[0]
                    if order_id in self.orders:
                        self.orders[order_id].add_item(*row[7:11])
                    else:
                        self.orders[order_id] = Order.create(*row[:11])

        else:
            sheet = self.doc.sheet_by_name(sheet_name)

            for row in range(1, sheet.nrows):
                order_id = str(sheet.cell(row, 0).value)
                if not order_id:
                    continue

                if order_id in self.orders:
                    self.orders[order_id].add_item(
                        *(sheet.cell(row, i).value for i in range(7, 11))
                    )
                else:
                    self.orders[order_id] = Order.create(
                        *(sheet.cell(row, i).value for i in range(11))
                    )

        return self.orders

    def parse_document(self):
        """Parse the whole document."""
        locations = self.parse_locations()
        locations = self.parse_coordinates()
        items = self.parse_items()
        balance = self.parse_inventory_balance()
        orders = self.parse_orders()

        return locations, items, balance, orders
