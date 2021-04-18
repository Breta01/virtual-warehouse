"""Module with plug-in for calculating selected items frequencies."""

from virtual_warehouse.parser.data_model import Inventory
from virtual_warehouse.plugin import BasePlugin


class Plugin(BasePlugin):
    """Sub-class of base plugin providing calculation of frequency.
    Calculate frequency as on-hand quantity of selected items.
    """

    update_on_items = True

    def __init__(self, locations, items, orders, inventory):
        """Initialize plugin and save required parameters.

        Args:
            locations (dict): dictionary of locations mapping id to locations
            items (dict): dictionary of items mapping id to items
            orders (dict): dictionary of orders mapping id to order
            inventory (dict): dictionary of specifying inventory
        """
        super().__init__(locations, items, orders, inventory)
        self.inventory = inventory
        self.items = items

    def _calculate_freq(self, locations, items, orders):
        """Calculate frequency for individual locations based on selected orders."""
        date = list(self.inventory.keys())[-1]
        for item_id in items:
            invs = Inventory.get_by_item(self.items[item_id], date)
            for inv in invs:
                inv.has_location.has_freq += inv.has_onhand_qty
