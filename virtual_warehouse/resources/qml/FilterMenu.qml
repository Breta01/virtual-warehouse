import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14


ToolBar {
    id: toolBar
    width: parent.width
    z: 30
    Material.elevation: 1

    property var model

    ToolButton {
        id: toolButton
        text: qsTr("All")
        anchors.left: parent.left
        checkable: true
        checked: model.filter === 0
        autoExclusive: true
        onClicked: model.filter = 0

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
        checked: model.filter === 1
        autoExclusive: true
        onClicked: model.filter = 1

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
        checked: model.filter === 2
        autoExclusive: true
        onClicked: model.filter = 2

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
        selectByMouse: true
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
        onTextChanged: model.search(text)

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
