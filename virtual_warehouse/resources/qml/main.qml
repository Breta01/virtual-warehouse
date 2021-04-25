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

    Dialogs {
        id: dialogs
    }

    menuBar: MenuBar {
        id: menuBar
        z: 100

        Menu {
            title: qsTr("&File")

            MenuItem {
                text: qsTr("&Open")
                onTriggered: dialogs.openImportFileDialog()
            }
            MenuItem {
                text: qsTr("&Export Ontology")
                onTriggered: dialogs.openSaveFileDialog()
            }
            MenuItem {
                text: qsTr("&Quit")
                onTriggered: Qt.quit()
            }
        }

        Menu {
            title: qsTr("&Plugins")

            MenuItem {
                text: "&None"
                checked: ViewController.plugin_manager.active === ""
                autoExclusive: true
                onTriggered: ViewController.plugin_manager.active = null
            }

            Repeater {
                model: ViewController.plugin_manager.names

                MenuItem {
                    text: model.modelData["name"]
                    autoExclusive: true
                    checked: ViewController.plugin_manager.active === model.modelData["module"]
                    onTriggered: ViewController.plugin_manager.active = model.modelData["module"]
                }
            }
        }

        Menu {
            title: qsTr("Option&s")

            MenuItem {
                text: qsTr("&Help")
                onTriggered: dialogs.openHelpDialog()
            }
            //            MenuItem {
            //                text: qsTr("&Settings")
            //            }
        }
    }

    Item {
        id: loadingOverlay
        width: parent.width
        anchors.top: menuBar.bottom
        anchors.bottom: parent.bottom
        z: 300
        visible: progressBar.value != 1

        Rectangle {
            opacity: 0.4
            anchors.fill: parent
            color: "#29323c"
            border.width: 0

            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: false
                hoverEnabled: true
                preventStealing: true
            }
        }

        Rectangle {
            height: 20
            width: 220
            color: "white"
            border.width: 0
            radius: 2
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            ProgressBar {
                id: progressBar
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                value: ViewController.progress_value
                indeterminate: (value == 0)
                Behavior on value {
                    NumberAnimation {}
                }
            }
        }
    }

    SplitView {
        anchors.fill: parent

        Item {
            id: contentView
            SplitView.fillWidth: true
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            Button {
                id: itemHistogramSwitchButton
                text: qsTr("Heatmap")
                icon.source: "qrc:/images/histogram_icon.png"
                anchors.left: parent.left
                anchors.bottom: orderHistogramSwitchButton.top
                checked: ViewController.plugin_manager.active === "item_frequencies"
                checkable: true
                autoExclusive: true
                display: AbstractButton.IconOnly
                anchors.leftMargin: 20
                anchors.bottomMargin: 0
                flat: true
                Material.foreground: "white"
                implicitWidth: 40
                visible: mapView2D.visible
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
                    if (ViewController.plugin_manager.active === "item_frequencies") {
                        ViewController.plugin_manager.active = null
                        checked = false
                    } else {
                        ViewController.plugin_manager.active = "item_frequencies"
                        checked = true
                    }
                }
            }

            Button {
                id: orderHistogramSwitchButton
                text: qsTr("Heatmap")
                icon.source: "qrc:/images/histogram_icon.png"
                anchors.left: parent.left
                anchors.bottom: viewSwitchButton.top
                checked: ViewController.plugin_manager.active === "order_frequencies"
                checkable: true
                autoExclusive: true
                display: AbstractButton.IconOnly
                anchors.leftMargin: 20
                anchors.bottomMargin: 0
                flat: true
                Material.foreground: "white"
                implicitWidth: 40
                visible: mapView2D.visible
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
                    if (ViewController.plugin_manager.active === "order_frequencies") {
                        ViewController.plugin_manager.active = null
                    } else {
                        ViewController.plugin_manager.active = "order_frequencies"
                    }
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
                    selectionMode: AbstractGraph3D.SelectionSlice
                                   | AbstractGraph3D.SelectionItemAndRow
                    scene.activeCamera.cameraPreset: Camera3D.CameraPresetIsometricLeft
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
                        reversed: true
                    }

                    customItemList: []

                    // TODO: add hover effect using inputHandler
                    onSelectedElementChanged: {
                        // TODO: Control - selection of multiple locations
                        var control = false
                        var selected_idxs = ViewController.get_selected()
                        for (var i = 0; !control
                             && i < selected_idxs.length; i++) {
                            var idx = selected_idxs[i]
                            if (idx >= 0) {
                                surfacePlot.customItemList[idx].textureFile
                                        = ":/textures/default.png"
                            }
                        }

                        if (surfacePlot.selectedCustomItemIndex() !== -1) {
                            let item = surfacePlot.selectedCustomItem()
                            let idx = surfacePlot.selectedCustomItemIndex()
                            item.textureFile = ":/textures/red.png"
                            ViewController.select_map_location(idx, control)
                        }
                    }
                }
            }
        }

        Rectangle {
            id: sidebarBg
            SplitView.preferredWidth: 330
            SplitView.minimumWidth: 290
            z: 20
            anchors.bottom: parent.bottom
            anchors.top: parent.top

            color: Material.background

            StackLayout {
                anchors.left: parent.left
                width: parent.width - sideTabbar.height
                height: parent.height
                currentIndex: sideTabbar.currentIndex

                Item {
                    id: dataSideTab
                    Layout.fillWidth: true
                    Layout.fillHeight: true

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

                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                OrderListView {}
                            }
                        }
                    }
                }
            }

            TabBar {
                id: sideTabbar
                width: parent.height
                anchors.left: parent.right
                anchors.top: parent.top
                transformOrigin: "TopLeft"
                contentHeight: 30
                rotation: 90
                leftPadding: 5
                spacing: 5

                background: Rectangle {
                    color: "#eee"
                    Rectangle {
                        color: Material.primary
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 1
                    }
                }

                TabButton {
                    id: sideTabBtn1
                    text: "Data"
                    width: 90

                    background: Rectangle {
                        color: "white"
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 1
                        height: parent.height - 5
                        border.color: Material.primary
                        border.width: 0
                        radius: 4

                        Rectangle {
                            color: parent.color
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            height: parent.radius
                        }
                    }
                }

                TabButton {
                    id: sideTabBtn2
                    text: "Classes"
                    width: 90

                    background: Rectangle {
                        color: "white"
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 1
                        height: parent.height - 5
                        border.color: Material.primary
                        border.width: 0
                        radius: 4

                        Rectangle {
                            color: parent.color
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            height: parent.radius
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: ViewController

        function onModelChanged() {
            surfacePlot.removeCustomItems()
            for (var row = 0; row < ViewController.model3D.rowCount(); row++) {
                var item = ViewController.model3D.get(row)
                var component = Qt.createComponent("qrc:/qml/CustomItem.qml")
                var instance = component.createObject(surfacePlot, {
                                                          "objectName": item.name,
                                                          "meshFile": item.mesh_file,
                                                          "position": Qt.vector3d(
                                                                          item.x,
                                                                          item.z,
                                                                          item.y)
                                                      })

                surfacePlot.addCustomItem(instance)
            }
        }

        function onItemSelected() {// TODO: select items based on 2D map
        }

        Component.onCompleted: onModelChanged()
    }
}
