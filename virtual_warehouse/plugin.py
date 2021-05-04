import importlib
import pkgutil
from abc import ABC, abstractmethod

from PySide2.QtCore import Property, QObject, Qt, Signal


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
        display_name (str): name of plugin to display in Menu (must be overwritten)
    """

    display_name: str

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


class PluginManager(QObject):
    """Class loading and controlling all plugins and providing them to controller."""

    pluginChanged = Signal()

    def __init__(self, location_model, item_model, order_model, update_signal):
        """Initialize PluginManager holding all plugins from plugins folder.

        Args:
            location_model (UniversalListModel): list model representing location tab
            item_model (UniversalListModel): list model representing item tab
            order_model (UniversalListModel): list model representing order tab
            update_signal (Signal): signal to emit on plugin update (drawModeChanged)
        """
        QObject.__init__(self)
        self.plugin_modules = PluginManager.load_plugins()
        self.plugins = {}
        self.active_plugin = None
        self._is_active = False

        self._location_model = location_model
        self._item_model = item_model
        self._order_model = order_model

        self.update_signal = update_signal

        self._location_model.checkChanged.connect(
            self._locations_update, Qt.DirectConnection
        )
        self._item_model.checkChanged.connect(self._items_update, Qt.DirectConnection)
        self._order_model.checkChanged.connect(self._orders_update, Qt.DirectConnection)

    def set_data(self, locations, items, orders, inventory):
        """Set new warehouse data for all plugins."""
        if (
            locations is not None
            and items is not None
            and orders is not None
            and inventory is not None
        ):
            for name, module in self.plugin_modules.items():
                self.plugins[name] = module.Plugin(locations, items, orders, inventory)
            self._is_active = True
            self._update()

    @Property(str, constant=False, notify=pluginChanged)
    def active(self):
        """Get name of active plugin."""
        return self.active_plugin

    @active.setter
    def activate_plugin(self, plugin_name):
        """Activate selected plugin and update frequencies.

        Args:
            plugin_name (str): plugin name works as key for plugins dictionary
        """
        if self.active_plugin != plugin_name:
            self.active_plugin = plugin_name
            self._update()
            self.pluginChanged.emit()

    def _locations_update(self, args):
        """Update active plugin on locations update."""
        if self.active_plugin and (args[0] or len(args[2]) != 0):
            self.plugins[self.active_plugin].on_locations_update(*args)
            self.update_signal.emit()

    def _items_update(self, args):
        """Update active plugin on items update."""
        if self.active_plugin and (args[0] or len(args[2]) != 0):
            self.plugins[self.active_plugin].on_items_update(*args)
            self.update_signal.emit()

    def _orders_update(self, args):
        """Update active plugin on orders update."""
        if self.active_plugin and (args[0] or len(args[2]) != 0):
            self.plugins[self.active_plugin].on_orders_update(*args)
            self.update_signal.emit()

    def _update(self):
        """Recalculate frequencies using active plugin."""
        if self.active_plugin and self._is_active:
            self.plugins[self.active_plugin].calculate_frequencies(
                self._location_model.checked,
                self._item_model.checked,
                self._order_model.checked,
            )

        if self._is_active:
            self.update_signal.emit()

    @Property("QVariantList", constant=True)
    def names(self):
        """Get list of display names and module names."""
        return [
            {"name": m.Plugin.display_name, "module": k}
            for k, m in self.plugin_modules.items()
        ]

    @staticmethod
    def _iter_namespace(ns_pkg):
        """Iterate modules in specified sub-package."""
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    @staticmethod
    def load_plugins():
        """Load plugin modules from virtual_warehouse.plugins sub-package.

        Returns:
            dict[str, module]: dictionary containing module name and module.
        """
        import virtual_warehouse.plugins

        return {
            name.split(".")[-1]: importlib.import_module(name)
            for finder, name, ispkg in PluginManager._iter_namespace(
                virtual_warehouse.plugins
            )
        }
