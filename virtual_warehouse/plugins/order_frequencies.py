"""Module with plug-in for calculating selected items frequencies."""

from virtual_warehouse.plugin import BasePlugin


class Plugin(BasePlugin):
    """Sub-class of base plugin providing calculation of frequency.
    Calculate frequency as frequency of item in order.
    """

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

    @staticmethod
    def item_locations(inventory):
        """Create dictionary mapping (date, item) to list of locations."""
        item_to_loc = {}
        for date, status in inventory.items():
            item_to_loc[date] = {}
            for loc_id, loc_inventories in status.items():
                for inv in loc_inventories:
                    if inv.has_item.name not in item_to_loc[date]:
                        item_to_loc[date][inv.has_item.name] = []
                    item_to_loc[date][inv.has_item.name].append(loc_id)

        return item_to_loc

    def _calculate_freq(self, locations, items, orders):
        """Calculate frequency for individual locations based on selected orders."""

        date = list(self.item_locs.keys())[-1]

        for order_id in self.orders.keys():
            for item in self.orders[order_id].has_ordered_items:
                for loc in self.item_locs[date][item.has_item.name]:
                    self.locations[loc].has_freq += item.has_total_qty
