"""Data model using Owlready2 ontology."""
import datetime
from typing import List

from owlready2 import (
    DataProperty,
    FunctionalProperty,
    ObjectProperty,
    Thing,
    default_world,
    destroy_entity,
    get_ontology,
)

from virtual_warehouse.parser.utils import (
    convert_date,
    convert_dim,
    convert_type,
    convert_weight,
)

# We could use actual irl with already created ontology
BASE_IRI = "http://warehouse/onto.owl"
onto = get_ontology(BASE_IRI)


def destroy_all(cls):
    """Destroy all instances of given class.

    Args:
        cls (class): ontology class
    """
    for i in cls.instances():
        destroy_entity(i)


with onto:

    class Country(Thing):
        """Class representing different countries.

        Attributes:
            name (str): Name of the country
        """

        pass

    class Inventory(Thing):
        """Description of inventory balance for given date and location.
        TODO: Re-work the structure of inventory saving (individual items)

        Attributes:
            name (str): unique ID of inventory object
            has_date (datetime.datetime): date of the inventory status
            has_location (Location): location object related to this inventory status
            has_ltype (str): location type
            has_items (List[Item]): list of items on given location
            has_expiry_date (datetime.datetime): date of the item expiration
            has_availabel_qty (int): availabel quantity of the item
            has_onhand_qty (int): on-hand quantity of the item
            has_transi_qty (int): transiting quantity of the item
            has_allocated_qty (int): allocated quantity of the item
            has_suspense_qty (int): suspended quantity of the item
        """

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

        def add_item(self, item_id: str):
            item = onto.search_one(iri=f"{BASE_IRI}#{item_id}")
            self.has_items.append(item)

        @classmethod
        def destroy_all(cls):
            """Destroy all instances of Inventory class."""
            destroy_all(cls)

    class ItemUnit(Thing):
        """Represents different packaging units of item.

        Attributes:
            name (str): unique id (item_id-unit_lvl)
            has_conversion_qty (int): number of packages inside base unit
            has_qty_uom (str): name of unit
            has_length (float): length of packaging (in meters)
            has_width (float): width of packaging (in meters)
            has_height (float): height of packaging (in meters)
            has_weight (float): weight of packaging (in kg)
        """

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
                has_height=height,
                has_weight=weight,
            )

    class Item(Thing):
        """Basic description of item, including packaging units.

        Attributes:
            name (str): id of item
            has_description (str): description of items
            has_gtype (str): type of goods
            has_zone (str): required zone for storing item
            has_base_unit (ItemUnit): base packaging unit
            has_unit_levels (List[ItemUnit]): list of all different packaging units
        """

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

        @classmethod
        def destroy_all(cls):
            """Destroy all instances of Item class as well as related entities."""
            destroy_all(cls)
            destroy_all(ItemUnit)

        @staticmethod
        def get_by_locations(locations):
            """Get list of items stored at given location.

            Args:
               locations (List[Location]): list of locations to look for.

            Returns:
               List[Item]: list of items stored at locations
            """
            # TODO: Check inventory date
            values = " ".join(map(lambda x: f"<{x.iri}>", locations))
            i1 = "VALUES ?loc { " + values + " } .\n"
            i2 = f"?inv <{has_location.iri}> ?loc .\n"
            i3 = f"?inv <{has_items.iri}> ?item .\n"

            query = "SELECT DISTINCT ?item WHERE { " + i1 + i2 + i3 + " }"
            return list(default_world.sparql_query(query))

        @staticmethod
        def get_by_orders(orders):
            """Get list of items included in given orders.

            Args:
               orders (List[Order]): list of orders to search.

            Returns:
               List[Item]: list of items included in orders.
            """
            values = " ".join(map(lambda x: f"<{x.iri}>", orders))
            i1 = "VALUES ?ord { " + values + " } .\n"
            i2 = f"?ord <{has_ordered_items.iri}> ?oi .\n"
            i3 = f"?oi <{has_item.iri}> ?item .\n"

            query = "SELECT DISTINCT ?item WHERE { " + i1 + i2 + i3 + " }"
            return list(default_world.sparql_query(query))

    class Location(Thing):
        """Description of location in warehouse.

        Attributes:
            name (str): unique id of location
            has_ltype (str): type of location
            has_lclass (str): class of location
            has_lsubclass (str): subclass of location
            has_length (float): length of location
            has_width (float): width of location
            has_height (float): height of location
            has_max_weight (float): maximal weight which can location hold
            has_zone (str): zone where is location located
            has_x (float): x coordinate of location
            has_y (float): y coordinate of location
            has_z (float): z coordinate of location
            has_freq (int): frequency calculated for heat map displaying
        """

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

        def set_coord(self, x: float, y: float, z: float):
            """Additionally set coordinates of the location."""
            self.has_x, self.has_y, self.has_z = x, y, z  # skipcq: PYL-W0201

        def get_2d(self):
            """Get planar coordinates of location (used for top-down view)."""
            return (self.has_x, self.has_y)

        @classmethod
        def destroy_all(cls):
            """Destroy all instances of Location class."""
            destroy_all(cls)

        @staticmethod
        def get_by_orders(orders):
            """Get list of locations which are potentially accessed by given orders.

            Args:
               locations (List[Order]): list of locations to inspect

            Returns:
               List[Location]: list of locations containing ordered items
            """
            values = " ".join(map(lambda x: f"<{x.iri}>", orders))
            i1 = "VALUES ?ord { " + values + " } .\n"
            i2 = f"?ord <{has_ordered_items.iri}> ?oi .\n"
            i3 = f"?oi <{has_item.iri}> ?item .\n"
            i4 = f"?inv <{has_items.iri}> ?item .\n"
            i5 = f"?inv <{has_location.iri}> ?loc .\n"

            query = "SELECT DISTINCT ?loc WHERE { " + i1 + i2 + i3 + i4 + i5 + " }"
            return list(default_world.sparql_query(query))

        @staticmethod
        def get_by_items(items):
            """Get list of locations storing given items.

            Args:
               items (List[Item]): list of items to locate items.

            Returns:
               List[Location]: list of locations storing items
            """
            values = " ".join(map(lambda x: f"<{x.iri}>", items))
            i1 = "VALUES ?item { " + values + " } .\n"
            i2 = f"?inv <{has_items.iri}> ?item .\n"
            i3 = f"?inv <{has_location.iri}> ?loc .\n"

            query = "SELECT DISTINCT ?loc WHERE { " + i1 + i2 + i3 + " }"
            return list(default_world.sparql_query(query))

    class OrderedItem(Thing):
        """Description of item instance in order.

        Attributes:
            name (str): id of object (ordered_id-item_id)
            has_item (Item): item object instantiated by this order
            has_requested_qty (int): requested amount of item inside ordered
            has_total_qty (int): amount of item provided inside order
            qty_uom (int): unit of measure of quantities
        """

        pass

    class Order(Thing):
        """Description of single order from warehouse.

        Attributes:
            name (str): id of the order
            has_direction (str): outbound/inbound
            has_country (str): Country object representing shipping destination
            has_delivery_date (datetime.datetime): requested delivery date
            has_s_ship_date (datetime.datetime): scheduled sipping date
            has_a_ship_date (datetime.datetime): actual sipping date
            has_line_num (int): ERP order line number
            has_ordered_items (List[OrderedItem]): list of item instances inside order
        """

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
            _id = str(_id)
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

        def add_item(
            self, item_id: str, requested_qty: int, total_qty: int, qty_uom: str
        ):
            """Create and add item instance into order."""
            item = onto.search_one(iri=f"{BASE_IRI}#{item_id}")
            oi = OrderedItem(
                f"{self.name}-{item_id}",
                has_item=item,
                has_requested_qty=requested_qty,
                has_total_qty=total_qty,
                has_qty_uom=qty_uom,
            )
            self.has_ordered_items.append(oi)

        @classmethod
        def destroy_all(cls):
            """Destroy all instances of Order class as well as related entities."""
            destroy_all(cls)
            destroy_all(OrderedItem)

        @staticmethod
        def get_by_items(items):
            """Get list of orders which contains given items.

            Args:
               items (List[Item]): list of items to look for.

            Returns:
               List[Order]: list of orders containing at leas one of the provided items
            """
            values = " ".join(map(lambda x: f"<{x.iri}>", items))
            i1 = "VALUES ?item { " + values + " } .\n"
            i2 = f"?oi <{has_item.iri}> ?item .\n"
            i3 = f"?ord <{has_ordered_items.iri}> ?oi .\n"

            query = "SELECT DISTINCT ?ord WHERE { " + i1 + i2 + i3 + " }"
            return list(default_world.sparql_query(query))

        @staticmethod
        def get_by_locations(locations):
            """Get list of orders which potentially access given locations.

            Args:
               locations (List[Location]): list of locations to inspect

            Returns:
               List[Order]: list of orders containing items stored at given locations
            """
            values = " ".join(map(lambda x: f"<{x.iri}>", locations))
            i1 = "VALUES ?loc { " + values + " } .\n"
            i2 = f"?inv <{has_location.iri}> ?loc .\n"
            i3 = f"?inv <{has_items.iri}> ?item .\n"
            i4 = f"?oi <{has_item.iri}> ?item .\n"
            i5 = f"?ord <{has_ordered_items.iri}> ?oi .\n"

            query = "SELECT DISTINCT ?ord WHERE { " + i1 + i2 + i3 + i4 + i5 + " }"
            return list(default_world.sparql_query(query))

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

    class has_weight(DataProperty, FunctionalProperty):
        domain = [ItemUnit]
        range = [float]

    # Item properties
    class in_ordered_item(Item >> OrderedItem):
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


# sync_reasoner(infer_property_values=True)

# SQLite3
# default_world.graph.db
# default_world.graph.execute
