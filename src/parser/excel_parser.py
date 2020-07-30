"""Parser of Excel data files."""
from pathlib import Path

from data_model import *
from xlrd import open_workbook


def parse_document(data_path):
    document = open_workbook(data_path)

    # Parse LOCATIONmaster sheet
    sheet = document.sheet_by_name("LOCATIONmaster")
    locations = {}
    for row in range(1, sheet.nrows):
        location_id = sheet.cell(row, 0).value
        if not location_id:
            continue

        locations[location_id] = Location(
            *(sheet.cell(row, i).value for i in range(11))
        )

    # Parse XYZ_coordinates sheet
    sheet = document.sheet_by_name("XYZ_coordinates")
    for row in range(1, sheet.nrows):
        location_id = sheet.cell(row, 0).value
        if not location_id:
            continue

        coord = Coord(*(sheet.cell(row, i).value for i in range(1, 4)))
        locations[location_id].set_coord(coord)

    # Parse ITEMmaster sheet
    sheet = document.sheet_by_name("ITEMmaster")
    items = {}
    for row in range(1, sheet.nrows):
        item_id, description, gtype, zone = (sheet.cell(row, i).value for i in range(4))
        if not item_id:
            continue

        unit_levels = []
        for col in range(4, sheet.ncols, 8):
            unit_levels.append(
                ItemUnit(*(sheet.cell(row, col + i).value for i in range(8)))
            )
        items[item_id] = Item(
            item_id, description, gtype, zone, unit_levels[0], unit_levels
        )

    # Parse Inventory Ballance sheet  ('balance' in final version, most likely)
    sheet = document.sheet_by_name("Inventory Ballance")
    balance = {}
    for row in range(1, sheet.nrows):
        date, location_id = sheet.cell(row, 0).value, sheet.cell(row, 1).value
        if not date:
            continue

        if not date in balance:
            balance[date] = {}
        balance[date][location_id] = Inventory(
            *(sheet.cell(row, i).value for i in range(10))
        )

    # Parse Order sheet
    sheet = document.sheet_by_name("Order")
    orders = []
    for row in range(1, sheet.nrows):
        order_id = sheet.cell(row, 0).value
        if not order_id:
            continue

        orders.append(Order(*(sheet.cell(row, i).value for i in range(11))))

    return locations, items, balance, orders


if __name__ == "__main__":
    data_file = Path(__file__).parent.joinpath("../assets/warehouse_data_v2.xlsx")
    locations, items, balance, orders = parse_document(data_file)
