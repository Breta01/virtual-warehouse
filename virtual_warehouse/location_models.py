from PySide2.QtCore import Property, QModelIndex, QObject, Qt, Signal, Slot

from virtual_warehouse.environment import LOCATION_TYPE_MAP
from virtual_warehouse.heatmap import get_heatmap_color


class SingleLocation:
    """Class representing single location in warehouse."""

    def __init__(self, location):
        # QObject.__init__(self)
        self._i = location
        self._color = LOCATION_TYPE_MAP[self._i.ltype]["color"]
        self._gcolor = LOCATION_TYPE_MAP[self._i.ltype]["gray_color"]
        self._mesh_file = LOCATION_TYPE_MAP[self._i.ltype]["mesh"]
        # Required for displaying selected locations
        self.names = [str(self._i.id)]

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

    def get_heat(self, level=-1):
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
        # Required for displaying selected locations
        self.names = [i.id for i in locations]

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

    def get_heat(self, level=-1):
        return self._l[level].freq if level != -1 else sum(i.freq for i in self._l)


class UniversalLocationListModel(QObject):
    """List model providing locations for 2D or 3D view."""

    ObjectRole = Qt.UserRole + 1

    maxChanged = Signal()
    levelChanged = Signal()

    def __init__(self, on_change, objects=None, parent=None):
        super(UniversalLocationListModel, self).__init__(parent)
        self._on_change = on_change
        self.set_data({} if objects is None else objects)
        self._max_heat = 0
        self._level = -1
        self._max_level = 1

    def set_data(self, objects):
        self._objects = objects
        self._keys = list(objects.keys())
        self._name_to_idx = {}
        for i, k in enumerate(self._keys):
            for n in self._objects[k].names:
                self._name_to_idx[n] = i
        if objects:
            self._max_heat = self._get_max_heat()
            self._max_level = max(l._i.coord.z for l in self._objects.values())
            print(self._max_level)
            self.maxChanged.emit()

    def _get_max_heat(self):
        if len(self._objects) == 0:
            return 0
        return max(o.get_heat() for _, o in self._objects.items())

    def _get_idx(self, idx):
        return self._objects[self._keys[idx]]

    @Property(float, constant=False, notify=maxChanged)
    def max_heat(self):
        return self._max_heat

    @Property(int, constant=False, notify=maxChanged)
    def max_level(self):
        return self._max_level

    @Slot(result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._keys)

    @Slot(int, result="QVariant")
    def get(self, index):
        return self._get_idx(index).get_dict()

    @Property(int, constant=False, notify=levelChanged)
    def level(self):
        return self._level

    @level.setter
    def set_level(self, level):
        self._level = level

    @Slot(int, float, result=str)
    def get_heat(self, index, max_heat=None):
        freq = self._get_idx(index).get_heat(self._level)
        if max_heat:
            return get_heatmap_color(freq / max_heat)
        return get_heatmap_color(freq / self._max_heat)

    def data(self, index, role):
        if index.isValid() and role == UniversalLocationListModel.ObjectRole:
            return self._get_idx(index.row())
        return None

    def roleNames(self):
        roles = {}
        roles[UniversalListModel.ObjectRole] = b"object"
        return roles
