import locale

from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
)

from virtual_warehouse.heatmap import get_heatmap_color

locale.setlocale(locale.LC_ALL, "")


class Location(QObject):
    """Location QObject for displaying list of selected locations."""

    def __init__(self, location):
        QObject.__init__(self)
        self._i = location
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        return self._i.name

    @Property(str, constant=True)
    def class_str(self):
        if self._i.has_lsubclass:
            return f"{self._i.has_lclass} > {self._i.has_lsubclass}"
        return self._i.has_lclass

    @Property(str, constant=True)
    def dimension_str(self):
        return f"{self._i.has_length} x {self._i.has_width} x {self._i.has_height}"

    @Property(int, constant=True)
    def max_weight(self):
        return self._i.has_max_weight

    @Property(str, constant=True)
    def zone(self):
        return self._i.has_zone

    @Property(str, constant=True)
    def z(self):
        return str(int(self._i.has_z))

    @Slot(float, result=str)
    def heat(self, max_freq=None):
        if max_freq:
            return get_heatmap_color(self._i.has_freq / max_freq)
        return self._i.has_freq

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        return self._checked

    @checked.setter
    def set_checked(self, val):
        self._checked = val


class Item(QObject):
    """Item QObject for displaying list of items in warehouse."""

    def __init__(self, item):
        QObject.__init__(self)
        self._i = item
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        return self._i.name

    @Property(str, constant=True)
    def description(self):
        if self._i.has_gtype:
            return f"{self._i.has_description} | {self._i.has_gtype}"
        return self._i.has_description

    @Property(str, constant=True)
    def zone(self):
        return self._i.has_zone

    @Property(str, constant=True)
    def base_dimension(self):
        bu = self._i.has_base_unit
        return f"{bu.has_length} x {bu.has_width} x {bu.has_height}"

    @Property(float, constant=True)
    def base_weight(self):
        return self._i.has_base_unit.has_weight

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        return self._checked

    @checked.setter
    def set_checked(self, val):
        self._checked = val


class Order(QObject):
    """Order QObject for displaying list of orders in warehouse."""

    def __init__(self, order):
        QObject.__init__(self)
        self._i = order
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        return str(self._i.name)

    @Property(str, constant=True)
    def direction(self):
        return self._i.has_direction

    @Property(str, constant=True)
    def date(self):
        return self._i.has_delivery_date.strftime("%x")

    @Property(str, constant=True)
    def item_id(self):
        if len(self._i.has_ordered_items) == 1:
            return str(self._i.has_ordered_items[0].has_item.name)
        return "Multi-item"

    @Property(int, constant=True)
    def num_items(self):
        return len(self._i.has_ordered_items)

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        return self._checked

    @checked.setter
    def set_checked(self, val):
        self._checked = val


class UniversalListModel(QAbstractListModel):
    """Universal class for holding lists in sidebar tabs (locations, items, orders)."""

    ObjectRole = Qt.UserRole + 1

    def __init__(self, object_class, objects=None, selected_objects=None, parent=None):
        super(UniversalListModel, self).__init__(parent)
        self._object_class = object_class
        self._selected = [] if selected_objects is None else selected_objects
        self._all_selected = self._selected
        self._checked = set()
        self._search = ""
        self._filter = 0

        if objects is None:
            self._objects = {}
        else:
            self._objects = {k: self._object_class(v) for k, v in objects.items()}

    filterChanged = Signal()

    def set_data(self, objects):
        self._objects = {k: self._object_class(v) for k, v in objects.items()}

    def set_selected(self, selected, check=False):
        self._selected = selected
        self._all_selected = selected
        if check:
            self.set_checked(selected)
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return len(self._selected)

    def data(self, index, role):
        if index.isValid() and role == UniversalListModel.ObjectRole:
            return self._objects[self._selected[index.row()]]
        return None

    def roleNames(self):
        roles = {}
        roles[UniversalListModel.ObjectRole] = b"object"
        return roles

    def clear_checked(self):
        for n in self._checked:
            self._objects[n].set_checked(False)
        self._checked.clear()
        # TODO: Specify correct range
        self.dataChanged.emit(
            self.createIndex(0, 0), self.createIndex(len(self._selected) - 1, 0)
        )

    def set_checked(self, checked, control=False):
        if not control:
            self.clear_checked()
        self._checked.update(checked)
        self._update_filter()
        for n in self._checked:
            self._objects[n].set_checked(True)
        self.dataChanged.emit(
            self.createIndex(0, 0), self.createIndex(len(self._selected) - 1, 0)
        )

    @Property(int, constant=False, notify=filterChanged)
    def filter(self):
        return self._filter

    @filter.setter
    def set_filter(self, val):
        self._filter = val
        self._update_filter()

    @Slot(str, bool)
    def check(self, _id, val):
        self._objects[_id].set_checked(val)
        if val:
            self._checked.add(_id)
        else:
            self._checked.remove(_id)

    @Slot(str)
    def search(self, val):
        self._search = val
        self._update_filter()

    def _update_filter(self):
        if self._search:
            self._selected = [
                k for k in self._all_selected if self._search.lower() in k.lower()
            ]
        elif self._filter == 0:
            self._selected = self._all_selected
        elif self._filter == 1:
            self._selected = sorted(list(self._checked))
        elif self._filter == 2:
            self._selected = [k for k in self._all_selected if k not in self._checked]
        self.layoutChanged.emit()


class HoverListModel(UniversalListModel):
    """List model for displaying location side view for hovered/selected location."""

    ObjectRole = Qt.UserRole + 1

    def __init__(
        self,
        object_class,
        objects=None,
        selected_objects=None,
        hovered_objects=None,
        parent=None,
    ):
        super(UniversalListModel, self).__init__(parent)
        self._object_class = object_class
        self._selected = [] if selected_objects is None else selected_objects
        self._hovered = [] if hovered_objects is None else hovered_objects
        self._is_hovered = False

        if objects is None:
            self._objects = {}
        else:
            self._objects = {k: self._object_class(v) for k, v in objects.items()}

    def set_selected(self, selected, check=False):
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
