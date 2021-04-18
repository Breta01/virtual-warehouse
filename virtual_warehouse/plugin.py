import importlib
import pkgutil
from abc import ABC, abstractmethod

from PySide2.QtCore import Qt


class BasePlugin(ABC):
    """Base plugin class for calculating frequencies.
    Each plugin must be subclass of this BasePlugin class.
    Plugins must be placed as separate modules in virtual_warehouse.plugins
    Implementation of (_calculate_freq(...)) initial frequency calculation is required.
    Plugin can also implement some of following functions to dynamically update
    frequencies:
        on_locations_update(...)
        on_items_update(...)
        on_orders_update(...)


    Attributes:
        locations (dict[str, Location]): always store dictionary of locations
    """

    def __init__(self, locations, items, orders, inventory):
        """Initialize plugin, all plugins must implement constructor with same arguments.

        Args:
            locations (dict): dictionary of locations mapping id to locations
            items (dict): dictionary of items mapping id to items
            orders (dict): dictionary of orders mapping id to order
            inventory (dict): dictionary of specifying inventory
        """
        self.locations = locations

    def calculate_frequencies(self, *args):
        """Run initial frequency calculation."""
        self._clear_frequencies()
        self._calculate_freq(*args)

    def on_locations_update(self, clear, add, ids):
        """Update frequency calculation on locations check/uncheck.
        By default this function does nothing. Should be implemented by plugin,
        if plugin frequencies change with location selection.

        Args:
            clear (bool): Whether to clear previously selected orders.
            add (bool): Whether to add or remove ids from calculation.
            ids (list[str]): list of ids considered in calculation.
        """

    def on_items_update(self, clear, add, ids):
        """Update frequency calculation on items check/uncheck.
        By default this function does nothing. Should be implemented by plugin,
        if plugin frequencies change with item selection.

        Args:
            clear (bool): Whether to clear previously selected orders.
            add (bool): Whether to add or remove ids from calculation.
            ids (list[str]): list of ids considered in calculation.
        """

    def on_orders_update(self, clear, add, ids):
        """Update frequency calculation on orders check/uncheck.
        By default this function does nothing. Should be implemented by plugin,
        if plugin frequencies change with order selection.

        Args:
            clear (bool): Whether to clear previously selected orders.
            add (bool): Whether to add or remove ids from calculation.
            ids (list[str]): list of ids considered in calculation.
        """

    @abstractmethod
    def _calculate_freq(self, locations, items, orders):
        """Calculate frequencies based on selected objects (abstract method).

        Args:
            locations (list[str]): list of selected location ids
            items (list[str]): list of selected item ids
            orders (list[str]): list of selected order ids
        """

    def _clear_frequencies(self):
        """Clear all frequencies."""
        for v in self.locations.values():
            v.has_freq = 0


class PluginManager:
    """Class loading and controlling all plugins and providing them to controller."""

    def __init__(self, location_model, item_model, order_model):
        """Initialize PluginManager holding all plugins from plugins folder."""
        self.plugin_modules = PluginManager.load_plugins()
        self.plugins = {}
        self.active_plugin = "order_frequencies"

        self._location_model = location_model
        self._item_model = item_model
        self._order_model = order_model

        self._location_model.checkChanged.connect(
            self._locations_update, Qt.DirectConnection
        )
        self._item_model.checkChanged.connect(self._items_update, Qt.DirectConnection)
        self._order_model.checkChanged.connect(self._orders_update, Qt.DirectConnection)

    def _locations_update(self, args):
        """Update active plugin on locations update."""
        self.plugins[self.active_plugin].on_locations_update(*args)

    def _items_update(self, args):
        """Update active plugin on items update."""
        self.plugins[self.active_plugin].on_items_update(*args)

    def _orders_update(self, args):
        """Update active plugin on orders update."""
        self.plugins[self.active_plugin].on_orders_update(*args)

    def set_data(self, locations, items, orders, inventory):
        """Set new warehouse date for all plugins."""
        for name, module in self.plugin_modules.items():
            self.plugins[name] = module.Plugin(locations, items, orders, inventory)

    def update(self):
        """Recalculate frequencies."""
        self.plugins[self.active_plugin].calculate_frequencies(
            self._location_model.checked,
            self._item_model.checked,
            self._order_model.checked,
        )

    @staticmethod
    def _iter_namespace(ns_pkg):
        """Iter modules in specified sub-package."""
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    @staticmethod
    def load_plugins():
        """Load plugin modules from virtual_warehouse.plugins sub-package."""
        import virtual_warehouse.plugins

        return {
            name.split(".")[-1]: importlib.import_module(name)
            for finder, name, ispkg in PluginManager._iter_namespace(
                virtual_warehouse.plugins
            )
        }
