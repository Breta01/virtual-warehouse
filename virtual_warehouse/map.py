"""Module providing basic functions for working with warehouse map."""
from PySide2.QtCore import Property, QObject


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
        self._min_x = min(l.has_x for l in locations.values())
        self._max_x = max(l.has_x + l.has_width for l in locations.values())

        self._min_y = min(l.has_y for l in locations.values())
        self._max_y = max(l.has_y + l.has_length for l in locations.values())

        self._min_z = min(l.has_z for l in locations.values())
        self._max_z = max(l.has_z + l.has_height for l in locations.values())

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
