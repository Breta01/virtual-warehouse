from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)


class Location(QObject):
    def __init__(self, location):
        QObject.__init__(self)
        self._l = location

    changed = Signal()

    @Property(str, constant=False, notify=changed)
    def name(self):
        return str(self._l.id)

    @Property(str, constant=False, notify=changed)
    def class_str(self):
        return str(f"{self._l.lclass} >  {self._l.lsubclass}")

    @Property(str, constant=False, notify=changed)
    def dimension_str(self):
        return str(f"{self._l.length} x {self._l.width} x {self._l.height}")

    @Property(int, constant=False, notify=changed)
    def max_weight(self):
        return self._l.max_weight

    @Property(str, constant=False, notify=changed)
    def zone(self):
        return self._l.zone


class LocationListModel(QAbstractListModel):
    LocationRole = Qt.UserRole + 1

    def __init__(self, locations={}, selected_locations=[], parent=None):
        super(LocationListModel, self).__init__(parent)
        self._locations = {k: Location(v) for k, v in locations.items()}
        self._selected_locations = selected_locations

    def set_locations(self, locations):
        self._locations = {k: Location(v) for k, v in locations.items()}

    def set_selected(self, selected):
        self._selected_locations = selected
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return len(self._selected_locations)

    def data(self, index, role):
        if index.isValid() and role == LocationListModel.LocationRole:
            return self._locations[self._selected_locations[index.row()]]
        return None

    def roleNames(self):
        roles = dict()
        roles[LocationListModel.LocationRole] = b"location"
        return roles
