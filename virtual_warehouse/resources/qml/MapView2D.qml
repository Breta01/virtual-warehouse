import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14

import 'qrc:/js/utils.js' as Utils

Canvas {
    id: mapView2D
    anchors.fill: parent
    visible: true

    property var max_heat: 1
    readonly property var sidebar_max: (ViewController.model2D.level === -1) ? ViewController.sideview_model.max_heat : max_heat

    AgentVisualizer {
        z: 10

    }

    // handler to override for drawing
    onPaint: {
        if (!ViewController.is2D()) {
            return
        }

        var ctx = getContext("2d")
        // background
        ctx.fillStyle = "#4d4d4f"
        ctx.fillRect(0, 0, width, height)

        // Drawing items
        var min_x = ViewController.map.min_x
        var min_y = ViewController.map.min_y
        var params = Utils.getDrawParams(mapView2D.height, mapView2D.width, ViewController)
        var item, heat, max = 1
        var heats = []

        // Draw Floor first
        for (var row = 0; row < ViewController.model2D.rowCount(); row++) {
            item = ViewController.model2D.get(row)

            if (item.type === "floor") {
                ctx.fillStyle = item.color
                ctx.fillRect((item.x - min_x) * params.coef + params.padding_x,
                             (item.y - min_y) * params.coef + params.padding_y,
                             item.width * params.coef,
                             item.length * params.coef)
            } else if (item.type === "rack") {
                heats[row] = ViewController.model2D.get_heat(row)
                max = Math.max(heats[row], max)
            }
        }

        // Set global max_heat property
        max_heat = max
        var is_heatmap = ViewController.is_heatmap

        for (row = 0; row < ViewController.model2D.rowCount(); row++) {
            item = ViewController.model2D.get(row)

            if (item.type !== "floor") {
                ctx.fillStyle = item.color
                if (is_heatmap) {
                    // is_heatmap() in future
                    if (item.type === "rack") {
                        heat = get_heat_color(heats[row], max)
                        ctx.fillStyle = heat
                    } else {
                        ctx.fillStyle = item.gray_color
                    }
                }

                ctx.fillRect((item.x - min_x) * params.coef + params.padding_x,
                             (item.y - min_y) * params.coef + params.padding_y,
                             item.width * params.coef,
                             item.length * params.coef)
            }
        }

        // Draw selected item
        var selected_idxs = ViewController.get_selected()
        for (var i = 0; i < selected_idxs.length; i++) {
            var idx = selected_idxs[i]
            if (idx >= 0) {
                item = ViewController.model2D.get(idx)
                ctx.beginPath()
                ctx.lineWidth = "3"
                ctx.strokeStyle = "red"
                ctx.rect((item.x - min_x) * params.coef + params.padding_x,
                         (item.y - min_y) * params.coef + params.padding_y,
                         item.width * params.coef, item.length * params.coef)
                ctx.stroke()
            }
        }
    }

    Rectangle {
        id: sideView
        visible: (sideViewList.count) ? true : false
        height: Math.min(parent.height * 0.6, 400)
        width: 120
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: 20
        anchors.leftMargin: 20
        color: "white"
        radius: 5

        Rectangle {
            id: svTitleBackground
            color: Material.primary
            anchors.top: parent.top
            anchors.topMargin: -3
            width: parent.width + 1
            height: svTitle.height + 10
            radius: parent.radius

            Rectangle {
                color: svTitleBackground.color
                height: svTitleBackground.radius
                anchors.left: svTitleBackground.left
                anchors.right: svTitleBackground.right
                anchors.bottom: svTitleBackground.bottom
            }

            Text {
                id: svTitle
                text: "Side View"
                color: "white"
                font.bold: true
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        ListView {
            id: sideViewList
            anchors.top: svTitleBackground.bottom
            anchors.topMargin: 10
            anchors.bottom: parent.bottom
            width: 70
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 1

            model: ViewController.sideview_model

            delegate: Item {
                id: sideViewItem
                height: Math.floor(
                            sideViewList.height / (sideViewList.count + 1))
                width: 70

                Rectangle {
                    id: sideViewRect
                    color: get_heat_color(model.object.heat, sidebar_max)
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    anchors.leftMargin: 0
                    anchors.left: parent.left
                    width: 40
                    height: parent.height
                }

                Rectangle {
                    id: sideViewLine
                    height: 1
                    width: 20
                    color: get_heat_color(model.object.heat, sidebar_max)

                    anchors.bottom: sideViewRect.bottom
                    anchors.left: sideViewRect.right
                }

                Text {
                    id: sideViewItemHeight
                    text: model.object.z
                    anchors.left: sideViewLine.right
                    anchors.bottom: sideViewLine.bottom
                    horizontalAlignment: Text.AlignLeft
                    anchors.bottomMargin: -4
                    anchors.leftMargin: 4
                    font.pixelSize: 12
                    color: get_heat_color(model.object.heat, sidebar_max)
                }
            }
        }
    }

    Rectangle {
        radius: 5
        border.width: 0

        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: -5
        Behavior on height {
            NumberAnimation {}
        }
        height: (levelSwitch.checked ? 200 : 20) + 80
        width: levelSlider.width + 40
        visible: ViewController.is_heatmap && ViewController.is2D
        z: 10

        Rectangle {
            id: titleBackground
            color: Material.primary
            anchors.top: parent.top
            anchors.topMargin: -3
            width: parent.width + 1
            height: levelTitle.height + levelSwitch.height
            radius: parent.radius

            Rectangle {
                color: titleBackground.color
                height: titleBackground.radius
                anchors.left: titleBackground.left
                anchors.right: titleBackground.right
                anchors.bottom: titleBackground.bottom
            }

            Text {
                id: levelTitle
                text: "Levels"
                color: "white"
                font.bold: true
                visible: levelSlider.visible
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 4
            }

            Switch {
                id: levelSwitch
                padding: 0
                scale: 0.65
                display: AbstractButton.IconOnly
                checked: false
                anchors.top: levelTitle.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                z: 1

                onClicked: {
                    if (checked) {
                        ViewController.model2D.level = levelSlider.value
                    } else {
                        ViewController.model2D.level = -1
                    }
                    mapView2D.requestPaint()
                }
            }
        }

        Text {
            id: levelIndication
            color: Material.accent

            visible: levelSlider.visible
            anchors.top: titleBackground.bottom
            anchors.topMargin: 4
            anchors.horizontalCenter: levelSlider.horizontalCenter
            text: (levelSwitch.checked) ? Number(levelSlider.value).toString(
                                              ) : "All"
        }

        Slider {
            id: levelSlider
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            Behavior on height {
                NumberAnimation {}
            }
            height: levelSwitch.checked ? 200 : 20

            visible: ViewController.is_heatmap && ViewController.is2D
            enabled: levelSwitch.checked

            live: true
            Material.theme: Material.Light
            orientation: Qt.Vertical
            snapMode: Slider.SnapAlways
            // Only model3D correctly set max Z coordinate right now
            to: ViewController.model3D.max_level
            from: 0
            value: -1
            stepSize: 1

            onMoved: {
                if (levelSwitch.checked) {
                    ViewController.model2D.level = value
                    mapView2D.requestPaint()
                    // Update sideview max value after redraw
                    ViewController.sideview_model.update()
                }
            }
        }
    }

    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        onPressed: {
            var min_x = ViewController.map.min_x
            var min_y = ViewController.map.min_y
            var params = Utils.getDrawParams(mapView2D.height, mapView2D.width, ViewController)
            var x1, y1, x2, y2

            for (var row = 0; row < ViewController.model2D.rowCount(); row++) {
                var item = ViewController.model2D.get(row)
                if (item.type === "rack") {
                    x1 = (item.x - min_x) * params.coef + params.padding_x
                    y1 = (item.y - min_y) * params.coef + params.padding_y
                    x2 = x1 + item.width * params.coef
                    y2 = y1 + item.length * params.coef
                    if (x1 <= mouseX && mouseX <= x2 && y1 <= mouseY
                            && mouseY <= y2) {

                        // Holding CTRL - adding location
                        ViewController.select_map_location(
                                    row, mouse.modifiers & Qt.ControlModifier)
                        // TODO: Speed up drawing - extra canvas, less items...
                        // mapView2D.requestPaint()
                        return
                    }
                }
            }
            // If CTRL is active, nothing happens
            if (!(mouse.modifiers & Qt.ControlModifier)) {
                ViewController.select_map_location(-1, false)
            }
        }

        onPositionChanged: {
            var min_x = ViewController.map.min_x
            var min_y = ViewController.map.min_y
            var params = Utils.getDrawParams(mapView2D.height, mapView2D.width, ViewController)
            var x1, y1, x2, y2

            for (var row = 0; row < ViewController.model2D.rowCount(); row++) {
                var item = ViewController.model2D.get(row)
                if (item.type === "rack") {
                    x1 = (item.x - min_x) * params.coef + params.padding_x
                    y1 = (item.y - min_y) * params.coef + params.padding_y
                    x2 = x1 + item.width * params.coef
                    y2 = y1 + item.length * params.coef
                    if (x1 <= mouseX && mouseX <= x2 && y1 <= mouseY
                            && mouseY <= y2) {
                        ViewController.hover_item(row)
                        return
                    }
                }
            }
            ViewController.hover_item(-1)
        }
    }

    Connections {
        target: ViewController
        function onModelChanged() {
            mapView2D.requestPaint()
        }
        function onDrawModeChanged() {
            mapView2D.requestPaint()
            // Update sideview max value after redraw
            ViewController.sideview_model.update()
        }
        function onItemSelected() {
            mapView2D.requestPaint()
        }
    }

    property var colors: ["#440154", "#440255", "#440357", "#450558", "#45065A",
        "#45085B", "#46095C", "#460B5E", "#460C5F", "#460E61", "#470F62", "#471163",
        "#471265", "#471466", "#471567", "#471669", "#47186A", "#48196B", "#481A6C",
        "#481C6E", "#481D6F", "#481E70", "#482071", "#482172", "#482273", "#482374",
        "#472575", "#472676", "#472777", "#472878", "#472A79", "#472B7A", "#472C7B",
        "#462D7C", "#462F7C", "#46307D", "#46317E", "#45327F", "#45347F", "#453580",
        "#453681", "#443781", "#443982", "#433A83", "#433B83", "#433C84", "#423D84",
        "#423E85", "#424085", "#414186", "#414286", "#404387", "#404487", "#3F4587",
        "#3F4788", "#3E4888", "#3E4989", "#3D4A89", "#3D4B89", "#3D4C89", "#3C4D8A",
        "#3C4E8A", "#3B508A", "#3B518A", "#3A528B", "#3A538B", "#39548B", "#39558B",
        "#38568B", "#38578C", "#37588C", "#37598C", "#365A8C", "#365B8C", "#355C8C",
        "#355D8C", "#345E8D", "#345F8D", "#33608D", "#33618D", "#32628D", "#32638D",
        "#31648D", "#31658D", "#31668D", "#30678D", "#30688D", "#2F698D", "#2F6A8D",
        "#2E6B8E", "#2E6C8E", "#2E6D8E", "#2D6E8E", "#2D6F8E", "#2C708E", "#2C718E",
        "#2C728E", "#2B738E", "#2B748E", "#2A758E", "#2A768E", "#2A778E", "#29788E",
        "#29798E", "#287A8E", "#287A8E", "#287B8E", "#277C8E", "#277D8E", "#277E8E",
        "#267F8E", "#26808E", "#26818E", "#25828E", "#25838D", "#24848D", "#24858D",
        "#24868D", "#23878D", "#23888D", "#23898D", "#22898D", "#228A8D", "#228B8D",
        "#218C8D", "#218D8C", "#218E8C", "#208F8C", "#20908C", "#20918C", "#1F928C",
        "#1F938B", "#1F948B", "#1F958B", "#1F968B", "#1E978A", "#1E988A", "#1E998A",
        "#1E998A", "#1E9A89", "#1E9B89", "#1E9C89", "#1E9D88", "#1E9E88", "#1E9F88",
        "#1EA087", "#1FA187", "#1FA286", "#1FA386", "#20A485", "#20A585", "#21A685",
        "#21A784", "#22A784", "#23A883", "#23A982", "#24AA82", "#25AB81", "#26AC81",
        "#27AD80", "#28AE7F", "#29AF7F", "#2AB07E", "#2BB17D", "#2CB17D", "#2EB27C",
        "#2FB37B", "#30B47A", "#32B57A", "#33B679", "#35B778", "#36B877", "#38B976",
        "#39B976", "#3BBA75", "#3DBB74", "#3EBC73", "#40BD72", "#42BE71", "#44BE70",
        "#45BF6F", "#47C06E", "#49C16D", "#4BC26C", "#4DC26B", "#4FC369", "#51C468",
        "#53C567", "#55C666", "#57C665", "#59C764", "#5BC862", "#5EC961", "#60C960",
        "#62CA5F", "#64CB5D", "#67CC5C", "#69CC5B", "#6BCD59", "#6DCE58", "#70CE56",
        "#72CF55", "#74D054", "#77D052", "#79D151", "#7CD24F", "#7ED24E", "#81D34C",
        "#83D34B", "#86D449", "#88D547", "#8BD546", "#8DD644", "#90D643", "#92D741",
        "#95D73F", "#97D83E", "#9AD83C", "#9DD93A", "#9FD938", "#A2DA37", "#A5DA35",
        "#A7DB33", "#AADB32", "#ADDC30", "#AFDC2E", "#B2DD2C", "#B5DD2B", "#B7DD29",
        "#BADE27", "#BDDE26", "#BFDF24", "#C2DF22", "#C5DF21", "#C7E01F", "#CAE01E",
        "#CDE01D", "#CFE11C", "#D2E11B", "#D4E11A", "#D7E219", "#DAE218", "#DCE218",
        "#DFE318", "#E1E318", "#E4E318", "#E7E419", "#E9E419", "#ECE41A", "#EEE51B",
        "#F1E51C", "#F3E51E", "#F6E61F", "#F8E621", "#FAE622", "#FDE724"]

    function get_heat_color(heat, max) {
        // Use value from predefined colors
        return colors[Math.min(255, Math.round((heat / Math.max(1, max)) * 255))]
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.01}
}
##^##*/

