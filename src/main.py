# This Python file uses the following encoding: utf-8
import os
import parser.excel_parser as parser
import random
import sys

from PySide2.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
    Slot,
)
from PySide2.QtDataVisualization import QtDataVisualization as QDV
from PySide2.QtGui import QGuiApplication, QIcon, QImage
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

from main_rc import *

dir_path = os.path.dirname(__file__)


class MyListModel(QAbstractListModel):
    # Our custom roles
    MeshRole = Qt.UserRole + 1

    def __init__(self, on_change, parent=None):
        super(MyListModel, self).__init__(parent)
        self._on_change = on_change
        self._assets = []

    def add(self):
        self._assets.append({"meshFile": "resources/objects/oilrig.obj"})
        self._on_change()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._assets)

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._assets[index.row()]

            if role == MyListModel.Mesh:
                return item["meshFile"]

    def get(self, index):
        return self._assets[index]

    def roleNames(self):
        roles = dict()
        roles[MyListModel.Mesh] = b"meshFile"
        return roles


class ViewController(QObject):
    def __init__(self, parent=None):
        super(ViewController, self).__init__(parent)
        self._model = MyListModel(on_change=lambda: self.modelChanged.emit())

    modelChanged = Signal()

    @Property(QObject, constant=False, notify=modelChanged)
    def model(self):
        return self._model
        return [QDV.QCustom3DItem(meshFile="resources/objects/oilrig.obj")]

    @Slot(int, result=str)
    def get_item(self, index):
        return self._model.get(index)["meshFile"]

    @Slot()
    def add(self):
        self._model.add()

    @Slot(str)
    def load(self, file_path):
        # TODO: Threading
        locations, items, balance, orders = parser.parse_document(
            file_path[len("file://") :]
        )
        print(locations)


if __name__ == "__main__":
    dir_path = os.path.dirname(__file__)

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("Bretislav Hajek")
    app.setOrganizationDomain("bretahajek.com")
    engine = QQmlApplicationEngine()

    controller = ViewController()
    #    qmlRegisterType(ViewController, "VirtualWarehouse", 1, 0, "ViewController")
    engine.rootContext().setContextProperty("ViewController", controller)

    app.setWindowIcon(QIcon(os.path.join(dir_path, "resources/images/icon.png")))
    engine.load(os.path.join(dir_path, "resources/qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
