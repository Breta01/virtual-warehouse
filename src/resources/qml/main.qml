import Qt.labs.platform 1.1
import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtDataVisualization 1.3
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.3
import QtQml.Models 2.2
import QtQuick.Controls.Material 2.14

ApplicationWindow {
    id: window
    title: qsTr("Virtual Warehouse")
    width: 1000
    height: 600
    visible: true

    menuBar: MenuBar {
        id: menuBar
        Menu {
            title: qsTr("&File")

            MenuItem {
                text: qsTr("&Open")
                onTriggered: openDialog.open()
            }
            MenuItem {
                text: qsTr("&Save As...")
            }
            MenuItem {
                text: qsTr("&Quit")
                onTriggered: Qt.quit()
            }
        }

        Menu {
            title: qsTr("&Edit")

            MenuItem {
                text: qsTr("&Copy")
            }
            MenuItem {
                text: qsTr("Cu&t")
            }
            MenuItem {
                text: qsTr("&Paste")
            }
        }

        Menu {
            title: qsTr("&Options")

            MenuItem {
                text: qsTr("&Help")
            }
            MenuItem {
                text: qsTr("&Settings")
            }
        }
    }

    Column {
        id: contentView
        x: 0
        y: 0
        width: window.width - sidebar.width
        height: window.height

        Item {
            id: surfaceView
            width: contentView.width
            height: contentView.height
            anchors.top: window.top
            anchors.left: window.left

            ColorGradient {
                id: surfaceGradient
                ColorGradientStop {
                    position: 0.0
                    color: "darkslategray"
                }
                ColorGradientStop {
                    id: middleGradient
                    position: 0.25
                    color: "peru"
                }
                ColorGradientStop {
                    position: 1.0
                    color: "red"
                }
            }

            Surface3D {
                id: surfacePlot
                objectName: "surfacePlot"
                width: surfaceView.width
                height: surfaceView.height
                theme: Theme3D {
                    type: Theme3D.ThemeStoneMoss
                    font.family: "STCaiyun"
                    font.pointSize: 35
                    colorStyle: Theme3D.ColorStyleRangeGradient
                    baseGradients: [surfaceGradient]
                }
                axisX: ValueAxis3D {
                    max: 30
                    min: 0
                }
                // Y is up
                axisY: ValueAxis3D {
                    max: 10
                    min: 0
                }
                axisZ: ValueAxis3D {
                    max: 30
                    min: 0
                }


                customItemList: []

                // TODO: add hover effect using inputHandler
                onSelectedElementChanged: {
                    let idx = ViewController.get_selected_idx();
                    surfacePlot.customItemList[idx].textureFile
                            = "resources/images/textures/default.png";


                    if (surfacePlot.selectedCustomItemIndex() !== -1) {
                        let item = surfacePlot.selectedCustomItem();
                        let idx = surfacePlot.selectedCustomItemIndex();
                        item.textureFile = "resources/images/textures/red.png";
                        ViewController.select_item(item.objectName, idx);
                    }
                }
            }

            Button {
                id: removeButton
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.leftMargin: 20
                anchors.bottomMargin: 60
                text: "2D"
                flat: true
                Material.foreground: "white"
                implicitWidth: 40

                background: Rectangle {
                    implicitWidth: 40
                    implicitHeight: 40
                    opacity: enabled ? 1 : 0.3
                    color: parent.down ? "#6b7080" : "#848895"
                    border.color: "#222840"
                    border.width: 1
                    radius: 5
                }

                onClicked: {
                    if (shapeSpawner.instances.length > 0)
                        shapeSpawner.addOrRemove(false)
                }
            }
        }
    }

    Column {
        id: sidebar
        x: contentView.width
        y: 0
        width: 300
        height: window.height

        TabBar {
            id: tabBar
            y: 0
            width: sidebar.width

            TabButton {
                id: tabButton
                text: qsTr("Locations")
            }

            TabButton {
                id: tabButton1
                text: qsTr("Items")
            }

            TabButton {
                id: tabButton2
                text: qsTr("Orders")
            }
        }

        StackLayout {
            y: tabBar.height
            width: parent.width
            height: parent.height - tabBar.height
            currentIndex: tabBar.currentIndex

            Item {
                id: locationTab
                Layout.fillWidth: true
                Layout.fillHeight: true

                LocationListView {}
            }
            Item {
                id: itemTab

                Layout.fillWidth: true
                Layout.fillHeight: true

                ItemListView {}
            }
            Item {
                id: orderTab

                Text {
                    id: elementy
                    width: 164
                    height: 94
                    text: qsTr("Order Tab")
                    font.pixelSize: 20
                    padding: 10
                }
            }
        }
    }

    FileDialog {
        id: openDialog
        title: "Please select a warehouse file"
        nameFilters: ["Excel file (*.xls, *.xlsx)", "CSV file (*.csv)"]
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: ViewController.load(openDialog.fileUrl)
    }

    Connections {
        target: ViewController
        function onModelChanged() {
            surfacePlot.customItemList = []
            for (var row = 0; row < ViewController.model.rowCount(); row++) {
                var item = ViewController.get_item(row)
                var component = Qt.createComponent("CustomItem.qml")
                let instance = component.createObject(surfacePlot, {
                                                          "objectName": item.name,
                                                          "meshFile": item.meshFile,
                                                          "position": Qt.vector3d(
                                                                          item.x,
                                                                          item.z,
                                                                          item.y)
                                                      })
                surfacePlot.customItemList.push(instance)
            }
        }
    }
}



