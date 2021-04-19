from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
)

from virtual_warehouse.environment import LOCATION_TYPE_MAP


class SingleLocation(QObject):
    """Class representing single location in warehouse."""

    def __init__(self, location):
        """Initialize location wrapper.

        Args:
            location (Location): location object to represent
        """
        self._i = location
        self._color = LOCATION_TYPE_MAP[self._i.has_ltype]["color"]
        self._gcolor = LOCATION_TYPE_MAP[self._i.has_ltype]["gray_color"]
        self._mesh_file = LOCATION_TYPE_MAP[self._i.has_ltype]["mesh"]
        # Required for displaying selected locations
        self.names = [self._i.name]

    def get_dict(self):
        """Return dictionary representing the location."""
        return {
            "name": self._i.name,
            "type": self._i.has_ltype,
            "mesh_file": self._mesh_file,
            "color": self._color,
            "gray_color": self._gcolor,
            "x": self._i.has_x,
            "y": self._i.has_y,
            "z": self._i.has_z,
            "length": self._i.has_length,
            "width": self._i.has_width,
            "height": self._i.has_height,
        }

    def get_heat(self):
        """Get heat of location."""
        return self._i.has_freq


class MultiLocation(QObject):
    """Class representing multiple locations merged together."""

    def __init__(self, locations):
        """Initialize multi-location wrapper.

        Args:
            locations (list[Location]): locations to store and represent
        """
        self._l = locations
        self._i = locations[0]
        self._color = LOCATION_TYPE_MAP[self._i.has_ltype]["color"]
        self._gcolor = LOCATION_TYPE_MAP[self._i.has_ltype]["gray_color"]
        self._mesh_file = LOCATION_TYPE_MAP[self._i.has_ltype]["mesh"]
        # Required for displaying selected locations
        self.names = [i.name for i in locations]

    def get_dict(self):
        """Return dictionary representing the multi-location."""
        return {
            "name": self._i.name,
            "type": self._i.has_ltype,
            "mesh_file": self._mesh_file,
            "color": self._color,
            "gray_color": self._gcolor,
            "x": self._i.has_x,
            "y": self._i.has_y,
            "z": self._i.has_z,
            "length": self._i.has_length,
            "width": self._i.has_width,
            "height": self._i.has_height,
        }

    def get_heat(self, level=-1):
        """Calculate heat of the whole location or single level."""
        return (
            self._l[level].has_freq if level != -1 else sum(i.has_freq for i in self._l)
        )


class UniversalLocationListModel(QAbstractListModel):
    """List model providing locations for 2D or 3D view."""

    ObjectRole = Qt.UserRole + 1

    maxChanged = Signal()
    levelChanged = Signal()

    def __init__(self, on_change, objects=None, parent=None):
        super(UniversalLocationListModel, self).__init__(parent)
        self._on_change = on_change
        self.set_data({} if objects is None else objects)
        self._level = -1
        self._max_level = 1

    def set_data(self, objects):
        """Set new objects which should already by wrapped by location class."""
        self._objects = objects
        self._keys = list(objects.keys())
        self.name_to_idx = {}
        for i, k in enumerate(self._keys):
            for n in self._objects[k].names:
                self.name_to_idx[n] = i

        if objects:
            self._max_level = max(l._i.has_z for l in self._objects.values())
            self.maxChanged.emit()

    def get_idx(self, idx):
        """Get object by index."""
        return self._objects[self._keys[idx]]

    @Property(int, constant=False, notify=maxChanged)
    def max_level(self):
        """Get max level possible to select."""
        return self._max_level

    @Slot(result=int)
    def rowCount(self, parent=QModelIndex()):
        """Get number of items in list (required method)."""
        return len(self._keys)

    @Slot(int, result="QVariant")
    def get(self, index):
        """Get dictionary representing location at given index."""
        return self.get_idx(index).get_dict()

    @Property(int, constant=False, notify=levelChanged)
    def level(self):
        """Get selected level property for heat-map visualization."""
        return self._level

    @level.setter
    def set_level(self, level):
        """Set level property."""
        self._level = level
        self.levelChanged.emit()

    @Slot(int, result=float)
    def get_heat(self, index):
        """Get heat of location on given index."""
        return self.get_idx(index).get_heat(self._level)

    def data(self, index, role):
        """Return data for given role and index (required method)."""
        if index.isValid() and role == UniversalLocationListModel.ObjectRole:
            return self.get_idx(index.row())
        return None

    def roleNames(self):  # skipcq: PYL-R0201
        """Set role names, QAbstractListModel requires implementation of this method."""
        roles = {}
        roles[UniversalLocationListModel.ObjectRole] = b"object"
        return roles
