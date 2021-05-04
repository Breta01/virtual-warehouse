.pragma library

function getDrawParams(mapHeight, mapWidth, ViewController) {
    // Get size coefficient and paddings
    var coef, padding_x = 20, padding_y = 20

    var min_x = ViewController.map.min_x
    var min_y = ViewController.map.min_y

    var width = (ViewController.map.max_x - min_x)
    var height = (ViewController.map.max_y - min_y)

    var coef_x = (mapWidth - 2 * padding_x) / width
    var coef_y = (mapHeight - 2 * padding_y) / height

    if (coef_x < coef_y) {
        coef = coef_x
        padding_y = (mapHeight - coef * height) / 2
    } else {
        coef = coef_y
        padding_x = (mapWidth - coef * width) / 2
    }

    return {
        "coef": coef,
        "padding_x": padding_x,
        "padding_y": padding_y
    }
}
