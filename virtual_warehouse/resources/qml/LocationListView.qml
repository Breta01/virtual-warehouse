import QtQuick 2.4
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: locationTab

    ToolBar {
        id: toolBar
        width: parent.width

        ToolButton {
            id: toolButton
            text: qsTr("All")
            anchors.left: parent.left
            checkable: true
            checked: true
            autoExclusive: true
            onClicked: ViewController.location_model.filter = 0

            contentItem: Text {
                color: Qt.darker("#ffffff", parent.enabled && parent.checked ? 1.5 : 1.0)
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                text: parent.text
                font: parent.font
            }
        }

        ToolButton {
            id: toolButton1
            text: qsTr("Checked")
            anchors.left: toolButton.right
            checkable: true
            autoExclusive: true
            onClicked: ViewController.location_model.filter = 1

            contentItem: Text {
                color: Qt.darker("#ffffff", parent.enabled && parent.checked ? 1.5 : 1.0)
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                text: parent.text
                font: parent.font
            }
        }

        ToolButton {
            id: toolButton2
            text: qsTr("Unchecked")
            anchors.left: toolButton1.right
            checkable: true
            autoExclusive: true
            onClicked: ViewController.location_model.filter = 2

            contentItem: Text {
                color: Qt.darker("#ffffff", parent.enabled && parent.checked ? 1.5 : 1.0)
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                text: parent.text
                font: parent.font
            }
        }

        TextField {
            id: searchText
            opacity: searchButton.checked ? 1 : 0;
            Behavior on opacity { NumberAnimation{} }
            visible: opacity ? true : false
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: searchButton.left
            topPadding: 15
            padding: 9
            anchors.left: parent.left
            height: parent.height
            placeholderText: qsTr("Search text...")

            property bool ignoreTextChange: false
            onTextChanged: ViewController.location_model.search(text)

            Material.foreground: "black"
            background: Rectangle {
               implicitWidth: 200
               implicitHeight: parent.height
               color: searchText.focus ? "white" : "lightgray"
            }
        }

        ToolButton {
            id: searchButton
            icon.source: checked ? "qrc:/images/close_icon.png" : "qrc:/images/search_icon.png"
            icon.height: 20
            icon.color: "white"
            anchors.right: parent.right
            antialiasing: true
            display: AbstractButton.IconOnly
            checkable: true
            autoExclusive: false

            onClicked: searchText.text = ""
        }
    }

    ListView {
       id: locationList
       anchors.top: toolBar.bottom
       anchors.bottom: parent.bottom
       width: parent.width
       topMargin: 8
       clip: true
       anchors.topMargin: 0
       spacing: 8
       anchors.rightMargin: 8
       anchors.leftMargin: 8


       model: ViewController.location_model

       delegate: Item {
           id: locationItem
           width: locationList.width
           height: 100

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
               anchors.bottom: locationZone.bottom
           }

           RoundButton {
               icon.source: "qrc:/images/menu_icon.png"
               id: roundButton
               width: 36
               height: 36
               anchors.right: locationCheckButton.left
               anchors.top: parent.top
               anchors.topMargin: 5
               padding: 8
               anchors.rightMargin: 0
               flat: true
           }

           CheckDelegate {
               id: locationCheckButton
               anchors.right: parent.right
               anchors.top: parent.top
               checked: model.object.checked
               anchors.topMargin: 5
               anchors.rightMargin: 8
               padding: 8
               width: 36
               height: 36

               onClicked: {
                   ViewController.location_model.check(model.object.name, checked)
               }
           }

           /*
           RoundButton {
               icon.source: "qrc:/images/close_icon.png"
               id: locationCloseButton
               width: 36
               height: 36
               anchors.right: parent.right
               anchors.top: parent.top
               anchors.topMargin: 5
               padding: 8
               anchors.rightMargin: 8
               flat: true
           }*/

           Text {
               id: locationID
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
               id: locationClass
               color: "#333333"
               text: model.object.class_str
               anchors.left: parent.left
               anchors.top: locationID.bottom
               font.pixelSize: 11
               horizontalAlignment: Text.AlignLeft
               anchors.leftMargin: 8
               anchors.topMargin: 4
           }

           Rectangle {
               id: locationUnderline
               x: 0
               anchors.top: locationClass.bottom
               anchors.topMargin: 4
               height: 1
               color: Material.accent
               width: parent.width
           }

           Image {
               id: locationDimensionIcon
               source: "qrc:/images/dimension_icon.png"
               smooth: true
               sourceSize.height: 19
               sourceSize.width: 19
               height: locationDimension.height + 5
               width: locationDimension.height + 5
               anchors.left: parent.left
               anchors.top: locationUnderline.bottom
               anchors.leftMargin: 8
               anchors.topMargin: 8
           }

           Text {
               id: locationDimension
               anchors.left: locationDimensionIcon.right
               anchors.leftMargin: 4
               text: model.object.dimension_str
               anchors.verticalCenter: locationDimensionIcon.verticalCenter
               font.pixelSize: 12
               horizontalAlignment: Text.AlignLeft
           }

           Image {
               id: locationMaxweightIcon
               source: "qrc:/images/max_weight_icon.png"
               anchors.horizontalCenterOffset: 8
               anchors.horizontalCenter: parent.horizontalCenter
               smooth: true
               sourceSize.height: 19
               sourceSize.width: 19
               height: locationMaxweight.height + 5
               width: locationMaxweight.height + 5
               anchors.top: locationUnderline.bottom
               anchors.topMargin: 8
           }

           Text {
               id: locationMaxweight
               anchors.left: locationMaxweightIcon.right
               anchors.leftMargin: 4
               text: model.object.max_weight
               anchors.verticalCenter: locationMaxweightIcon.verticalCenter
               font.pixelSize: 12
               horizontalAlignment: Text.AlignLeft
           }

           Text {
               id: locationZoneIcon
               color: "#333333"
               anchors.left: parent.left
               anchors.top: locationDimension.bottom
               anchors.leftMargin: 8
               anchors.topMargin: 8
               text: "Zone:"
               font.pixelSize: 12
               horizontalAlignment: Text.AlignLeft
           }

           Text {
               id: locationZone
               anchors.left: locationZoneIcon.right
               anchors.top: locationDimension.bottom
               anchors.leftMargin: 4
               anchors.topMargin: 8
               text: model.object.zone
               font.pixelSize: 12
               horizontalAlignment: Text.AlignLeft
           }

       }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
