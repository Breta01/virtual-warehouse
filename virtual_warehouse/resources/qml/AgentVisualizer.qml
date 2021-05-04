import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

import 'qrc:/js/utils.js' as Utils

Canvas {
    id: agentView
    anchors.fill: parent
    visible: true

    property int num_agents: ViewController.agent_manager.num_agents
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

        var steps = ViewController.agent_manager.get_timestep(time)
        for (let i = 0; i < num_agents; i++) {
            ctx.beginPath();
            ctx.arc((steps[i][0] + 0.5) * params.coef + params.padding_x,
                    (steps[i][1] + 0.5) * params.coef + params.padding_y,
                    0.2 * params.coef, // Radius
                    0,
                    2 * Math.PI,
                    false);
            ctx.fillStyle = 'red';
            ctx.fill();
        }
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        width: parent.width
        height: 20
        z: 10
        color: "white"

        Timer {
            interval: 50
            running: true && slider.value <= slider.to
            repeat: true
            onTriggered: {
                time += 1
                agentView.requestPaint()
            }
        }

        Slider {
            id: slider
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            width: parent.width
            height: 10

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
    }

}
