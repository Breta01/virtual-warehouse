# This Python file uses the following encoding: utf-8
import os
import sys

from PySide2 import QtCore
from PySide2.QtGui import QGuiApplication, QIcon, QImage
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

import virtual_warehouse.main_rc
from virtual_warehouse.view_controller import ViewController

try:
    # Win incon support, include in try/except block if you're also targeting Mac/Linux
    from PySide2.QtWinExtras import QtWin

    myappid = "com.bretahajek.virtual-varehouse"
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


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

    app.setWindowIcon(QIcon(":/images/icon.png"))
    engine.load(QtCore.QUrl("qrc:/qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
