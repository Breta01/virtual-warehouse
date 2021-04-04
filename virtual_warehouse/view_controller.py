from PySide2.QtCore import Property, QObject, Qt, QThread, QUrl, Signal, Slot

from virtual_warehouse import __version__
from virtual_warehouse.heatmap import calculate_frquencies
from virtual_warehouse.location_models import (
    MultiLocation,
    SingleLocation,
    UniversalLocationListModel,
)
from virtual_warehouse.location_utils import cluster_locations
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
    """Thread which loads data from file."""

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

        if len(where(self.sheets, "Locations")) and len(
            where(self.sheets, "Coordinates")
        ):
            Location.destroy_all()
            for sheet in where(self.sheets, "Locations"):
                self.locations = document.parse_locations(sheet)

            for sheet in where(self.sheets, "Coordinates"):
                self.locations = document.parse_coordinates(sheet)

            self.locationsReady.emit(self.locations)

        if len(where(self.sheets, "Items")):
            Item.destroy_all()
            for sheet in where(self.sheets, "Items"):
                self.items = document.parse_items(sheet)

            self.itemsReady.emit(self.items)

        if len(where(self.sheets, "Inventory")):
            Inventory.destroy_all()
            for sheet in where(self.sheets, "Inventory"):
                self.inventory = document.parse_inventory_balance(sheet)

            self.inventoryReady.emit(self.inventory)

        if len(where(self.sheets, "Orders")):
            Order.destroy_all()
            for sheet in where(self.sheets, "Orders"):
                self.orders = document.parse_orders(sheet)

            self.ordersReady.emit(self.orders)

        calculate_frquencies(self.locations, self.inventory, self.orders)
        self.frequenciesReady.emit()


class Map(QObject):
    """Object holding basic informations about the map."""

    def __init__(self, locations=None):
        QObject.__init__(self)
        if locations:
            self.set_data(locations)
        else:
            self._min_x = 0
            self._max_x = 0
            self._min_y = 0
            self._max_y = 0
            self._min_z = 0
            self._max_z = 0

    def set_data(self, locations):
        self._min_x = min(l.has_x for l in locations.values())
        self._max_x = max(l.has_x + l.has_width for l in locations.values())

        self._min_y = min(l.has_y for l in locations.values())
        self._max_y = max(l.has_y + l.has_length for l in locations.values())

        self._min_z = min(l.has_z for l in locations.values())
        self._max_z = max(l.has_z + l.has_height for l in locations.values())

    @Property(float, constant=True)
    def min_x(self):
        return self._min_x

    @Property(float, constant=True)
    def max_x(self):
        return self._max_x

    @Property(float, constant=True)
    def min_y(self):
        return self._min_y

    @Property(float, constant=True)
    def max_y(self):
        return self._max_y

    @Property(float, constant=True)
    def min_z(self):
        return self._min_z

    @Property(float, constant=True)
    def max_z(self):
        return self._max_z


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

        self.selected_idxs = set()
        self.reset_selection()

        self.locations = None
        self.items = None
        self.inventory = None
        self.orders = None

        self._progress_value = 1

    modelChanged = Signal()
    sidebarChanged = Signal()
    drawModeChanged = Signal()
    itemSelected = Signal()
    progressChanged = Signal()

    @Property(str, constant=True)
    def version(self):
        return __version__

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
        self.reset_selection()
        for name in self._location_model._checked:
            idx = self.model._name_to_idx[name]
            self.selected_idxs.add(idx)
        self.itemSelected.emit()

    @Slot(str, bool)
    def checked_location(self, selected, val):
        """Location checked in tab list."""
        idx = self.model._name_to_idx[selected]
        if val:
            self.selected_idxs.add(idx)
        else:
            self.selected_idxs.discard(idx)
        self.itemSelected.emit()

    @Slot(int, bool)
    def select_item(self, idx, control=False):
        """Location selected from map (CTRL adds location)."""
        if not control:
            self.reset_selection()
        if idx >= 0:
            self.selected_idxs.add(idx)
            names = self.model._get_idx(idx).names
            self._location_model.set_checked(names, control)
            self._sidebar_model.set_selected(names)
        else:
            self._location_model.set_checked([])
            self._sidebar_model.set_selected([])
        self.itemSelected.emit()

    # Connecting sidebar tabs
    # TODO: run in separate thread
    @staticmethod
    def _connect_tabs(src_tab_model, dst_tab_model, connector):
        if src_tab_model._checked:
            objs = [src_tab_model._objects[k]._i for k in src_tab_model._checked]
            res = connector(objs)
            dst_tab_model.set_checked([i[0].name for i in res])
        else:
            dst_tab_model.set_checked([])

    @Slot()
    def checked_locations_to_items(self):
        self._connect_tabs(
            self._location_model, self._item_model, Item.get_by_locations
        )

    @Slot()
    def checked_orders_to_items(self):
        self._connect_tabs(self._order_model, self._item_model, Item.get_by_orders)

    @Slot()
    def checked_items_to_orders(self):
        self._connect_tabs(self._item_model, self._order_model, Order.get_by_items)

    @Slot()
    def checked_locations_to_orders(self):
        self._connect_tabs(
            self._location_model, self._order_model, Order.get_by_locations
        )

    @Slot()
    def checked_orders_to_locations(self):
        self._connect_tabs(
            self._order_model, self._location_model, Location.get_by_orders
        )

    @Slot()
    def checked_items_to_locations(self):
        self._connect_tabs(
            self._item_model, self._location_model, Location.get_by_items
        )

    @Slot(int)
    def hover_item(self, idx):
        if idx >= 0:
            names = self.model._get_idx(idx).names
            self._sidebar_model.set_hovered(names, True)
        else:
            self._sidebar_model.set_hovered([], False)
        self.sidebarChanged.emit()

    @Slot(result="QVariantList")
    def get_selected(self):
        return list(self.selected_idxs)

    @Slot()
    def reset_selection(self):
        self.selected_idxs.clear()

    @Slot(str, result="QVariantList")
    def get_sheets(self, file_path):
        return Document.get_sheet_names(QUrl(file_path).toLocalFile())

    @Slot(str, "QVariantList")
    def load(self, file_path, types):
        print(types)
        print(types[0])
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
        self.reset_selection()
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
        self.items = items
        self._item_model.clear_checked()
        self._item_model.set_data(items)
        self._item_model.set_selected(list(items.keys()))
        self.progress_value = 0.5

    def _load_inventory(self, inventory):
        self.inventory = inventory
        self.progress_value = 0.7

    def _load_orders(self, orders):
        self.orders = orders
        self._order_model.clear_checked()
        self._order_model.set_data(orders)
        self._order_model.set_selected(list(orders.keys()))
        self.progress_value = 0.9

    def _load_frequencies(self):
        self._model2D.update_max_heat()
        self._model3D.update_max_heat()
        self.progress_value = 1
