"""Module providing content for sidebar tabs: locations/items/orders.
It provides classes wrapping the location/item/order objects along with list model.
It also provides functionality for checking different items.

HoverListModel is for displaying side view of location which is selected or hovered.
"""
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

locale.setlocale(locale.LC_ALL, "")


class TabLocation(QObject):
    """Location QObject for displaying list of selected locations."""

    def __init__(self, location):
        QObject.__init__(self)
        self._i = location
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        """Get name of location (property)."""
        return self._i.name

    @Property(str, constant=True)
    def class_str(self):
        """Get class + subclass representation (property)."""
        if self._i.has_lsubclass:
            return f"{self._i.has_lclass} > {self._i.has_lsubclass}"
        return self._i.has_lclass

    @Property(str, constant=True)
    def dimension_str(self):
        """Get dimension representation (property)."""
        return f"{self._i.has_length} x {self._i.has_width} x {self._i.has_height}"

    @Property(int, constant=True)
    def max_weight(self):
        """Get maximal weight supported by location (property)."""
        return self._i.has_max_weight

    @Property(str, constant=True)
    def zone(self):
        """Get zone where is location located (property)."""
        return self._i.has_zone

    @Property(str, constant=True)
    def z(self):
        """Get z - vertical direction - coordinate of location (property)."""
        return str(int(self._i.has_z))

    @Property(float, constant=True)
    def heat(self):
        """Calculate heat for side-view."""
        return self._i.has_freq

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        """Get checked state of location (property)."""
        return self._checked

    @checked.setter
    def set_checked(self, val):
        """Set checked state of location (property setter)."""
        self._checked = val
        self.checkedChanged.emit()


class TabItem(QObject):
    """Item QObject for displaying list of items in warehouse."""

    def __init__(self, item):
        QObject.__init__(self)
        self._i = item
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        """Get name of item (property)."""
        return self._i.name

    @Property(str, constant=True)
    def description(self):
        """Get description representation of item (property)."""
        if self._i.has_gtype:
            return f"{self._i.has_description} | {self._i.has_gtype}"
        return self._i.has_description

    @Property(str, constant=True)
    def zone(self):
        """Get zone which item requires (property)."""
        return self._i.has_zone

    @Property(str, constant=True)
    def base_dimension(self):
        """Get representation of base dimension of item package (property)."""
        bu = self._i.has_base_unit
        return f"{bu.has_length} x {bu.has_width} x {bu.has_height}"

    @Property(float, constant=True)
    def base_weight(self):
        """Get base weight of item package (property)."""
        return self._i.has_base_unit.has_weight

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        """Get item checked state (property)."""
        return self._checked

    @checked.setter
    def set_checked(self, val):
        """Set item checked state (property setter)."""
        self._checked = val
        self.checkedChanged.emit()


class TabOrder(QObject):
    """Order QObject for displaying list of orders in warehouse."""

    def __init__(self, order):
        QObject.__init__(self)
        self._i = order
        self._checked = False

    checkedChanged = Signal()

    @Property(str, constant=True)
    def name(self):
        """Get name order (property)."""
        return str(self._i.name)

    @Property(str, constant=True)
    def direction(self):
        """Get direction of order (property)."""
        return self._i.has_direction

    @Property(str, constant=True)
    def date(self):
        """Get formatted date of order (property)."""
        return self._i.has_delivery_date.strftime("%x")

    @Property(str, constant=True)
    def item_id(self):
        """Get representation of item/items (property)."""
        if len(self._i.has_ordered_items) == 1:
            return str(self._i.has_ordered_items[0].has_item.name)
        return "Multi-item"

    @Property(int, constant=True)
    def num_items(self):
        """Get number of items in order."""
        return len(self._i.has_ordered_items)

    @Property(bool, constant=False, notify=checkedChanged)
    def checked(self):
        """Get order checked state (property)."""
        return self._checked

    @checked.setter
    def set_checked(self, val):
        """Set order checked state (property setter)."""
        self._checked = val
        self.checkedChanged.emit()


