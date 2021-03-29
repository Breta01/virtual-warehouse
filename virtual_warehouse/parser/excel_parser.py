"""Parser of Excel data files."""
from pathlib import Path

from xlrd import open_workbook

from virtual_warehouse.parser.data_model import (
    Inventory,
    Item,
    ItemUnit,
    Location,
    Order,
)


def parse_locations(
    document,
    locations_sheet_name="LOCATIONmaster",
    coordinates_sheet_name="XYZ_coordinates",
):
    # Parse LOCATIONmaster sheet
    sheet = document.sheet_by_name(locations_sheet_name)
    locations = {}
    for row in range(1, sheet.nrows):
        location_id = str(sheet.cell(row, 0).value)
        if not location_id:
            continue

        locations[location_id] = Location.create(
            *(sheet.cell(row, i).value for i in range(11))
        )

    # Parse XYZ_coordinates sheet
    sheet = document.sheet_by_name(coordinates_sheet_name)
    for row in range(1, sheet.nrows):
        location_id = str(sheet.cell(row, 0).value)
        if not location_id:
            continue

        locations[location_id].set_coord(
            *(sheet.cell(row, i).value for i in range(1, 4))
        )

    return locations


def parse_items(document, sheet_name="ITEMmaster"):
    # Parse ITEMmaster sheet
    sheet = document.sheet_by_name(sheet_name)
    items = {}
    for row in range(1, sheet.nrows):
        item_id, description, gtype, zone = (sheet.cell(row, i).value for i in range(4))
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
        items[item_id] = Item.create(
            item_id, description, gtype, zone, unit_levels[0], unit_levels
        )

    return items


def parse_inventory_balance(document, sheet_name="Inventory Ballance"):
    # Parse Inventory Balance sheet  ('balance' in final version, most likely)
    sheet = document.sheet_by_name(sheet_name)
    balance = {}
    for row in range(1, sheet.nrows):
        date, location_id = sheet.cell(row, 0).value, sheet.cell(row, 1).value
        location_id = str(location_id)
        if not date:
            continue

        if date not in balance:
            balance[date] = {}
        balance[date][location_id] = Inventory.create(
            *(sheet.cell(row, i).value for i in range(10))
        )

    return balance


def parse_orders(document, sheet_name="Order"):
    # Parse Order sheet
    sheet = document.sheet_by_name("Order")
    orders = {}
    for row in range(1, sheet.nrows):
        order_id = str(sheet.cell(row, 0).value)
        if not order_id:
            continue

        if order_id in orders:
            orders[order_id].add_item(*(sheet.cell(row, i).value for i in range(7, 11)))
        else:
            orders[order_id] = Order.create(
                *(sheet.cell(row, i).value for i in range(11))
            )

    return orders


def parse_document(data_path):
    print("Data path:", data_path)
    document = open_workbook(data_path)

    locations = parse_locations(document)
    items = parse_items(document)
    balance = parse_inventory_balance(document)
    orders = parse_orders(document)

    return locations, items, balance, orders
