"""Main app module starting the Virtual Warehouse app."""
import sys

from PySide2 import QtCore
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine

import virtual_warehouse.main_rc  # skipcq: PYL-W0611
from virtual_warehouse import __version__
from virtual_warehouse.view_controller import ViewController

try:
    # Win incon support, include in try/except block if you're also targeting Mac/Linux
    from PySide2.QtWinExtras import QtWin

    myappid = "com.bretahajek.virtual-varehouse"
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def run():
    """Start Virtual Warehouse application."""
    QGuiApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("Bretislav Hajek")
    app.setOrganizationDomain("bretahajek.com")
    app.setApplicationName("Virtual Warehouse")
    app.setApplicationVersion(__version__)
    engine = QQmlApplicationEngine()

    controller = ViewController()
    engine.rootContext().setContextProperty("ViewController", controller)
    engine.rootContext().setContextProperty("versionNumber", __version__)

    app.setWindowIcon(QIcon(":/images/icon.png"))
    engine.load(QtCore.QUrl("qrc:/qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
