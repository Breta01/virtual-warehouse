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
    "custome": "custome",
}


def convert_type(type_str):
    try:
        return types[type_str.lower()]
    except:
        return "custome"


def convert_dim(dim, uom):
    if uom:
        return dim * dim_factors[uom.lower()]
    return dim


def convert_weight(weight, uom):
    if uom:
        return weight * weight_factors[uom.lower()]
    return weight


def convert_date(date, fmt="%d.%m.%Y"):
    if date:
        return datetime.strptime(date, fmt)
    return None


def create_gridmap(locations, resolution):
    pass
