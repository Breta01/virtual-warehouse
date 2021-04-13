import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: orderTab

    FilterMenu {
        id: toolBar
        model: ViewController.order_model
    }

    ConnectionsMenu {
        id: connectionsBar
        toolBarModel: toolBar.model

        dst1: "Locations"
        idx1: 0
        fun1: ViewController.checked_orders_to_locations
        mdl1: ViewController.location_model

        dst2: "Items"
        idx2: 1
        fun2: ViewController.checked_orders_to_items
        mdl2: ViewController.item_model
    }

    ScrollView {
        anchors.top: toolBar.bottom
        anchors.bottom: connectionsBar.top
        anchors.right: parent.right
        anchors.left: parent.left
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ListView {
            id: orderList

            anchors.fill: parent
            anchors.topMargin: 0
            anchors.rightMargin: 8
            anchors.leftMargin: 8
            topMargin: 8
            clip: true
            spacing: 8

            model: ViewController.order_model

            delegate: Item {
                id: orderItem
                height: 50
                width: orderList.width

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
                    anchors.bottom: orderContentQty.bottom
                }

                //            RoundButton {
                //                icon.source: "qrc:/images/menu_icon.png"
                //                id: orderMenuButton
                //                width: 36
                //                height: 36
                //                anchors.right: orderCheckButton.left
                //                anchors.top: parent.top
                //                anchors.topMargin: 5
                //                padding: 8
                //                anchors.rightMargin: 0
                //                flat: true
                //            }
                CheckDelegate {
                    id: orderCheckButton
                    anchors.right: parent.right
                    anchors.top: parent.top
                    checked: model.object.checked
                    anchors.topMargin: 5
                    anchors.rightMargin: 8
                    padding: 8
                    width: 36
                    height: 36

                    onClicked: ViewController.order_model.check(
                                   model.object.name, checked)
                }

                Text {
                    id: orderID
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
                    id: orderDate
                    color: "#333333"
                    text: model.object.date
                    anchors.left: orderID.right
                    anchors.bottom: orderID.bottom
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                }

                Text {
                    id: orderContentItemText
                    color: "#333333"
                    text: "Item:"
                    anchors.left: parent.left
                    anchors.top: orderID.bottom
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Text {
                    id: orderContentItem
                    color: Material.accent
                    text: model.object.item_id
                    anchors.left: orderContentItemText.right
                    anchors.top: orderID.bottom
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 4
                    anchors.topMargin: 4
                }

                Text {
                    id: orderContentQtyText
                    color: "#333333"
                    text: "Num. Items:"
                    anchors.left: orderContentItem.right
                    anchors.top: orderID.bottom
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Text {
                    id: orderContentQty
                    color: "#333333"
                    text: model.object.num_items
                    anchors.left: orderContentQtyText.right
                    anchors.top: orderID.bottom
                    font.pixelSize: 14
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

