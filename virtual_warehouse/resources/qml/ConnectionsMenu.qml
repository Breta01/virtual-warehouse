import QtQuick 2.0
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

ToolBar {
    id: connectionsBar
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 0
    width: parent.width

    Material.background: "white"
    Material.foreground: Material.BlueGrey
    Material.elevation: 0

    property bool isLocation: false
    property string dst1
    property int    idx1
    property var    fun1
    property var    mdl1

    property string dst2
    property int    idx2
    property var    fun2
    property var    mdl2

    property var toolBarModel


    ToolButton {
        id: toolButton
        text: qsTr("Related:")
        anchors.left: parent.left
        anchors.leftMargin: 8
        enabled: false
    }

    ToolButton {
        id: toolButton1
        text: dst1
        anchors.left: toolButton.right

        onClicked: {
            tabBar.currentIndex = idx1
            fun1()
            mdl1.filter = 1
        }
    }

    ToolButton {
        id: toolButton2
        text: dst2
        anchors.left: toolButton1.right

        onClicked: {
            tabBar.currentIndex = idx2
            fun2()
            mdl2.filter = 1
        }
    }

    CheckDelegate {
        id: mainCheckButton
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        tristate: true
        checkState: toolBarModel.check_state
        anchors.rightMargin: 16
        padding: 8
        width: 36
        height: 36

        onClicked: {
            var st  = toolBarModel.check_state !== 2
            toolBarModel.check_all(st)

            if (isLocation) {
                ViewController.select_all(st)
            }
        }
    }
}
