"""Module providing ViewController class - connector class between QML and Python."""
from PySide2.QtCore import Property, QObject, Qt, QThread, QUrl, Signal, Slot

from virtual_warehouse.heatmap import calculate_frquencies
from virtual_warehouse.location_models import (
    MultiLocation,
    SingleLocation,
    UniversalLocationListModel,
)
from virtual_warehouse.location_utils import cluster_locations
from virtual_warehouse.map import Map
from virtual_warehouse.parser.data_model import Inventory, Item, Location, Order
from virtual_warehouse.parser.excel_parser import Document
from virtual_warehouse.tab_controller import (
    HoverListModel,
    TabItem,
    TabLocation,
    TabOrder,
    UniversalListModel,
)


class DataLoaderThread(QThread):
    """Thread which loads warehouse data from file."""

    locationsReady = Signal(object)
    itemsReady = Signal(object)
    inventoryReady = Signal(object)
    ordersReady = Signal(object)
    frequenciesReady = Signal()

    def __init__(
        self,
        file_path,
        sheet_types,
        locations=None,
        items=None,
        inventory=None,
        orders=None,
    ):
        """Initialize thread params for loading file in separate thread.

        Args:
            file_path (str): path to file for loading
            sheet_types (list[dict[str, str]]): list of dictionaries, each containing
                keys "name": name of the sheet, "type": name of the type.
                There are 6 types ("None", "Locations", "Coordinates", "Items",
                "Inventory", "Orders")
            locations (dict[str, Location]): previously loaded locations
            items (dict[str, Item]): previously loaded items
            inventory (dict[str, Inventory]): previously loaded inventory
            orders (dict[str, Inventory]): previously loaded orders
        """
        super(DataLoaderThread, self).__init__()
        self.file_path = file_path
        self.sheets = sheet_types

        self.locations = locations
        self.items = items
        self.inventory = inventory
        self.orders = orders

    def run(self):
        """Load data from file path and emit data through signal."""

        def where(arr, y):
            return [x["name"] for x in arr if x["type"] == y]

        document = Document(QUrl(self.file_path).toLocalFile())

        if (
            len(where(self.sheets, "Locations")) > 0
            and len(where(self.sheets, "Coordinates")) > 0
        ):
            Location.destroy_all()
            for sheet in where(self.sheets, "Locations"):
                self.locations = document.parse_locations(sheet)

            for sheet in where(self.sheets, "Coordinates"):
                self.locations = document.parse_coordinates(sheet)

            self.locationsReady.emit(self.locations)

        if len(where(self.sheets, "Items")) > 0:
            Item.destroy_all()
            for sheet in where(self.sheets, "Items"):
                self.items = document.parse_items(sheet)

            self.itemsReady.emit(self.items)

        if len(where(self.sheets, "Inventory")) > 0:
            Inventory.destroy_all()
            for sheet in where(self.sheets, "Inventory"):
                self.inventory = document.parse_inventory_balance(sheet)

            self.inventoryReady.emit(self.inventory)

        if len(where(self.sheets, "Orders")) > 0:
            Order.destroy_all()
            for sheet in where(self.sheets, "Orders"):
                self.orders = document.parse_orders(sheet)

            self.ordersReady.emit(self.orders)

        # First query is always slower than rest (probably some initialization going on)
        Item.get_by_locations([self.locations[next(iter(self.locations))]])

        calculate_frquencies(self.locations, self.inventory, self.orders)
        self.frequenciesReady.emit()


class QueryThread(QThread):
    """Thread runs database queries."""

    dataReady = Signal(object)

    def __init__(self, function, *args):
        """Initialize thread params for running the query.

        Args:
            function (Callable): function which runs the query.
            *args: arguments which will be passed to the function
        """
        super(QueryThread, self).__init__()
        self.function = function
        self.args = args

    def run(self):
        """Run the query and emit data through dataReady signal."""
        data = self.function(*self.args)
        self.dataReady.emit(data)


