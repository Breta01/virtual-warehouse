"""Module providing basic functions for working with warehouse map."""
from PySide2.QtCore import Property, QObject, Signal


class Map(QObject):
    """Object holding basic informations about the map."""

    dataUpdated = Signal()

    def __init__(self, locations=None):
        """Initialize basic properties of map.

        Args:
            locations (dict): dictionary of all locations.
        """
        QObject.__init__(self)
        if locations:
            self.set_data(locations)
        else:
            self._min_x = 0
            self._max_x = 1
            self._min_y = 0
            self._max_y = 1
            self._min_z = 0
            self._max_z = 1
            self._min = 0
            self._max = 1

    def set_data(self, locations):
        """Update properties of map with new data.

        Args:
            locations (dict): dictionary of all locations.
        """
        self._min_x = min(l.has_x for l in locations.values())
        self._max_x = max(l.has_x + l.has_width for l in locations.values())

        self._min_y = min(l.has_y for l in locations.values())
        self._max_y = max(l.has_y + l.has_length for l in locations.values())

        self._min_z = min(l.has_z for l in locations.values())
        self._max_z = max(l.has_z + l.has_height for l in locations.values())

        self._max = max(self._max_x, self._max_y, self._max_z)
        self._min = max(self._min_x, self._min_y, self._min_z)
        self.dataUpdated.emit()

    @Property(float, constant=False, notify=dataUpdated)
    def max(self):
        """Get max value of all coordinates."""
        return self._max

    @Property(float, constant=False, notify=dataUpdated)
    def min(self):
        """Get min value of all coordinates."""
        return self._min

    @Property(float, constant=False, notify=dataUpdated)
    def min_x(self):
        """Get minimal value of X coordinate."""
        return self._min_x

    @Property(float, constant=False, notify=dataUpdated)
    def max_x(self):
        """Get maximal value of X coordinate."""
        return self._max_x

    @Property(float, constant=False, notify=dataUpdated)
    def min_y(self):
        """Get minimal value of Y coordinate."""
        return self._min_y

    @Property(float, constant=False, notify=dataUpdated)
    def max_y(self):
        """Get maximal value of Y coordinate."""
        return self._max_y

    @Property(float, constant=False, notify=dataUpdated)
    def min_z(self):
        """Get minimal value of Z coordinate."""
        return self._min_z

    @Property(float, constant=False, notify=dataUpdated)
    def max_z(self):
        """Get maximal value of Z coordinate."""
        return self._max_z
