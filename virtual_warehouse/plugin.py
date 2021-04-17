import importlib
import pkgutil
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Base plugin class for calculating frequencies.
    Each plugin must be subclass of this BasePlugin class.
    Plugins must be placed as separate modules in virtual_warehouse.plugins

    Attributes:
        update_on_locations (bool): true if plugin should be updated on locations update
        update_on_items (bool) = true if plugin should be updated on items update
        update_on_orders (bool) = true if plugin should be updated on orders update
    """

    update_on_locations: bool = False
    update_on_items: bool = False
    update_on_orders: bool = False

    def __init__(self, locations, items, orders, inventory):
        """Initialize plugin, all plugins must implement constructor with same arguments.

        Args:
            locations (dict): dictionary of locations mapping id to locations
            items (dict): dictionary of items mapping id to items
            orders (dict): dictionary of orders mapping id to order
            inventory (dict): dictionary of specifying inventory
        """
        self.locations = locations

    def calculate_frequencies(self):
        """Run initial frequency calculation."""
        self._clear_frequencies()
        args = [None, None, None]
        if self.update_on_locations:
            args[0] = self.locations.keys()
        if self.update_on_items:
            args[1] = self.items.keys()
        if self.update_on_orders:
            args[2] = self.orders.keys()

        self._calculate_freq(*args)

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

    def __init__(self):
        """Initialize PluginManager holding all plugins from plugins folder."""
        self.plugin_modules = PluginManager.load_plugins()
        self.plugins = {}
        self.active_plugin = "order_frequencies"

    def set_data(self, locations, items, orders, inventory):
        """Set new warehouse date for all plugins."""
        for name, module in self.plugin_modules.items():
            self.plugins[name] = module.Plugin(locations, items, orders, inventory)

    def update(self):
        """Recalculate frequencies."""
        self.plugins[self.active_plugin].calculate_frequencies()

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