class ViewController(QObject):
    """Main controller which communicates with QML GUI."""

    def __init__(self, parent=None):
        super(ViewController, self).__init__(parent)

        self._is2D = True
        self._is_heatmap = False

        self._model3D = UniversalLocationListModel(on_change=self.modelChanged.emit)
        self._model2D = UniversalLocationListModel(on_change=self.modelChanged.emit)
        self._map = Map()

        self._sidebar_model = HoverListModel(TabLocation)
        self._location_model = UniversalListModel(TabLocation)
        self._item_model = UniversalListModel(TabItem)
        self._order_model = UniversalListModel(TabOrder)

        self.selected_idxs = {}

        self.locations = None
        self.items = None
        self.inventory = None
        self.orders = None

        self._query_thread = None
        self._loader = None
        self._progress_value = 1

    modelChanged = Signal()
    sidebarChanged = Signal()
    drawModeChanged = Signal()
    itemSelected = Signal()
    progressChanged = Signal()

    @Property(QObject, constant=False, notify=modelChanged)
    def map(self):
        return self._map

    @Property(QObject, constant=False, notify=modelChanged)
    def model(self):
        return self._model2D if self._is2D else self._model3D

    @Property(QObject, constant=False, notify=modelChanged)
    def model2D(self):
        return self._model2D

    @Property(QObject, constant=False, notify=modelChanged)
    def model3D(self):
        return self._model3D

    @Property(QObject, constant=False, notify=modelChanged)
    def location_model(self):
        return self._location_model

    @Property(QObject, constant=False, notify=sidebarChanged)
    def sidebar_model(self):
        return self._sidebar_model

    @Property(QObject, constant=False, notify=modelChanged)
    def item_model(self):
        return self._item_model

    @Property(QObject, constant=False, notify=modelChanged)
    def order_model(self):
        return self._order_model

    @Property(bool, constant=False, notify=drawModeChanged)
    def is_heatmap(self):
        return self._is_heatmap

    @Property(float, constant=False, notify=progressChanged)
    def progress_value(self):
        return self._progress_value

    @progress_value.setter
    def set_progress_value(self, val):
        self._progress_value = val
        self.progressChanged.emit()

    @Slot(result=bool)
    def is2D(self):
        return self._is2D

    @Slot()
    def switch_heatmap(self):
        self._is_heatmap = not self._is_heatmap
        self.drawModeChanged.emit()

    @Slot()
    def switch_view(self):
        """Switch 2D - 3D model and update selection."""
        self._is2D = not self._is2D
        self.selected_idxs.clear()
        for name in self._location_model._checked:
            idx = self.model.name_to_idx[name]
            self.selected_idxs[idx] = self.selected_idxs.get(idx, 0) + 1
        self.itemSelected.emit()

    def _select_locations(self, selected, checked, clear):
        """Update selected locations in the map.

        Args:
            selected (list[str]): list of names of selected locations
            checked (bool): whether we should add or remove the locations from selection
            clear (bool): if true previously selected indexes will be cleared
        """
        if clear:
            self.selected_idxs.clear()

        for name in selected:
            idx = self.model.name_to_idx[name]
            # Add or remove one occurrence of locations from counter
            self.selected_idxs[idx] = self.selected_idxs.get(idx, 0) + (
                1 if checked else -1
            )
            if self.selected_idxs[idx] <= 0:
                self.selected_idxs.pop(idx)

        self.itemSelected.emit()

    @Slot(str, bool)
    def select_location(self, selected, checked):
        """Select location index of location checked/unchecked in tab list.

        Args:
            selected (str): name of selected location
            checked (bool): check state, if true add location, remove otherwise
        """
        self._select_locations([selected], checked, clear=False)

    @Slot(int, bool)
    def select_map_location(self, idx, control=False):
        """Update selected location from map (CTRL adds location)."""
        if not control:
            self.selected_idxs.clear()

        if idx >= 0:
            names = self.model.get_idx(idx).names
            self.selected_idxs[idx] = len(names)
            self._location_model.set_checked(names, control)
            self._sidebar_model.set_selected(names)
        else:
            self._location_model.set_checked([])
            self._sidebar_model.set_selected([])
        self.itemSelected.emit()

    @Slot(bool)
    def select_all(self, select):
        """Select/unselect all locations from the tab list in the map."""
        self._select_locations(self.location_model._selected, select, clear=True)

    # Connecting sidebar tabs
    def _connect_tabs(self, src_tab_model, dst_tab_model, connector, locations=False):
        """Run query and update tab model with resulting data."""

        def callback(data):
            """Process data from query (callback function)."""
            names = [i[0].name for i in data]
            dst_tab_model.set_checked(names)
            self._query_thread = None
            if locations:
                self._select_locations(names, checked=True, clear=True)

        if src_tab_model._checked:
            objs = [src_tab_model._objects[k]._i for k in src_tab_model._checked]
            if self._query_thread is None:
                self._query_thread = QueryThread(connector, objs)
                self._query_thread.dataReady.connect(callback, Qt.QueuedConnection)
                self._query_thread.start()
        else:
            dst_tab_model.set_checked([])

    @Slot()
    def checked_locations_to_items(self):
        """Connect locations -> items tabs."""
        self._connect_tabs(
            self._location_model, self._item_model, Item.get_by_locations
        )

    @Slot()
    def checked_orders_to_items(self):
        """Connect orders -> items tabs."""
        self._connect_tabs(self._order_model, self._item_model, Item.get_by_orders)

    @Slot()
    def checked_items_to_orders(self):
        """Connect items -> orders tabs."""
        self._connect_tabs(self._item_model, self._order_model, Order.get_by_items)

    @Slot()
    def checked_locations_to_orders(self):
        """Connect locations -> orders tabs."""
        self._connect_tabs(
            self._location_model, self._order_model, Order.get_by_locations
        )

    @Slot()
    def checked_orders_to_locations(self):
        """Connect orders -> locations tabs."""
        self._connect_tabs(
            self._order_model, self._location_model, Location.get_by_orders, True
        )

    @Slot()
    def checked_items_to_locations(self):
        """Connect items -> locations tabs."""
        self._connect_tabs(
            self._item_model, self._location_model, Location.get_by_items, True
        )

    @Slot(int)
    def hover_item(self, idx):
        """Hover location on the map - displaying statistics in sidebar."""
        if idx >= 0:
            names = self.model.get_idx(idx).names
            self._sidebar_model.set_hovered(names, True)
        else:
            self._sidebar_model.set_hovered([], False)
        self.sidebarChanged.emit()

    @Slot(result="QVariantList")
    def get_selected(self):
        """Get list of indexes of selected locations inside the map."""
        return list(self.selected_idxs.keys())

    @Slot(str, result="QVariantList")
    def get_sheets(self, file_path):
        """Get names of sheets inside the file and expected type.

        Args:
            file_path (str): file url

        Returns:
            list[tuple[str, str]]: list containing lists [[name, type_name], ...]
        """
        return Document.get_sheet_names(QUrl(file_path).toLocalFile())

    @Slot(str, "QVariantList")
    def load(self, file_path, types):
        """Load excel file with corresponding sheet types.

        Args:
            file_path (str): file url should be processed with QUrl(file_path)
            types (list[dict[str, str]]): list of dictionaries, each containing
                keys "name": name of the sheet, "type": name of the type.
                There are 6 types ("None", "Locations", "Coordinates", "Items",
                "Inventory", "Orders")
        """
        self.progress_value = 0
        self._loader = DataLoaderThread(
            file_path, types, self.locations, self.items, self.inventory, self.orders
        )
        self._loader.locationsReady.connect(self._load_locations, Qt.QueuedConnection)
        self._loader.itemsReady.connect(self._load_items, Qt.QueuedConnection)
        self._loader.inventoryReady.connect(self._load_inventory, Qt.QueuedConnection)
        self._loader.ordersReady.connect(self._load_orders, Qt.QueuedConnection)
        self._loader.frequenciesReady.connect(
            self._load_frequencies, Qt.QueuedConnection
        )
        self._loader.start()

    def _load_locations(self, locations):
        """Process loaded locations (callback function)."""
        self.selected_idxs.clear()
        self.locations = locations

        self._map.set_data(locations)

        self._location_model.clear_checked()
        self._location_model.set_data(locations)
        self._location_model.set_selected(
            [k for k, v in locations.items() if v.has_ltype == "rack"]
        )

        self._sidebar_model.set_data(locations)

        self._model3D.set_data(
            {k: SingleLocation(v) for k, v in self.locations.items()}
        )

        clusters = cluster_locations(self.locations)
        multi_loc = {}
        for k, v in clusters.items():
            multi_loc[k] = MultiLocation([self.locations[l] for l in v])
        self._model2D.set_data(multi_loc)

        self.modelChanged.emit()
        self.progress_value = 0.3

    def _load_items(self, items):
        """Process loaded items (callback function)."""
        self.items = items
        self._item_model.clear_checked()
        self._item_model.set_data(items)
        self._item_model.set_selected(list(items.keys()))
        self.progress_value = 0.5

    def _load_inventory(self, inventory):
        """Process loaded inventory (callback function)."""
        self.inventory = inventory
        self.progress_value = 0.7

    def _load_orders(self, orders):
        """Process loaded orders (callback function)."""
        self.orders = orders
        self._order_model.clear_checked()
        self._order_model.set_data(orders)
        self._order_model.set_selected(list(orders.keys()))
        self.progress_value = 0.9

    def _load_frequencies(self):
        """Update frequencies (callback function)."""
        self._model2D.update_max_heat()
        self._model3D.update_max_heat()
        self.progress_value = 1
        self.drawModeChanged.emit()
