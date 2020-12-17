import QtQuick 2.0

Canvas {
    id: mapView2D
    width: contentView.width
    height: contentView.height
    anchors.top: contentView.top
    anchors.left: contentView.left
    visible: true;

    // handler to override for drawing
    onPaint: {
        var ctx = getContext("2d");
        // background
        ctx.fillStyle = "#4d4d4f"
        ctx.fillRect(0, 0, width, height);

        // Drawing items
        var min_x = ViewController.map.min_x;
        var min_y = ViewController.map.min_y;
        var params = getDrawParams();
        var item, heat;

        // Draw selected item
        var idx = ViewController.get_selected_idx();
        if (idx >= 0) {
            item = ViewController.model.get(idx);
            ctx.fillStyle = "red";
            ctx.fillRect(
                        (item.x - min_x) * params.coef + params.padding_x,
                        (item.y - min_y) * params.coef + params.padding_y,
                        item.width * params.coef,
                        item.length * params.coef);
        }

        // TODO: speed up drawing - sort by z coordinate?
        // Draw Floor first
        for (var row = 0; row < ViewController.model.rowCount(); row++) {
            if (row == idx) {
                continue;
            }

            item = ViewController.model.get(row);

            if (item.type === "floor") {
                ctx.fillStyle = item.color;
                ctx.fillRect(
                            (item.x - min_x) * params.coef + params.padding_x,
                            (item.y - min_y) * params.coef + params.padding_y,
                            item.width * params.coef,
                            item.length * params.coef);
            }
        }

        // Draw rest of the items
        for (row = 0; row < ViewController.model.rowCount(); row++) {
            if (row == idx) {
                continue;
            }

            item = ViewController.model.get(row);

            if (item.type !== "floor") {
                ctx.fillStyle = item.color;
                if (true) { // is_heatmap() in future
                    if (item.type === "rack") {
                        heat = ViewController.model.get_heat(row);
                        var h = Math.floor((1.0 - heat) * 240);
                        ctx.fillStyle = "hsl(" + h + ", 100%, 50%)";

//                        var h = Math.floor(heat * 255);
//                        ctx.fillStyle = "rgb( 0," + h + "," + h + ")";
                    } else {
                        ctx.fillStyle = item.gray_color;
                    }
                }

                ctx.fillRect(
                            (item.x - min_x) * params.coef + params.padding_x,
                            (item.y - min_y) * params.coef + params.padding_y,
                            item.width * params.coef,
                            item.length * params.coef);
            }
        }
    }

    MouseArea {
        id: area
        anchors.fill: parent
        onPressed: {
            var min_x = ViewController.map.min_x;
            var min_y = ViewController.map.min_y;
            var params = getDrawParams();
            var x1, y1, x2, y2;

            for (var row = 0; row < ViewController.model.rowCount(); row++) {
                var item = ViewController.model.get(row);
                if (item.type === "rack") {
                    x1 = (item.x - min_x) * params.coef + params.padding_x;
                    y1 = (item.y - min_y) * params.coef + params.padding_y;
                    x2 = x1 + item.width * params.coef;
                    y2 = y1 + item.length * params.coef;
                    if (x1 <= mouseX && mouseX <= x2 &&
                            y1 <= mouseY && mouseY <= y2) {
                        ViewController.select_item(item.name, row);
                        // TODO: Speed up drawing - extra canvas, less items...
                        mapView2D.requestPaint()
                        return;
                    }
                }
            }

            ViewController.select_item(null, -1);
        }
    }

    Connections {
        target: ViewController
        function onModelChanged() {
            mapView2D.requestPaint();
        }
    }

    function getDrawParams() {
        // Get size coefficient and paddings
        var coef, padding_x = 20, padding_y = 20;

        var min_x = ViewController.map.min_x;
        var min_y = ViewController.map.min_y;

        var width = (ViewController.map.max_x - ViewController.map.min_x);
        var height = (ViewController.map.max_y - ViewController.map.min_y);

        var coef_x = (mapView2D.width - 2 * padding_x) / width;
        var coef_y = (mapView2D.height - 2 * padding_y) / height;

        if (coef_x < coef_y) {
            coef = coef_x;
            padding_y = (mapView2D.height - coef * height) / 2;
        } else {
            coef = coef_y;
            padding_x = (mapView2D.width - coef * width) / 2;
        }

        return {
            coef: coef,
            padding_x: padding_x,
            padding_y: padding_y,
        };
    }
}
