import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.3
import QtQml.Models 2.2
import QtQuick.Controls.Material 2.14

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
                text: qsTr("&Import Agents")
                onTriggered: dialogs.openImportAgentsDialog()
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
                text: qsTr("S&ettings")
                onTriggered: dialogs.openSettingsDialog()
            }
            MenuItem {
                text: qsTr("&Help")
                onTriggered: dialogs.openHelpDialog()
            }
        }
    }

    LoadingOverlay {
        progressValue: ViewController.progress_value
        width: parent.width
        anchors.top: menuBar.bottom
        anchors.bottom: parent.bottom
    }

    SplitView {
        anchors.fill: parent
        id: splitView

        focus: true

        property bool controlKey: false

        Keys.onPressed: {
            controlKey = event.modifiers & Qt.ControlModifier
        }

        Keys.onReleased: {
            controlKey = event.modifiers & Qt.ControlModifier
        }

        Item {
            id: contentView
            SplitView.fillWidth: true
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            Item {
                id: mapView
                width: parent.width
                anchors.top: parent.top
                anchors.bottom: timelinePlaceholder.top

                Button {
                    id: itemHistogramSwitchButton
                    text: qsTr("Item Heatmap")
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

                    Text {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 8
                        anchors.rightMargin: 6
                        text: qsTr("Item")
                        color: "white"
                        font.pixelSize: 10
                    }

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
                        } else {
                            ViewController.plugin_manager.active = "item_frequencies"
                        }
                    }
                }

                Button {
                    id: orderHistogramSwitchButton
                    text: qsTr("Order Heatmap")
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

                    Text {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 8
                        anchors.rightMargin: 4
                        text: qsTr("Ord.")
                        color: "white"
                        font.pixelSize: 10
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

                MapView3D {
                    id: mapView3D
                }
            }

            Rectangle {
                id: timelinePlaceholder
                height: (ViewController.agent_manager.active) ? 40 : 0
                width: parent.width
                anchors.bottom: parent.bottom
                color: "white"
                z: -1

                Behavior on height {
                    NumberAnimation {}
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

                Item {
                    id: classSideTab
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ClassView {}
                }

                Item {
                    id: agentsSideTab
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    AgentView {}
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
                    text: "Ontology"
                    width: 120

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
                    id: sideTabBtn3
                    text: "Agents"
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
}
