import QtQuick 2.0
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {

    property var progressValue

    id: loadingOverlay
    anchors.fill: parent
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
            value: progressValue
            indeterminate: (value == 0)
            Behavior on value {
                NumberAnimation {}
            }
        }
    }
}
