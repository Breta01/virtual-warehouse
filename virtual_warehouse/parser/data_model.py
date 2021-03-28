"""Data model using Owlready2 ontology"""
import datetime
from typing import List

from owlready2 import *

from virtual_warehouse.parser.utils import (
    convert_date,
    convert_dim,
    convert_type,
    convert_weight,
)

# We could use actual irl with already created ontology
BASE_IRI = "http://warehouse/onto.owl"
onto = get_ontology(BASE_IRI)

with onto:

    class Country(Thing):
        """Class representing different countries."""

        pass

    class Inventory(Thing):
        """Description of inventory balance for given date and location."""

        @classmethod
        def create(
            cls,
            date: str,
            location_id: str,
            ltype: str,
            item_id: str,
            expiry_date: str,
            available_qty: int,
            onhand_qty: int,
            transi_qty: int,
            allocated_qty: int,
            suspense_qty: int,
        ):
            date_t = convert_date(date, "%d.%m.%Y")
            expiry_date = convert_date(expiry_date, "%d.%m.%Y")

            item = onto.search_one(iri=f"{BASE_IRI}#{item_id}")
            location = onto.search_one(iri=f"{BASE_IRI}#{location_id}")

            return cls(
                f"{date}-{location_id}",
                has_date=date_t,
                has_location=location,
                has_ltype=ltype,
                has_items=[item],
                has_expiry_date=expiry_date,
                has_availabel_qty=available_qty,
                has_onhand_qty=onhand_qty,
                has_transi_qty=transi_qty,
                has_allocated_qty=allocated_qty,
                suspense_qty=suspense_qty,
            )

    class ItemUnit(Thing):
        @classmethod
        def create(
            cls,
            _id: str,
            conversion_qty: int,
            qty_uom: str,
            length: float,
            width: float,
            height: float,
            dim_uom: str,
            weight: float,
            weight_uom: str,
        ):
            length = convert_dim(length, dim_uom)
            width = convert_dim(width, dim_uom)
            height = convert_dim(height, dim_uom)
            weight = convert_weight(weight, weight_uom)

            return cls(
                _id,
                has_conversion_qty=conversion_qty,
                has_qty_uom=qty_uom,
                has_length=length,
                has_width=width,
                has_weight=weight,
            )

    class Item(Thing):
        """Basic description of item, including packaging units."""

        @classmethod
        def create(
            cls,
            _id: str,
            description: str,
            gtype: str,
            zone: str,
            base_unit: ItemUnit,
            unit_levels: List[ItemUnit],
        ):
            return cls(
                _id,
                has_description=description,
                has_gtype=gtype,
                has_zone=zone,
                has_base_unit=base_unit,
                has_unit_levels=unit_levels,
            )

    class Location(Thing):
        """Description of location in warehouse."""

        @classmethod
        def create(
            cls,
            _id: str,
            ltype: str,
            lclass: str,
            lsubclass: str,
            length: float,
            width: float,
            height: float,
            dim_uom: str,
            max_weight: float = None,
            weight_uom: str = None,
            zone: str = None,
            # Params which are usually calculated later:
            x: float = None,
            y: float = None,
            z: float = None,
            freq: int = 0,
        ):
            ltype = convert_type(ltype)
            length = convert_dim(length, dim_uom)
            width = convert_dim(width, dim_uom)
            height = convert_dim(height, dim_uom)
            if max_weight:
                max_weight = convert_weight(max_weight, weight_uom)

            return cls(
                _id,
                has_ltype=ltype,
                has_lclass=lclass,
                has_lsubclass=lsubclass,
                has_length=length,
                has_width=width,
                has_height=height,
                has_max_weight=max_weight,
                has_zone=zone,
                has_x=x,
                has_y=y,
                has_z=z,
                has_freq=freq,
            )

        def set_coord(self, x, y, z):
            self.has_x, self.has_y, self.has_z = x, y, z

        def get_2d(self):
            return (self.has_x, self.has_y)

    class OrderedItem(Thing):
        """Description of item instance in order."""

        pass

    class Order(Thing):
        """Description of single order from warehouse."""

        @classmethod
        def create(
            cls,
            _id: str,
            direction: str,
            country_id: str,
            delivery_date: str,
            s_ship_date: str,
            a_ship_date: str,
            line_num: int,
            item_id: str,
            requested_qty: int,
            total_qty: int,
            qty_uom: str,
        ):
            # Convert to datetime
            delivery_date = convert_date(delivery_date, "%d.%m.%Y")
            s_ship_date = convert_date(s_ship_date, "%d.%m.%Y")
            a_ship_date = convert_date(a_ship_date, "%d.%m.%Y")

            country = onto.search_one(iri=f"{BASE_IRI}#{country_id}")
            if country is None:
                country = Country(country_id)

            item = onto.search_one(iri=f"{BASE_IRI}#{item_id}")
            oi = OrderedItem(
                f"{_id}-{item_id}",
                has_item=item,
                has_requested_qty=requested_qty,
                has_total_qty=total_qty,
                has_qty_uom=qty_uom,
            )

            return cls(
                _id,
                has_direction=direction,
                has_country=country,
                has_delivery_date=delivery_date,
                has_s_ship_date=s_ship_date,
                has_a_ship_date=a_ship_date,
                has_line_num=line_num,
                has_ordered_items=[oi],
            )

        def add_item(self, item_id, requested_qty, total_qty, qty_uom):
            item = onto.search_one(iri=f"{BASE_IRI}#{item_id}")
            oi = OrderedItem(
                f"{self.name}-{item_id}",
                has_item=item,
                has_requested_qty=requested_qty,
                has_total_qty=total_qty,
                has_qty_uom=qty_uom,
            )
            self.has_ordered_items.append()

    # Order properties
    class has_direction(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [str]

    class has_country(ObjectProperty, FunctionalProperty):
        domain = [Order]
        range = [Country]

    class has_delivery_date(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [datetime.datetime]

    class has_s_ship_date(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [datetime.date]

    class has_a_ship_date(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [datetime.date]

    class has_line_num(DataProperty, FunctionalProperty):
        domain = [Order]
        range = [int]

    class has_ordered_items(Order >> OrderedItem):
        pass

    # OrderedItem properties
    class has_item(ObjectProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [Item]

    class in_order(OrderedItem >> Order):
        inverse_property = has_ordered_items

    class has_requested_qty(DataProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [int]

    class has_total_qty(DataProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [int]

    class has_qty_uom(DataProperty, FunctionalProperty):
        domain = [OrderedItem, ItemUnit]
        range = [str]

    # ItemUnit properties
    class has_conversion_qty(DataProperty, FunctionalProperty):
        domain = [ItemUnit]
        range = [int]

    # class has_qty_uom(DataProperty, FunctionalProperty):
    # class has_length(DataProperty, FunctionalProperty):
    # class has_width(DataProperty, FunctionalProperty):
    # class has_height(DataProperty, FunctionalProperty):

    class has_weight(DataProperty, FunctionalProperty):
        domain = [ItemUnit]
        range = [float]

    # Item properties
    class in_order(Item >> OrderedItem):
        inverse_property = has_item

    class has_description(DataProperty, FunctionalProperty):
        domain = [Item]
        range = [str]

    class has_gtype(DataProperty, FunctionalProperty):
        domain = [Item]
        range = [str]

    class has_zone(DataProperty, FunctionalProperty):
        domain = [Item, Location]
        range = [str]

    class has_base_unit(ObjectProperty, FunctionalProperty):
        domain = [Item]
        range = [ItemUnit]

    class has_unit_levels(Item >> ItemUnit):
        pass

    # Location properties
    class has_ltype(DataProperty, FunctionalProperty):
        domain = [Location, Inventory]
        range = [str]

    class has_lclass(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_lsubclass(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_length(DataProperty, FunctionalProperty):
        domain = [Location, ItemUnit]
        range = [float]

    class has_width(DataProperty, FunctionalProperty):
        domain = [Location, ItemUnit]
        range = [float]

    class has_height(DataProperty, FunctionalProperty):
        domain = [Location, ItemUnit]
        range = [float]

    class has_max_weight(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    # class has_zone(DataProperty, FunctionalProperty):

    class has_coord(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_freq(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [int]

    class has_x(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_y(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_z(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    # Inventory properties
    class has_date(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [datetime.datetime]

    class has_location(ObjectProperty, FunctionalProperty):
        domain = [Inventory]
        range = [Location]

    # class has_ltype(DataProperty, FunctionalProperty):

    class has_items(Inventory >> Item):
        pass

    class has_expiry_date(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [datetime.datetime]

    class has_availabel_qty(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [int]

    class has_onhand_qty(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [int]

    class has_transi_qty(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [int]

    class has_allocated_qty(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [int]

    class has_supsense_qty(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [int]


if __name__ == "__main__":
    o1 = Order("o1", direction="out")
    o2 = Order("o2")
    o3 = Order("o3")
    Order("o4")
    Order("o5")
    i1 = Item("i1", has_for_direction="x1")

    i2 = Item("i2")
    i3 = Item("i3")

    io1 = OrderedItem("io1", has_item=i1)
    io2 = OrderedItem("io2", has_item=i2)
    io3 = OrderedItem("io3", has_item=i2)

    print("In", i2.in_order)

    o1.has_ordered_items.append(io1)
    o2.has_ordered_items.append(io1)
    o2.has_ordered_items.append(io2)
    o3.has_ordered_items.append(io3)

    # sync_reasoner(infer_property_values=True)

    # SQLite3
    # default_world.graph.db
    # default_world.graph.execute

    ix = f"?p <{has_ordered_items.iri}> ?oi .\n"
    i = f"?oi <{has_item.iri}> ?item .\n"

    items = [i1, i2]
    itms = " ".join(map(lambda x: f"<{x.iri}>", items))
    ii = "VALUES ?item { " + itms + " }"

    q = "SELECT DISTINCT ?p WHERE { " + ix + i + ii + " }"
    print(q)
    r = list(default_world.sparql_query(q))
    print(r)
