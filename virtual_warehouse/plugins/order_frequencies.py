"""Module with plug-in for calculating selected items frequencies."""

from virtual_warehouse.plugin import BasePlugin


class Plugin(BasePlugin):
    """Sub-class of base plugin providing calculation of frequency.
    Calculate frequency as frequency of item in order.
    """

    display_name = "&Order Histogram"

    def __init__(self, locations, items, orders, inventory):
        """Initialize plugin and save required parameters.

        Args:
            locations (dict): dictionary of locations mapping id to locations
            items (dict): dictionary of items mapping id to items
            orders (dict): dictionary of orders mapping id to order
            inventory (dict): dictionary of specifying inventory
        """
        super().__init__(locations, items, orders, inventory)
        self.orders = orders
        self.item_locs = Plugin.item_locations(inventory)
        self.date = list(self.item_locs.keys())[-1]

    @staticmethod
    def item_locations(inventory):
        """Create dictionary mapping (date, item) to list of locations."""
        item_to_loc = {}
        for date, status in inventory.items():
            item_to_loc[date] = {}
            for loc_inventories in status.values():
                for inv in loc_inventories:
                    if inv.has_item.name not in item_to_loc[date]:
                        item_to_loc[date][inv.has_item.name] = []
                    item_to_loc[date][inv.has_item.name].append(inv.has_location)

        return item_to_loc

    def on_orders_update(self, clear, add, ids):
        """Update frequency calculation on orders check/uncheck.

        Args:
            clear (bool): Whether to clear previously selected orders.
            add (bool): Whether to add or remove ids from calculation.
            ids (list[str]): list of ids considered in calculation.
        """
        if clear:
            self._clear_frequencies()

        for order_id in ids:
            for ord_item in self.orders[order_id].has_ordered_items:
                for loc in self.item_locs[self.date][ord_item.has_item.name]:
                    loc.has_freq += (1 if add else -1) * ord_item.has_total_qty

    def _calculate_freq(self, locations, items, orders):
        """Calculate frequency for individual locations based on selected orders."""
        self.on_orders_update(False, True, orders)
