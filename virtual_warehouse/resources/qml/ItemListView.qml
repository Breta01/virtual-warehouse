import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: itemTab

    FilterMenu {
        id: toolBar
        model: ViewController.item_model
    }

    ConnectionsMenu {
        id: connectionsBar
        toolBarModel: toolBar.model

        dst1: "Locations"
        idx1: 0
        fun1: ViewController.checked_items_to_locations
        mdl1: ViewController.location_model

        dst2: "Orders"
        idx2: 2
        fun2: ViewController.checked_items_to_orders
        mdl2: ViewController.order_model
    }

    ScrollView {
        anchors.top: toolBar.bottom
        anchors.bottom: connectionsBar.top
        anchors.right: parent.right
        anchors.left: parent.left
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ListView {
            id: itemList

            anchors.fill: parent
            anchors.topMargin: 0
            anchors.rightMargin: 8
            anchors.leftMargin: 8
            topMargin: 8
            clip: true
            spacing: 8

            model: ViewController.item_model

            delegate: Item {
                id: itemItem
                height: 100
                width: itemList.width

                Rectangle {
                    id: rectangle
                    x: 0
                    y: 0
                    anchors.bottomMargin: -8
                    color: "#eeeeee"
                    border.color: "#eeeeee"
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: itemZone.bottom
                }

                //            RoundButton {
                //                icon.source: "qrc:/images/menu_icon.png"
                //                id: itemMenuButton
                //                width: 36
                //                height: 36
                //                anchors.right: itemCheckButton.left
                //                anchors.top: parent.top
                //                anchors.topMargin: 5
                //                padding: 8
                //                anchors.rightMargin: 0
                //                flat: true
                //            }
                CheckDelegate {
                    id: itemCheckButton
                    anchors.right: parent.right
                    anchors.top: parent.top
                    checked: model.object.checked
                    anchors.topMargin: 5
                    anchors.rightMargin: 8
                    padding: 8
                    width: 36
                    height: 36

                    onClicked: ViewController.item_model.check(
                                   model.object.name, checked)
                }

                Text {
                    id: itemID
                    text: model.object.name
                    anchors.left: parent.left
                    anchors.top: parent.top
                    horizontalAlignment: Text.AlignLeft
                    anchors.topMargin: 8
                    anchors.leftMargin: 8
                    font.pixelSize: 14
                    font.bold: true
                }

                Text {
                    id: itemGtype
                    color: "#333333"
                    text: model.object.description
                    anchors.left: parent.left
                    anchors.top: itemID.bottom
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Rectangle {
                    id: itemUnderline
                    x: 0
                    anchors.top: itemGtype.bottom
                    anchors.topMargin: 4
                    height: 1
                    color: Material.accent
                    width: parent.width
                }

                Image {
                    id: itemDimensionIcon
                    source: "qrc:/images/dimension_icon.png"
                    smooth: true
                    sourceSize.height: 19
                    sourceSize.width: 19
                    height: itemDimension.height + 5
                    width: itemDimension.height + 5
                    anchors.left: parent.left
                    anchors.top: itemUnderline.bottom
                    anchors.leftMargin: 8
                    anchors.topMargin: 8
                }

                Text {
                    id: itemDimension
                    anchors.left: itemDimensionIcon.right
                    anchors.leftMargin: 4
                    text: model.object.base_dimension
                    anchors.verticalCenter: itemDimensionIcon.verticalCenter
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignLeft
                }

                Image {
                    id: itemWeightIcon
                    source: "qrc:/images/max_weight_icon.png"
                    anchors.horizontalCenterOffset: 8
                    anchors.horizontalCenter: parent.horizontalCenter
                    smooth: true
                    sourceSize.height: 19
                    sourceSize.width: 19
                    height: itemWeight.height + 5
                    width: itemWeight.height + 5
                    anchors.top: itemUnderline.bottom
                    anchors.topMargin: 8
                }

                Text {
                    id: itemWeight
                    anchors.left: itemWeightIcon.right
                    anchors.leftMargin: 4
                    text: model.object.base_weight
                    anchors.verticalCenter: itemWeightIcon.verticalCenter
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    id: itemZoneIcon
                    color: "#333333"
                    anchors.left: parent.left
                    anchors.top: itemDimension.bottom
                    anchors.leftMargin: 8
                    anchors.topMargin: 8
                    text: "Zone:"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    id: itemZone
                    anchors.left: itemZoneIcon.right
                    anchors.top: itemDimension.bottom
                    anchors.leftMargin: 4
                    anchors.topMargin: 8
                    text: model.object.zone
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignLeft
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

