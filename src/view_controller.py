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

from tab_controller import Item, Location, UniversalListModel

location_type_map = {
    "FLOOR": "resources/objects/floor.obj",
    "RACK": "resources/objects/rack.obj",
    "Storage Rack": "resources/objects/rack.obj",
}


class ItemListModel(QAbstractListModel):
    # Our custom roles
    MeshRole = Qt.UserRole + 1
    XPosRole = Qt.UserRole + 2
    YPosRole = Qt.UserRole + 3
    ZPosRole = Qt.UserRole + 4
    NameRole = Qt.UserRole + 5

    def __init__(self, on_change, parent=None):
        super(ItemListModel, self).__init__(parent)
        self._on_change = on_change
        self._assets = []

    def add(self, loc, emit=True):
        try:
            meshFile = location_type_map[loc.ltype]
        except:
            return
        self._assets.append(
            {
                "meshFile": meshFile,
                "x": loc.coord.x,
                "y": loc.coord.y,
                "z": loc.coord.z,
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

    def roleNames(self):
        roles = dict()
        roles[ItemListModel.MeshRole] = b"meshFile"
        roles[ItemListModel.XPosRole] = b"x"
        roles[ItemListModel.YPosRole] = b"y"
        roles[ItemListModel.ZPosRole] = b"z"
        roles[ItemListModel.NameRole] = b"name"
        return roles


class ViewController(QObject):
    def __init__(self, parent=None):
        super(ViewController, self).__init__(parent)
        self._model = ItemListModel(on_change=lambda: self.modelChanged.emit())
        self._location_model = UniversalListModel(Location)
        self._item_model = UniversalListModel(Item)
        self.reset_selection()
        self.locations = {}

    modelChanged = Signal()
    itemSelected = Signal()

    @Property(QObject, constant=False, notify=modelChanged)
    def model(self):
        return self._model

    @Property(QObject, constant=False, notify=modelChanged)
    def location_model(self):
        return self._location_model

    @Property(QObject, constant=False, notify=modelChanged)
    def item_model(self):
        return self._item_model

    @Property("QVariant", constant=False, notify=itemSelected)
    def item(self):
        if self.selected_name and self.selected_name in self.locations:
            l = self.locations[self.selected_name]
            return {
                "text": f"Name: {l.id}\nType: {l.ltype}\nClass: {l.lclass}\nMax weight: {l.max_weight}"
            }
        else:
            return {"text": "No location selected"}

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
        self.selected_idx = 0

    @Slot(str)
    def load(self, file_path):
        # TODO: Threading
        locations, items, balance, orders = parser.parse_document(
            file_path[len("file://") :]
        )
        self.reset_selection()
        self.locations = locations

        self._location_model.set_data(locations)
        self._item_model.set_data(items)
        self._item_model.set_selected(list(items.keys()))

        self._model.clear()
        for loc in locations.values():
            self._model.add(loc, False)
        self.modelChanged.emit()
