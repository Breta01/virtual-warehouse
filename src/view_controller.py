import parser.excel_parser as parser

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

from heatmap import calculate_frquencies
from location_models import MultiLocation, SingleLocation, UniversalLocationListModel
from tab_controller import Item, Location, Order, UniversalListModel


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

        self._model3D = UniversalLocationListModel(
            on_change=lambda: self.modelChanged.emit()
        )
        self._model2D = UniversalLocationListModel(
            on_change=lambda: self.modelChanged.emit()
        )
        self._map = Map()

        self._location_model = UniversalListModel(Location)
        self._item_model = UniversalListModel(Item)
        self._order_model = UniversalListModel(Order)

        self.reset_selection()
        self.locations = {}

    modelChanged = Signal()
    itemSelected = Signal()

    @Property(QObject, constant=False, notify=modelChanged)
    def map(self):
        return self._map

    @Property(QObject, constant=False, notify=modelChanged)
    def model(self):
        # print("Model", self.is2D)
        return self._model2D if self._is2D else self._model3D

    @Property(QObject, constant=False, notify=modelChanged)
    def location_model(self):
        return self._location_model

    @Property(QObject, constant=False, notify=modelChanged)
    def item_model(self):
        return self._item_model

    @Property(QObject, constant=False, notify=modelChanged)
    def order_model(self):
        return self._order_model

    @Slot(result=bool)
    def is2D(self):
        return self._is2D

    @Slot()
    def switch_view(self):
        self._is2D = not self._is2D

    @Slot(str, int)
    def select_item(self, name, idx):
        self.selected_name = name
        self.selected_idx = idx
        # self._location_model.set_selected([name])
        self.itemSelected.emit()

    @Slot(result=int)
    def get_selected_idx(self):
        return self.selected_idx

    @Slot()
    def reset_selection(self):
        self.selected_name = None
        self.selected_idx = -1

    @Slot(str)
    def load(self, file_path):
        # TODO: Threading
        worker = Worker(self._load, file_path)
        self.threadpool.start(worker)

    def _load(self, file_path):
        locations, items, balance, orders = parser.parse_document(
            file_path[len("file://") :]
        )
        # TODO: Calculate after initial draw
        calculate_frquencies(locations, items, balance, orders)

        self.reset_selection()
        self.locations = locations

        self._map.set_data(locations)
        self._location_model.set_data(
            locations
            # {k: v for k, v in locations.items() if v.ltype == "rack"}
        )
        self._location_model.set_selected(
            list(locations.keys())
            # [k for k, v in locations.items() if v.ltype == "rack"]
        )

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
