from matplotlib import cm
from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    Signal,
    Slot,
)

import virtual_warehouse.parser.excel_parser as parser
from virtual_warehouse.heatmap import calculate_frquencies
from virtual_warehouse.location_models import (
    MultiLocation,
    SingleLocation,
    UniversalLocationListModel,
)
from virtual_warehouse.tab_controller import (
    HoverListModel,
    Item,
    Location,
    Order,
    UniversalListModel,
)


class Worker(QRunnable):
    """Worker thread - runs provided function with given parameters."""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        """Initialise the runner function with passed args, kwargs."""
        self.fn(*self.args, **self.kwargs)


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
        self._min_x = min(l.coord.x for l in locations.values())
        self._max_x = max(l.coord.x + l.width for l in locations.values())

        self._min_y = min(l.coord.y for l in locations.values())
        self._max_y = max(l.coord.y + l.length for l in locations.values())

        self._min_z = min(l.coord.z for l in locations.values())
        self._max_z = max(l.coord.z + l.height for l in locations.values())

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
    def __init__(self, parent=None):
        super(ViewController, self).__init__(parent)
        self.threadpool = QThreadPool()

        self._is2D = True
        self._is_heatmap = False

        self._model3D = UniversalLocationListModel(
            on_change=lambda: self.modelChanged.emit()
        )
        self._model2D = UniversalLocationListModel(
            on_change=lambda: self.modelChanged.emit()
        )
        self._map = Map()

        self._sidebar_model = HoverListModel(Location)
        self._location_model = UniversalListModel(Location)
        self._item_model = UniversalListModel(Item)
        self._order_model = UniversalListModel(Order)

        self.selected_idxs = set()
        self.reset_selection()
        self.locations = {}

        # DEBUG:
        self.load(
            "file:///home/breta/Documents/github/virtual-warehouse/data/warehouse_no_1_v2.xlsx"
        )

    modelChanged = Signal()
    sidebarChanged = Signal()
    drawModeChanged = Signal()
    itemSelected = Signal()

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
        names = self._location_model._checked
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
            self._location_model.set_checked(names)
            self._sidebar_model.set_selected(names)
        else:
            self._location_model.set_checked([])
            self._sidebar_model.set_selected([])
        self.itemSelected.emit()

    @Slot(int)
    def hover_item(self, idx):
        if idx >= 0:
            names = self.model._get_idx(idx).names
            self._sidebar_model.set_hovered(names, True)
        else:
            self._sidebar_model.set_hovered([], False)
        self.sidebarChanged.emit()

    @Slot(int, result=int)
    def get_selected_idx(self, idx):
        return list(self.selected_idxs)[idx]

    # TODO: Property might be better
    @Slot(result=int)
    def count_selected(self):
        return len(self.selected_idxs)

    @Slot()
    def reset_selection(self):
        self.selected_idxs.clear()

    @Slot(str)
    def load(self, file_path):
        self._load(file_path)
        # TODO: Threading
        # worker = Worker(self._load, file_path)
        # self.threadpool.start(worker)

    def _load(self, file_path):
        print(file_path)
        locations, items, balance, orders = parser.parse_document(
            file_path[len("file://") :]
        )
        # TODO: Calculate after initial draw
        calculate_frquencies(locations, items, balance, orders)

        self.reset_selection()
        self.locations = locations

        self._map.set_data(locations)
        self._location_model.set_data(locations)
        self._location_model.set_selected(
            # list(locations.keys())
            [k for k, v in locations.items() if v.ltype == "rack"]
        )

        self._sidebar_model.set_data(locations)

        self._item_model.set_data(items)
        self._item_model.set_selected(list(items.keys()))

        self._order_model.set_data(orders)
        self._order_model.set_selected(list(orders.keys()))

        self._model3D.set_data(
            {k: SingleLocation(v) for k, v in self.locations.items()}
        )

        clusters = self._cluster_locations(self.locations)
        multi_loc = {}
        for k, v in clusters.items():
            multi_loc[k] = MultiLocation([self.locations[l] for l in v])
        self._model2D.set_data(multi_loc)

        self.modelChanged.emit()

    def _cluster_locations(self, locations):
        coord_to_locations = {}

        for key, loc in locations.items():
            if not loc.coord.get_2d() in coord_to_locations:
                coord_to_locations[loc.coord.get_2d()] = []
            coord_to_locations[loc.coord.get_2d()].append(key)

        return coord_to_locations
