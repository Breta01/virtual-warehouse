import datetime

from owlready2 import *

# We could use actual irl with already created ontologies
BASE_IRI = "http://warehouse/onto.owl"
onto = get_ontology(BASE_IRI)

with onto:

    class Country(Thing):
        pass

    class Inventory(Thing):
        pass

    class Item(Thing):
        pass

    class Location(Thing):
        def get_2d(self):
            return (self.has_x, self.has_y)

    class OrderedItem(Thing):
        pass

    class Order(Thing):
        @classmethod
        def create(
            cls,
            _id,
            direction,
            country_id,
            delivery_date,
            s_ship_date,
            a_ship_date,
            line_num,
            item_id,
            requested_qty,
            total_qty,
            qty_uom,
        ):
            country = onto.search_one(iri=f"{BASE_IRI}#{country_id}")
            if country is None:
                country = Country(country_id)

            item = onto.search(iri=f"{BASE_IRI}#{item_id}")
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
                has_ordered_item=oi,
            )

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

    class has_ordered_item(Order >> OrderedItem):
        pass

    # OrderedItem properties
    class has_item(ObjectProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [Item]

    class in_order(OrderedItem >> Order):
        inverse_property = has_ordered_item

    class has_requested_qty(DataProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [int]

    class has_total_qty(DataProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [int]

    class has_qty_uom(DataProperty, FunctionalProperty):
        domain = [OrderedItem]
        range = [str]

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
        domain = [Item]
        range = [str]

    # Location properties
    class has_items(Location >> Item):
        pass

    class has_ltype(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_lclass(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_lsubclass(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

    class has_length(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_width(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_height(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_max_weight(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [float]

    class has_zone(DataProperty, FunctionalProperty):
        domain = [Location]
        range = [str]

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

    class has_ltype(DataProperty, FunctionalProperty):
        domain = [Inventory]
        range = [str]

    # class has_item

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

    o1.has_ordered_item.append(io1)
    o2.has_ordered_item.append(io1)
    o2.has_ordered_item.append(io2)
    o3.has_ordered_item.append(io3)

    # sync_reasoner(infer_property_values=True)

    # SQLite3
    # default_world.graph.db
    # default_world.graph.execute

    ix = f"?p <{has_ordered_item.iri}> ?oi .\n"
    i = f"?oi <{has_item.iri}> ?item .\n"

    items = [i1, i2]
    itms = " ".join(map(lambda x: f"<{x.iri}>", items))
    ii = "VALUES ?item { " + itms + " }"

    q = "SELECT DISTINCT ?p WHERE { " + ix + i + ii + " }"
    print(q)
    r = list(default_world.sparql_query(q))
    print(r)
