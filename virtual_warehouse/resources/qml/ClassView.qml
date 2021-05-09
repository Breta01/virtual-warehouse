import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: parent

    ToolBar {
        id: classToolBar
        anchors.top: parent.top
        anchors.topMargin: 0
        width: parent.width

        Material.elevation: 1

        ToolButton {
            id: toolButton1
            text: qsTr("Create")
            anchors.left: parent.left

            onClicked: {
                dialogs.openCreateClassDialog()
            }
        }
    }

    ScrollView {
        anchors.top: classToolBar.bottom
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

            model: ViewController.onto_manager.classes

            delegate: Item {
                id: classItem
                width: classList.width
                height: 52

                Rectangle {
                    id: rectangle
                    color: "#eeeeee"
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
                            onClicked: ViewController.select_class(
                                           model.modelData["name"],
                                           model.modelData["class"])
                        }
                        MenuItem {
                            text: "Delete"
                            onClicked: ViewController.onto_manager.delete_class(
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

