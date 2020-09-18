# This Python file uses the following encoding: utf-8
import os
import random
import sys

from PySide2.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide2.QtDataVisualization import QtDataVisualization as QDV
from PySide2.QtGui import QGuiApplication, QIcon, QImage, QQuaternion, QVector3D
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtQuick import QQuickItem

from main_rc import *

dir_path = os.path.dirname(__file__)


class ViewController(QDV.Q3DSurface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #        color = QImage(2, 2, QImage.Format_RGB32)
    #        color.fill(Qt.darkMagenta)

    #        item = QDV.QCustom3DItem(
    #            os.path.join(dir_path, "resources/objects/oilrig.obj"),
    #            QVector3D(0, 0, 0),
    #            QVector3D(0.05, 0.05, 0.05),
    #            QQuaternion(0, 1, 0, 0),
    #            color)
    #        graph.addCustomItem(item)
    #        item = QDV.QCustom3DItem(
    #            os.path.join(dir_path, "resources/objects/oilrig.obj"),
    #            QVector3D(0, 1, 0),
    #            QVector3D(0.05, 0.05, 0.05),
    #            QQuaternion(0, 1, 0, 0),
    #            color)
    #        graph.addCustomItem(item)
    #        handler = QDV.Q3DInputHandler()

    # graph.selectedElementChanged.connect(self.handleElementSelect)
    # graph.addInputHandler(handler)

    def handleElementSelect(type):
        if type == QDV.QAbstract3DGraph.ElementType.ElementCustomItem:
            item = graph.selectedCustomItem()
            print(graph.selectedCustomItemIndex())
            color = QImage(2, 2, QImage.Format_RGB32)
            color.fill(Qt.blue)
            item.setTextureImage(color)


if __name__ == "__main__":
    dir_path = os.path.dirname(__file__)

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("somename")
    app.setOrganizationDomain("somename")
    engine = QQmlApplicationEngine()

    qmlRegisterType(ViewController, "VirtualWarehouse", 1, 0, "ViewController")

    app.setWindowIcon(QIcon(os.path.join(dir_path, "resources/images/icon.png")))
    engine.load(os.path.join(dir_path, "resources/qml/main.qml"))

    print(engine.rootObjects())

    graph = QDV.Q3DSurface()
    print(graph)
    print(QDV.Q3DSurface)

    if not engine.rootObjects():
        sys.exit(-1)

    class Conn:
        def __init__(self):
            self.connected = False

        def select(self):
            #        print(engine.rootObjects()[0].findChildren(QQuickItem, 'surfaceView'))
            # print(engine.rootObjects()[0].activeFocusItem())
            print(engine.rootObjects()[0].findChild(QDV.Q3DSurface, "surfacePlot"))
            print(engine.rootObjects()[0].findChild(QQuickItem, "surfacePlot"))
            print("Con", self.connected)
            if not self.connected:
                graph = engine.rootObjects()[0].findChild(QQuickItem, "surfacePlot")
                color = QImage(2, 2, QImage.Format_RGB32)
                color.fill(Qt.darkMagenta)

                item = QDV.QCustom3DItem(
                    os.path.join(dir_path, "resources/objects/oilrig.obj"),
                    QVector3D(0, 0, 0),
                    QVector3D(0.05, 0.05, 0.05),
                    QQuaternion(0, 1, 0, 0),
                    color,
                )
                graph.addCustomItem(item)
                self.connected = True

    #    conn = Conn()
    #    timer = QTimer(engine)
    #    timer.setSingleShot(True)
    #    timer.timeout.connect(conn.select)
    #    timer.start(1000)
    ctx = engine.rootContext()
    print(ctx)
    object = ctx.contextObject()
    print(object)

    #    engine.rootObjects()[0].activeFocusItemChanged.connect(conn.select)
    sys.exit(app.exec_())
