import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: parent

    LoadingOverlay {
        progressValue: ViewController.onto_manager.progress_value
    }

    ToolBar {
        id: classToolBar
        anchors.top: parent.top
        anchors.topMargin: 0
        width: parent.width

        Material.elevation: 1

        ToolButton {
            id: toolButton1
            text: qsTr("Create:")
            anchors.left: parent.left
            enabled: false

            onClicked: {
                dialogs.openCreateClassDialog()
            }
        }

        ToolButton {
            id: toolButton2
            text: qsTr("Query")
            anchors.left: toolButton1.right

            onClicked: {
                dialogs.openCreateQueryDialog()
            }
        }

        ToolButton {
            id: toolButton3
            text: qsTr("Class")
            anchors.left: toolButton2.right
            enabled: ViewController.onto_manager.java_correct

            onClicked: {
                dialogs.openCreateClassDialog()
            }
        }
    }

    Text {
        id: cErrorText
        anchors.top: classToolBar.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.margins: 8
        visible: !ViewController.onto_manager.java_correct
        height: visible ? 50 : 0
        font.pixelSize: 11
        wrapMode: Text.Wrap
        text: "Your Java path is incorrect. Please go to the \"Options > Settings\" and set correct path."
        color: "red"
    }

    ScrollView {
        anchors.top: cErrorText.bottom
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ListView {
            id: classList

            anchors.fill: parent
            anchors.topMargin: 0
            anchors.rightMargin: 8
            anchors.leftMargin: 8
            topMargin: 8
            bottomMargin: 8
            clip: true
            spacing: 8

            model: ViewController.onto_manager.objects

            delegate: Item {
                id: classItem
                width: classList.width
                height: 52

                Rectangle {
                    id: rectangle
                    color: model.modelData["is_class"] ? "#eeeeee" : "#eeeefe"
                    anchors.fill: parent
                }

                RoundButton {
                    icon.source: "qrc:/images/menu_icon.png"
                    id: roundButton
                    width: 36
                    height: 36
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 5
                    padding: 8
                    anchors.rightMargin: 0
                    flat: true

                    onClicked: contextMenu.popup()

                    Menu {
                        id: contextMenu
                        width: 150
                        MenuItem {
                            text: "Select"
                            onClicked: {
                                ViewController.select_onto_objects(
                                           model.modelData["is_class"],
                                           model.modelData["name"],
                                           model.modelData["class"],
                                           true)
                                sideTabbar.currentIndex = 0
                                tabBar.currentIndex = ((model.modelData["class"] === "RackLocation") ? 0 : ((model.modelData["class"] === "Item") ? 1 : 2))
                            }
                        }
                        MenuItem {
                            text: "Add to selection"
                            onClicked: {
                                ViewController.select_onto_objects(
                                           model.modelData["is_class"],
                                           model.modelData["name"],
                                           model.modelData["class"],
                                           false)
                                sideTabbar.currentIndex = 0
                                tabBar.currentIndex = ((model.modelData["class"] === "RackLocation") ? 0 : ((model.modelData["class"] === "Item") ? 1 : 2))
                            }
                        }
                        MenuItem {
                            text: "Edit"
                            visible: !model.modelData["is_class"]
                            enabled: visible
                            height: visible ? implicitHeight : 0
                            onClicked: dialogs.openCreateQueryDialog(model.modelData["name"], model.modelData["class"], model.modelData["query"])
                        }
                        MenuItem {
                            text: "Delete"
                            onClicked: ViewController.onto_manager.delete(
                                           model.modelData["is_class"],
                                           model.modelData["name"])
                        }
                    }
                }

                Text {
                    id: name
                    text: model.modelData["name"]
                    anchors.left: parent.left
                    anchors.top: parent.top
                    horizontalAlignment: Text.AlignLeft
                    anchors.topMargin: 8
                    anchors.leftMargin: 8
                    font.pixelSize: 14
                    font.bold: true
                }

                Text {
                    id: baseClass
                    color: "#333"
                    text: model.modelData["class"]
                    anchors.left: name.right
                    anchors.baseline: name.baseline
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Text {
                    id: instanceCountText
                    color: "#666"
                    text: qsTr("Instances:")
                    anchors.left: parent.left
                    anchors.top: name.bottom
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Text {
                    id: instanceCount
                    color: Material.accent
                    text: model.modelData["count"]
                    anchors.left: instanceCountText.right
                    anchors.top: name.bottom
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 4
                    anchors.topMargin: 4
                }
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/