class UniversalListModel(QAbstractListModel):
    """Universal class for holding lists in sidebar tabs (locations, items, orders).

    Attributes:
        checkChanged (Signal): emits on new item in list checked.
            Emits update data (list[bool, bool, list[str]]) which represents:
            [is_clear, is_add, list_of_object_ids]. This is used to update plugins.
        filterChanged (Signal): emits on filter value changed

    """

    ObjectRole = Qt.UserRole + 1

    def __init__(self, object_class, objects=None, selected_objects=None, parent=None):
        """Initialize list model.

        Args:
            object_class (cls): class which wraps objects stored in list (TabItem,...)
            objects (dict[str, object]): dictionary of objects stored in list
            selected_objects (list[str]): list of ids (keys) of selected objects,
                selected objects are displayed in the list
            parent (object): required param for initialization
        """
        super(UniversalListModel, self).__init__(parent)
        self._object_class = object_class
        self._selected = [] if selected_objects is None else selected_objects
        self._all_selected = self._selected
        self.checked = set()
        self._search_text = ""
        self._filter = 0

        if objects is None:
            self._objects = {}
        else:
            self._objects = {k: self._object_class(v) for k, v in objects.items()}

    # Emits list as [is_clear, is_add, list_of_ids]
    checkChanged = Signal("QVariantList")
    filterChanged = Signal()

    def set_data(self, objects):
        """Set new objects and wrap then in wrapper class."""
        self._objects = {k: self._object_class(v) for k, v in objects.items()}

    def set_selected(self, selected, check=False):
        """Set new list of selected objects."""
        self._selected = selected
        self._all_selected = selected
        if check:
            self.set_checked(selected)
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Get number of items in list (required method)."""
        return len(self._selected)

    def data(self, index, role):
        """Return data for given role and index (required method)."""
        if index.isValid() and role == UniversalListModel.ObjectRole:
            return self._objects[self._selected[index.row()]]
        return None

    def roleNames(self):  # skipcq: PYL-R0201
        """Set role names, QAbstractListModel requires implementation of this method."""
        roles = {}
        roles[UniversalListModel.ObjectRole] = b"object"
        return roles

    def clear_checked(self):
        """Clear all checked items in list."""
        for n in self.checked:
            self._objects[n].set_checked(False)
        self.checked.clear()

    def set_checked(self, checked, control=False):
        """Set/add list of newly checked items in list.

        Args:
            checked (list[str]): list of ids of checked objects
            control (bool): if control is set to true, items are added to checked items
                otherwise originally checked items are cleared firs.
        """
        if not control:
            self.clear_checked()

        self.checked.update(checked)
        self._update_filter()
        for n in self.checked:
            self._objects[n].set_checked(True)

        self.checkChanged.emit([not control, True, checked])

    @Property(int, constant=False, notify=checkChanged)
    def check_state(self):
        """Return state of main checkbox of all visible check boxes.
        States: unchecked (0)/ partially checked (1) / checked (2)
        """
        selected_set = set(self._selected)
        match_count = sum(map(lambda x: x in selected_set, self.checked))
        if match_count:
            return 2 if match_count == len(self._selected) else 1
        return 0

    @Property(int, constant=False, notify=filterChanged)
    def filter(self):
        """Filter property for splitting tabs on all(0)/checked(1)/unchecked(2)."""
        return self._filter

    @filter.setter
    def set_filter(self, val):
        """Set value of filter property.

        Args:
            val (int): new value of filter (one of 0, 1, 2)
        """
        if self._filter != val:
            self._filter = val
            self.filterChanged.emit()
            self._update_filter()
            self.checkChanged.emit(
                [False, False, []]
            )  # Required for check_state update

    @Slot(bool)
    def check_all(self, check=True):
        """Check/Uncheck all currently visible list items."""
        self.set_checked(self._selected if check else [])

    @Slot(str, bool)
    def check(self, _id, check=True):
        """Check/uncheck one item in the list."""
        self._objects[_id].set_checked(check)
        if check:
            self.checked.add(_id)
        else:
            self.checked.remove(_id)

        self.checkChanged.emit([False, check, [_id]])

    @Slot(str)
    def search(self, text):
        """Search for text between object ids."""
        self._search_text = text
        self._update_filter()

    def _update_filter(self):
        """Filter items appearing in one of the lists: all/checked/unchecked/search."""
        if self._search_text:
            self._selected = [
                k for k in self._all_selected if self._search_text.lower() in k.lower()
            ]
        elif self._filter == 0:
            self._selected = self._all_selected
        elif self._filter == 1:
            self._selected = sorted(list(self.checked))
        elif self._filter == 2:
            self._selected = [k for k in self._all_selected if k not in self.checked]
        self.layoutChanged.emit()


class SideviewListModel(UniversalListModel):
    """List model for displaying location side view for hovered/selected location."""

    ObjectRole = Qt.UserRole + 1

    maxChanged = Signal()

    def __init__(
        self,
        object_class,
        objects=None,
        selected_objects=None,
        hovered_objects=None,
        parent=None,
    ):
        """Initialize list model.

        Args:
            object_class (cls): class which wraps objects stored in list (TabItem,...)
            objects (dict[str, object]): dictionary of objects stored in list
            selected_objects (list[str]): list of ids (keys) of selected objects,
                selected objects are displayed in the list
            hovered_objects (list[str]): list of ids (keys) of objects that are hovered
            parent (object): required param for initialization
        """
        super(SideviewListModel, self).__init__(parent)
        self._object_class = object_class
        self._selected = [] if selected_objects is None else selected_objects
        self._hovered = [] if hovered_objects is None else hovered_objects
        self._selected_max_heat = 1
        self._hovered_max_heat = 1
        self._is_hovered = False

        if objects is None:
            self._objects = {}
        else:
            self._objects = {k: self._object_class(v) for k, v in objects.items()}

    def set_selected(self, selected, check=False):
        """Set list of names of clicked locations."""
        self._selected = list(reversed(selected))
        if self._selected:
            self._selected_max_heat = max(self._objects[k].heat for k in self._selected)
            self.maxChanged.emit()
        self.layoutChanged.emit()

    def set_hovered(self, hovered, is_hovered=True):
        """Set list of names of currently hovered locations."""
        self._is_hovered = is_hovered
        self._hovered = list(reversed(hovered))
        if self._hovered:
            self._hovered_max_heat = max(self._objects[k].heat for k in self._hovered)
            self.maxChanged.emit()
        self.layoutChanged.emit()

    @Property(float, constant=False, notify=maxChanged)
    def max_heat(self):
        """Get current max heat of selected/hovered location."""
        return self._hovered_max_heat if self._is_hovered else self._selected_max_heat

    @Slot()
    def update(self):
        """Update maximal value, emit maxChanged signal which results in list redraw."""
        if self._selected:
            self._selected_max_heat = max(self._objects[k].heat for k in self._selected)
            self.maxChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Get number of items in list (required method)."""
        if self._is_hovered:
            return len(self._hovered)
        return len(self._selected)

    def data(self, index, role):
        """Return data for given role and index (required method)."""
        if index.isValid() and role == UniversalListModel.ObjectRole:
            if self._is_hovered:
                return self._objects[self._hovered[index.row()]]
            return self._objects[self._selected[index.row()]]
        return None
