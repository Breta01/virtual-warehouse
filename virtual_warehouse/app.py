# This Python file uses the following encoding: utf-8
import os
import sys

from PySide2.QtGui import QGuiApplication, QIcon, QImage
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

from virtual_warehouse.main_rc import *
from virtual_warehouse.view_controller import ViewController


def run():
    dir_path = os.path.dirname(__file__)

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("Bretislav Hajek")
    app.setOrganizationDomain("bretahajek.com")
    app.setApplicationName("Virtual Warehouse")
    app.setApplicationVersion("0.1")
    engine = QQmlApplicationEngine()

    controller = ViewController()
    #    qmlRegisterType(ViewController, "VirtualWarehouse", 1, 0, "ViewController")
    engine.rootContext().setContextProperty("ViewController", controller)

    app.setWindowIcon(QIcon(os.path.join(dir_path, "resources/images/icon.png")))
    engine.load(os.path.join(dir_path, "resources/qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
