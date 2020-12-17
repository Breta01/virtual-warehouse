"""Data model for loading from Excel file."""
from dataclasses import InitVar, dataclass
from typing import List

from .utils import convert_date, convert_dim, convert_type, convert_weight


@dataclass(eq=True)
class Coord:
    """Location coordinates."""

    x: float = None
    y: float = None
    z: float = None

    def get_2d(self):
        return (self.x, self.y)


@dataclass
class ItemUnit:
    """Basic properties of item unit."""

    conversion_qty: int
    qty_uom: str
    length: float
    width: float
    height: float
    dim_uom: InitVar[str]
    weight: float
    weight_uom: InitVar[str]

    def __post_init__(self, dim_uom, weight_uom):
        self.length = convert_dim(self.length, dim_uom)
        self.width = convert_dim(self.width, dim_uom)
        self.height = convert_dim(self.height, dim_uom)
        self.weight = convert_weight(self.weight, weight_uom)


@dataclass
class Item:
    """Basic description of item, including packaging units."""

    id: str
    description: str
    gtype: str
    zone: str
    base_unit: ItemUnit
    unit_levels: List[ItemUnit]


@dataclass
class Location:
    """Description of location in warehouse."""

    id: str
    ltype: str
    lclass: str
    lsubclass: str
    length: float
    width: float
    height: float
    dim_uom: InitVar[str]
    max_weight: float = None
    weight_uom: InitVar[str] = None
    zone: str = None
    coord: Coord = None
    freq: int = 0

    def __post_init__(self, dim_uom, weight_uom):
        self.ltype = convert_type(self.ltype)
        self.length = convert_dim(self.length, dim_uom)
        self.width = convert_dim(self.width, dim_uom)
        self.height = convert_dim(self.height, dim_uom)
        if self.max_weight:
            self.max_weight = convert_weight(self.max_weight, weight_uom)

    def set_coord(self, coord):
        self.coord = coord


@dataclass
class Order:
    """Description of single order from warehouse."""

    id: int
    direction: str
    country: str
    delivery_date: str
    s_ship_date: str
    a_ship_date: str
    line_num: int
    item_id: str
    requested_qty: int
    total_qty: int
    qty_uom: str

    def __post_init__(self):
        self.delivery_date = convert_date(self.delivery_date, "%d.%m.%Y")
        self.s_ship_date = convert_date(self.s_ship_date, "%d.%m.%Y")
        self.a_ship_date = convert_date(self.a_ship_date, "%d.%m.%Y")


@dataclass
class Inventory:
    date: str
    location_id: str
    ltype: str
    item_id: str
    expiry_date: str
    available_qty: int
    onhand_qty: int
    transi_qty: int
    allocated_qty: int
    suspense_qty: int

    def __post_init__(self):
        self.date = convert_date(self.date, "%d.%m.%Y")
