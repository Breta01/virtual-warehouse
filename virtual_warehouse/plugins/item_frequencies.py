"""Module with plug-in for calculating selected items frequencies."""

from virtual_warehouse.data.data_model import Inventory
from virtual_warehouse.plugin import BasePlugin


class Plugin(BasePlugin):
    """Sub-class of base plugin providing calculation of frequency.
    Calculate frequency as on-hand quantity of selected items.
    """

    display_name = "&Item Histogram"

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
        self.date = list(self.inventory.keys())[-1]

    def on_items_update(self, clear, add, ids):
        """Update frequency calculation on items check/uncheck.

        Args:
            clear (bool): Whether to clear previously selected orders.
            add (bool): Whether to add or remove ids from calculation.
            ids (list[str]): list of ids considered in calculation.
        """
        if clear:
            self._clear_frequencies()

        for item_id in ids:
            invs = Inventory.get_by_item(self.items[item_id], self.date)
            for inv in invs:
                inv.has_location.has_freq += (1 if add else -1) * inv.has_onhand_qty

    def _calculate_freq(self, locations, items, orders):
        """Calculate frequency for individual locations based on selected orders."""
        self.on_items_update(False, True, items)
