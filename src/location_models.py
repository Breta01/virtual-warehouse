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

from environment import LOCATION_TYPE_MAP


class SingleLocation:
    """Class representing single location in warehouse."""

    def __init__(self, location):
        # QObject.__init__(self)
        self._i = location
        self._color = LOCATION_TYPE_MAP[self._i.ltype]["color"]
        self._gcolor = LOCATION_TYPE_MAP[self._i.ltype]["gray_color"]
        self._mesh_file = LOCATION_TYPE_MAP[self._i.ltype]["mesh"]

    def get_dict(self):
        return {
            "name": str(self._i.id),
            "type": self._i.ltype,
            "mesh_file": self._mesh_file,
            "color": self._color,
            "gray_color": self._gcolor,
            "x": self._i.coord.x,
            "y": self._i.coord.y,
            "z": self._i.coord.z,
            "length": self._i.length,
            "width": self._i.width,
            "height": self._i.height,
        }

    def get_heat(self):
        return self._i.freq


class MultiLocation:
    """Class representing multiple locations merged together."""

    def __init__(self, locations):
        # QObject.__init__(self)
        self._l = locations
        self._i = locations[0]
        self._color = LOCATION_TYPE_MAP[self._i.ltype]["color"]
        self._gcolor = LOCATION_TYPE_MAP[self._i.ltype]["gray_color"]
        self._mesh_file = LOCATION_TYPE_MAP[self._i.ltype]["mesh"]

    def get_dict(self):
        return {
            "name": str(self._i.id),
            "type": self._i.ltype,
            "mesh_file": self._mesh_file,
            "color": self._color,
            "gray_color": self._gcolor,
            "x": self._i.coord.x,
            "y": self._i.coord.y,
            "z": self._i.coord.z,
            "length": self._i.length,
            "width": self._i.width,
            "height": self._i.height,
        }

    def get_heat(self):
        return sum(i.freq for i in self._l)


class UniversalLocationListModel(QObject):
    ObjectRole = Qt.UserRole + 1

    def __init__(self, on_change, objects={}, parent=None):
        super(UniversalLocationListModel, self).__init__(parent)
        self._on_change = on_change
        self.set_data(objects)
        self.max_heat = 0

    def set_data(self, objects):
        self._objects = objects
        self._keys = list(objects.keys())
        self.max_heat = self._get_max_heat()

    def _get_max_heat(self):
        if len(self._objects) == 0:
            return 0
        return max(o.get_heat() for _, o in self._objects.items())

    @Slot(result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._keys)

    @Slot(int, result="QVariant")
    def get(self, index):
        # print(index)
        # if (index == 0):
        # print(self._objects[self._keys[index]], self._objects[self._keys[index]]._i)
        return self._objects[self._keys[index]].get_dict()

    @Slot(int, result=float)
    def get_heat(self, index):
        # print(index)
        # if (index == 0):
        # print(self._objects[self._keys[index]], self._objects[self._keys[index]]._i)
        return self._objects[self._keys[index]].get_heat() / self.max_heat

    def data(self, index, role):
        if index.isValid() and role == UniversalListModel.ObjectRole:
            return self._objects[self._keys[index.row()]]
        return None

    def roleNames(self):
        roles = dict()
        roles[UniversalListModel.ObjectRole] = b"object"
        return roles
