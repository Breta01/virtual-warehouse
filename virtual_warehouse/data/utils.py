"""Utils for parsing the Excel data."""
from datetime import datetime

dim_factors = {
    "m": 1,
    "meters": 1,
    "dm": 0.1,
    "cm": 0.01,
    "mm": 0.001,
}

weight_factors = {
    "kg": 1,
    "g": 0.001,
}

# Mapping possible names to standard types
types = {
    "floor": "floor",
    "rack": "rack",
    "storage rack": "rack",
    "wall": "wall",
    "inbound door": "inbound_door",
    "outbound door": "outbound_door",
    "staging area": "staging_area",
    "custom": "custom",
}


def estimate_sheet_type(sheet):
    """Estimate sheet type based on sheet name."""
    sheet = sheet.lower()
    if "coord" in sheet:
        return "Coordinates"
    if "loc" in sheet:
        return "Locations"
    if "item" in sheet:
        return "Items"
    if "inv" in sheet:
        return "Inventory"
    if "ord" in sheet:
        return "Orders"
    return "None"


def convert_type(type_str):
    """Unify location type names."""
    return types.get(" ".join(type_str.lower().split()), "custom")


def convert_dim(dim, uom):
    """Convert dimension size to meters."""
    if uom:
        return dim * dim_factors[uom.lower()]
    return dim


def convert_weight(weight, uom):
    """Convert weight to kilograms."""
    if uom:
        return weight * weight_factors[uom.lower()]
    return weight


def convert_date(date, fmt="%d.%m.%Y"):
    """Convert string date to datetime."""
    if type(date) is datetime:
        return date
    if date:
        return datetime.strptime(date, fmt)
    return None
