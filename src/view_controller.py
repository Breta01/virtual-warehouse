import parser.excel_parser as parser

from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
)

from environment import LOCATION_TYPE_MAP
from tab_controller import Item, Location, Order, UniversalListModel


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


class ItemListModel(QAbstractListModel):
    MeshRole = Qt.UserRole + 1
    XPosRole = Qt.UserRole + 2
    YPosRole = Qt.UserRole + 3
    ZPosRole = Qt.UserRole + 4
    NameRole = Qt.UserRole + 5
    TypeRole = Qt.UserRole + 6
    ColorRole = Qt.UserRole + 7
    LenghtRole = Qt.UserRole + 8
    WidthRole = Qt.UserRole + 9
    HeightRole = Qt.UserRole + 10

    def __init__(self, on_change, parent=None):
        super(ItemListModel, self).__init__(parent)
        self._on_change = on_change
        self._assets = []

    def add(self, loc, emit=True):
        try:
            loc_setting = LOCATION_TYPE_MAP[loc.ltype]
        except:
            return
        self._assets.append(
            {
                "meshFile": loc_setting["mesh"],
                "color": loc_setting["color"],
                "type": loc.ltype,
                "x": loc.coord.x,
                "y": loc.coord.y,
                "z": loc.coord.z,
                "length": loc.length,
                "width": loc.width,
                "height": loc.height,
                "name": loc.id,
            }
        )
        if emit:
            self._on_change()

    def clear(self):
        self._assets = []
        self._on_change()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._assets)

    def get(self, index):
        return self._assets[index]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            item = self._assets[index.row()]

            if role == ItemListModel.MeshRole:
                return item["meshFile"]
            elif role == ItemListModel.XPosRole:
                return item["x"]
            elif role == ItemListModel.YPosRole:
                return item["y"]
            elif role == ItemListModel.ZPosRole:
                return item["z"]
            elif role == ItemListModel.NameRole:
                return item["name"]
            elif role == ItemListModel.TypeRole:
                return item["type"]
            elif role == ItemListModel.ColorRole:
                return item["color"]
            elif role == ItemListModel.LengthRole:
                return item["length"]
            elif role == ItemListModel.WidthRole:
                return item["width"]
            elif role == ItemListModel.HeightRole:
                return item["height"]

    def roleNames(self):
        roles = dict()
        roles[ItemListModel.MeshRole] = b"meshFile"
        roles[ItemListModel.XPosRole] = b"x"
        roles[ItemListModel.YPosRole] = b"y"
        roles[ItemListModel.ZPosRole] = b"z"
        roles[ItemListModel.NameRole] = b"name"
        roles[ItemListModel.TypeRole] = b"type"
        roles[ItemListModel.ColorRole] = b"color"
        roles[ItemListModel.LengthRole] = b"length"
        roles[ItemListModel.WidthRole] = b"width"
        roles[ItemListModel.HeightRole] = b"height"
        return roles


class ViewController(QObject):
    def __init__(self, parent=None):
        super(ViewController, self).__init__(parent)
        self._model = ItemListModel(on_change=lambda: self.modelChanged.emit())
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
        return self._model

    @Property(QObject, constant=False, notify=modelChanged)
    def location_model(self):
        return self._location_model

    @Property(QObject, constant=False, notify=modelChanged)
    def item_model(self):
        return self._item_model

    @Property(QObject, constant=False, notify=modelChanged)
    def order_model(self):
        return self._order_model

    @Slot(int, result="QVariant")
    def get_item(self, idx):
        return self._model.get(idx)

    @Slot(str, int)
    def select_item(self, name, idx):
        self.selected_name = name
        self.selected_idx = idx
        self._location_model.set_selected([name])
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
        locations, items, balance, orders = parser.parse_document(
            file_path[len("file://") :]
        )
        self.reset_selection()
        self.locations = locations

        self._map.set_data(locations)
        self._location_model.set_data(
            {k: v for k, v in locations.items() if v.ltype == "rack"}
        )
        self._location_model.set_selected(
            [k for k, v in locations.items() if v.ltype == "rack"]
        )

        self._item_model.set_data(items)
        self._item_model.set_selected(list(items.keys()))

        self._order_model.set_data(orders)
        self._order_model.set_selected(list(orders.keys()))

        self._model.clear()
        for loc in locations.values():
            self._model.add(loc, False)
        self.modelChanged.emit()
