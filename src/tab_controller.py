from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
)

from heatmap import get_heatmap_color


class Location(QObject):
    """Location QObject for displaying list of selected locations."""

    def __init__(self, location):
        QObject.__init__(self)
        self._i = location

    @Property(str, constant=True)
    def name(self):
        return self._i.id

    @Property(str, constant=True)
    def class_str(self):
        if self._i.lsubclass:
            return f"{self._i.lclass} > {self._i.lsubclass}"
        return self._i.lclass

    @Property(str, constant=True)
    def dimension_str(self):
        return f"{self._i.length} x {self._i.width} x {self._i.height}"

    @Property(int, constant=True)
    def max_weight(self):
        return self._i.max_weight

    @Property(str, constant=True)
    def zone(self):
        return self._i.zone

    @Property(str, constant=True)
    def z(self):
        return str(int(self._i.coord.z))

    @Slot(float, result=str)
    def heat(self, max_freq=None):
        if max_freq:
            return get_heatmap_color(self._i.freq / max_freq)
        return self._i.freq


class Item(QObject):
    """Item QObject for displaying list of items in warehouse."""

    def __init__(self, item):
        QObject.__init__(self)
        self._i = item

    @Property(str, constant=True)
    def name(self):
        return str(self._i.id)

    @Property(str, constant=True)
    def description(self):
        return self._i.description

    @Property(str, constant=True)
    def description(self):
        if self._i.gtype:
            return f"{self._i.description} | {self._i.gtype}"
        return self._i.description

    @Property(str, constant=True)
    def zone(self):
        return self._i.zone

    @Property(str, constant=True)
    def base_dimension(self):
        bu = self._i.base_unit
        return f"{bu.length} x {bu.width} x {bu.height}"

    @Property(float, constant=True)
    def base_weight(self):
        return self._i.base_unit.weight


class Order(QObject):
    """Order QObject for displaying list of orders in warehouse."""

    def __init__(self, order):
        QObject.__init__(self)
        self._i = order

    @Property(str, constant=True)
    def name(self):
        return str(self._i.id)

    @Property(str, constant=True)
    def direction(self):
        return self._i.direction

    @Property(str, constant=True)
    def date(self):
        return self._i.delivery_date.strftime("%-d. %-m. %Y")

    @Property(str, constant=True)
    def item_id(self):
        return str(self._i.item_id)

    @Property(str, constant=True)
    def total_qty(self):
        return f"{int(self._i.total_qty)} {self._i.qty_uom}"


class UniversalListModel(QAbstractListModel):
    ObjectRole = Qt.UserRole + 1

    def __init__(self, object_class, objects={}, selected_objects=[], parent=None):
        super(UniversalListModel, self).__init__(parent)
        self._object_class = object_class
        self._objects = {k: self._object_class(v) for k, v in objects.items()}
        self._selected = selected_objects

    def set_data(self, objects):
        self._objects = {k: self._object_class(v) for k, v in objects.items()}

    def set_selected(self, selected):
        self._selected = selected
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return len(self._selected)

    def data(self, index, role):
        if index.isValid() and role == UniversalListModel.ObjectRole:
            return self._objects[self._selected[index.row()]]
        return None

    def roleNames(self):
        roles = dict()
        roles[UniversalListModel.ObjectRole] = b"object"
        return roles


class HoverListModel(UniversalListModel):
    ObjectRole = Qt.UserRole + 1

    def __init__(
        self,
        object_class,
        objects={},
        selected_objects=[],
        hovered_objects=[],
        parent=None,
    ):
        super(UniversalListModel, self).__init__(parent)
        self._object_class = object_class
        self._objects = {k: self._object_class(v) for k, v in objects.items()}
        self._selected = selected_objects
        self._hovered = hovered_objects
        self._is_hovered = False

    def set_selected(self, selected):
        self._selected = list(reversed(selected))
        self.layoutChanged.emit()

    def set_hovered(self, hovered, is_hovered=True):
        self._is_hovered = is_hovered
        self._hovered = list(reversed(hovered))
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        if self._is_hovered:
            return len(self._hovered)
        return len(self._selected)

    def data(self, index, role):
        if index.isValid() and role == UniversalListModel.ObjectRole:
            if self._is_hovered:
                return self._objects[self._hovered[index.row()]]
            return self._objects[self._selected[index.row()]]
        return None
