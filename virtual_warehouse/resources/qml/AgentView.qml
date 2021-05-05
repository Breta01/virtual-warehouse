import QtQuick 2.0
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

Item {
    anchors.fill: parent


    ScrollView {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ListView {
            id: agentList

            anchors.fill: parent
            anchors.topMargin: 0
            anchors.rightMargin: 8
            anchors.leftMargin: 8
            topMargin: 8
            bottomMargin: 8
            clip: true
            spacing: 8

            model: ViewController.agent_manager.agent_list

            delegate: Item {
                id: agentItem
                width: agentList.width
                height: 52

                Rectangle {
                    id: rectangle
                    color: "#eeeeee"
                    anchors.fill: parent
                }

                Rectangle {
                    id: colorPoint
                    color: model.modelData["color"]
                    height: 10
                    width: 10
                    radius: 5
                    anchors.left: parent.left
                    anchors.verticalCenter: name.verticalCenter
                    anchors.margins: 8
                }

                Text {
                    id: name
                    text: "Agent " + model.modelData["name"]
                    anchors.left: colorPoint.right
                    anchors.top: parent.top
                    horizontalAlignment: Text.AlignLeft
                    anchors.topMargin: 8
                    anchors.leftMargin: 8
                    font.pixelSize: 14
                    font.bold: true
                }

                CheckDelegate {
                    id: itemCheckButton
                    anchors.right: parent.right
                    anchors.top: parent.top
                    checked: model.modelData["checked"]
                    anchors.topMargin: 5
                    anchors.rightMargin: 8
                    padding: 8
                    width: 36
                    height: 36

                    onClicked: ViewController.agent_manager.toggle_agent(model.modelData["name"], checked)
                }

                Text {
                    id: stepCountText
                    color: "#666"
                    text: qsTr("Step count:")
                    anchors.left: parent.left
                    anchors.top: name.bottom
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                }

                Text {
                    id: stepCount
                    color: Material.accent
                    text: model.modelData["steps"]
                    anchors.left: stepCountText.right
                    anchors.top: name.bottom
                    horizontalAlignment: Text.AlignLeft
                    anchors.leftMargin: 4
                    anchors.topMargin: 4
                }
            }
        }
    }
}
