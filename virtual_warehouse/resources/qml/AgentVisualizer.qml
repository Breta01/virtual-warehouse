import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

import 'qrc:/js/utils.js' as Utils

Canvas {
    id: agentView
    anchors.fill: parent
    visible: ViewController.agent_manager.active

    property int time: 0

    // handler to override for drawing
    onPaint: {
        if (!ViewController.is2D()) {
            return
        }

        var ctx = getContext("2d")
        // background
        ctx.clearRect(0, 0, width, height)

        // Drawing items
        var min_x = ViewController.map.min_x
        var min_y = ViewController.map.min_y
        var params = Utils.getDrawParams(agentView.height, agentView.width, ViewController)
        var item, heat, max = 1
        var heats = []

        var colors = ViewController.agent_manager.get_colors()
        var steps = ViewController.agent_manager.get_timestep(time)
        for (let i = 0; i < steps.length; i++) {
            ctx.beginPath();
            ctx.arc((steps[i][0] + 0.5) * params.coef + params.padding_x,
                    (steps[i][1] + 0.5) * params.coef + params.padding_y,
                    0.25 * params.coef, // Radius
                    0,
                    2 * Math.PI,
                    false);
            ctx.fillStyle = colors[i];
            ctx.fill();

            if (steps[i][2]) {
                ctx.beginPath();
                ctx.arc((steps[i][0] + 0.5) * params.coef + params.padding_x,
                        (steps[i][1] + 0.5) * params.coef + params.padding_y,
                        0.25 * params.coef, // Radius
                        0,
                        2 * Math.PI,
                        false);
                ctx.strokeStyle = "black";
                ctx.stroke();
            }
        }
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.bottom
        width: parent.width
        height: (ViewController.agent_manager.active) ? 40 : 0
        z: 10
        color: "white"

        Button {
            id: playButton
            anchors.left: parent.left
            anchors.margins: 4
            anchors.verticalCenter: parent.verticalCenter
            bottomPadding: 16
            text: (checked) ? qsTr("❚❚") : qsTr("▶")
            implicitHeight: 45
            implicitWidth: 40
            highlighted: true
            flat: true
            checkable: true
            display: AbstractButton.TextBesideIcon
        }

        Timer {
            interval: 50
            running: playButton.checked && slider.value <= slider.to
            repeat: true
            onTriggered: {
                time += 1
                agentView.requestPaint()
            }
        }

        Slider {
            id: slider
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: playButton.right
            anchors.right: parent.right
            anchors.margins: 8

            visible: true
            enabled: true

            Material.theme: Material.Light
            orientation: Qt.Horizontal
            snapMode: Slider.SnapAlways
            to: ViewController.agent_manager.max_time
            from: 0
            value: time
            stepSize: 1

            onMoved: {
                time = value
                agentView.requestPaint()
            }
        }
    }

    Connections {
        target: ViewController
        function onModelChanged() {
            agentView.requestPaint()
        }
    }

    Connections {
        target: ViewController.agent_manager
        function onAgentsChanged() {
            agentView.requestPaint()
        }

        function onActiveAgentsChanged() {
            agentView.requestPaint()
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
