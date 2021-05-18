import QtQuick 2.0
import QtDataVisualization 1.3
import QtGraphicalEffects 1.12
import QtQuick.Controls 2.14
import QtQml.Models 2.2

Item {
    id: mapView3D
    width: contentView.width
    height: contentView.height
    anchors.top: window.top
    anchors.left: window.left
    visible: false

    property var selectedIdxs: []


    ColorGradient {
        id: surfaceGradient
        ColorGradientStop {
            position: 0.0
            color: "darkslategray"
        }
        ColorGradientStop {
            id: middleGradient
            position: 0.25
            color: "peru"
        }
        ColorGradientStop {
            position: 1.0
            color: "red"
        }
    }

    Surface3D {
        id: surfacePlot
        width: mapView3D.width
        height: mapView3D.height
        selectionMode: AbstractGraph3D.SelectionSlice
                       | AbstractGraph3D.SelectionItemAndRow
        scene.activeCamera.cameraPreset: Camera3D.CameraPresetIsometricLeft
        theme: Theme3D {
            type: Theme3D.ThemeStoneMoss
            font.family: "STCaiyun"
            font.pointSize: 35
            colorStyle: Theme3D.ColorStyleRangeGradient
            baseGradients: [surfaceGradient]
        }
        // TODO: Automatically set values
        axisX: ValueAxis3D {
            max: ViewController.map.max
            min: ViewController.map.min
        }
        // Y is up
        axisY: ValueAxis3D {
            max: ViewController.map.max
            min: ViewController.map.min
        }
        axisZ: ValueAxis3D {
            max: ViewController.map.max
            min: ViewController.map.min
            reversed: true
        }

        customItemList: []

        // TODO: add hover effect using inputHandler
        onSelectedElementChanged: {
            var selected_idxs = ViewController.get_selected()
            for (var i = 0; !splitView.controlKey && i < selected_idxs.length; i++) {
                var idx = selected_idxs[i]
                if (idx >= 0) {
                    surfacePlot.customItemList[idx].textureFile
                            = ":/textures/default.png"
                }
            }

            if (surfacePlot.selectedCustomItemIndex() !== -1) {
                let item = surfacePlot.selectedCustomItem()
                let idx = surfacePlot.selectedCustomItemIndex()
                item.textureFile = ":/textures/red.png"
                ViewController.select_map_location(idx, splitView.controlKey)
            }
        }
    }

    Connections {
        target: ViewController

        function onModelChanged() {
            surfacePlot.removeCustomItems()
            for (var row = 0; row < ViewController.model3D.rowCount(); row++) {
                var item = ViewController.model3D.get(row)
                var component = Qt.createComponent("qrc:/qml/CustomItem.qml")
                var instance = component.createObject(surfacePlot, {
                                                          "objectName": item.name,
                                                          "meshFile": item.mesh_file,
                                                          "position": Qt.vector3d(
                                                                          item.x,
                                                                          item.z,
                                                                          item.y)
                                                      })

                surfacePlot.addCustomItem(instance)
            }
        }

        function onItemSelected() {// TODO: select items based on 2D map
            for (var i = 0; !splitView.controlKey && i < selectedIdxs.length; i++) {
                var idx = selectedIdxs[i]
                if (idx >= 0) {
                    surfacePlot.customItemList[idx].textureFile
                            = ":/textures/default.png"
                }
            }

            selectedIdxs = ViewController.get_selected()
            for (var i = 0; !splitView.controlKey && i < selectedIdxs.length; i++) {
                var idx = selectedIdxs[i]
                if (idx >= 0) {
                    surfacePlot.customItemList[idx].textureFile
                            = ":/textures/red.png"
                }
            }
        }

        Component.onCompleted: onModelChanged()
    }
}
