"""Utils for parsing the Excel data."""

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


def convert_dim(dim, uom):
    return dim * dim_factor[uom.lower()]


def convert_weight(weight, uom):
    return weight * weight_factors[uom.lower()]


def create_gridmap(locations, resolution):
    pass
