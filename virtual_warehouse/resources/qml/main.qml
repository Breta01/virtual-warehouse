import Qt.labs.platform 1.1
import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtDataVisualization 1.3
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.3
import QtQml.Models 2.2
import QtQuick.Controls.Material 2.14
import QtGraphicalEffects 1.12

ApplicationWindow {
    id: window
    title: qsTr("Virtual Warehouse")
    width: 1200
    height: 600
    visible: true

    menuBar: MenuBar {
        id: menuBar
        z: 100

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

    Item {
        id: contentView
        x: 0
        y: 0
        width: window.width - sidebar.width
        height: window.height - menuBar.height

        Button {
            id: histogramSwitchButton
            text: qsTr("Heatmap")
            icon.source: "qrc:/images/histogram_icon.png"
            anchors.left: parent.left
            anchors.bottom: viewSwitchButton.top
            checked: ViewController.is_heatmap
            checkable: true
            display: AbstractButton.IconOnly
            anchors.leftMargin: 20
            anchors.bottomMargin: 0
            flat: true
            Material.foreground: "white"
            implicitWidth: 40
            z: 1

            background: Rectangle {
                implicitWidth: 40
                implicitHeight: 40
                opacity: parent.enabled ? 1 : 0.3
                color: parent.checked ? Material.accent : (parent.down ? "#6b7080" : "#848895")
                border.color: "#222840"
                border.width: 1
                radius: 5
            }

            onClicked: {
                ViewController.switch_heatmap()
            }
        }

        Button {
            id: viewSwitchButton
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 20
            anchors.bottomMargin: 20
            text: "3D"
            flat: true
            Material.foreground: "white"
            implicitWidth: 40
            z: 1

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
                mapView2D.visible = mapView3D.visible
                mapView3D.visible = !mapView3D.visible
                viewSwitchButton.text = (mapView3D.visible) ? "2D" : "3D"
                ViewController.switch_view()
            }
        }

        MapView2D {
            id: mapView2D
        }

        Item {
            id: mapView3D
            width: contentView.width
            height: contentView.height
            anchors.top: window.top
            anchors.left: window.left
            visible: false

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
                width: mapView3D.width
                height: mapView3D.height
                theme: Theme3D {
                    type: Theme3D.ThemeStoneMoss
                    font.family: "STCaiyun"
                    font.pointSize: 35
                    colorStyle: Theme3D.ColorStyleRangeGradient
                    baseGradients: [surfaceGradient]
                }
                // TODO: Automatically set values
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
                    let idx = ViewController.get_selected_idx()
                    if (idx >= 0) {
                        surfacePlot.customItemList[idx].textureFile = ":/textures/default.png"
                    }

                    if (surfacePlot.selectedCustomItemIndex() !== -1) {
                        let item = surfacePlot.selectedCustomItem()
                        let idx = surfacePlot.selectedCustomItemIndex()
                        item.textureFile = ":/textures/red.png"
                        ViewController.select_item(idx)
                    }
                }
            }
        }
    }

    Rectangle {
        id: sidebarBg
        x: contentView.width
        y: 0
        z: 20
        width: 300
        height: window.height

        color: Material.background

        Column {
            id: sidebar
            anchors.fill: parent

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
                height: parent.height - 2 * tabBar.height
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

                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    OrderListView {}
                }
            }
        }
    }

    FileDialog {
        id: openDialog
        modality: Qt.WindowModal
        title: "Please select a warehouse file"
        nameFilters: ["Excel file (*.xls, *.xlsx)", "CSV file (*.csv)"]
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: ViewController.load(openDialog.fileUrl)
    }

    Connections {
        target: ViewController
        // TODO: Fix textures
        function onModelChanged() {
            surfacePlot.customItemList = []
            for (var row = 0; row < ViewController.model3D.rowCount(); row++) {
                var item = ViewController.model3D.get(row)
                var component = Qt.createComponent("qrc:/qml/CustomItem.qml")
                let instance = component.createObject(surfacePlot, {
                                                          "objectName": item.name,
                                                          "meshFile": item.mesh_file,
                                                          "position": Qt.vector3d(
                                                                          item.x,
                                                                          item.z,
                                                                          item.y)
                                                      })

                surfacePlot.customItemList.push(instance)
            }
        }

        Component.onCompleted: onModelChanged()
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.66}
}
##^##*/

