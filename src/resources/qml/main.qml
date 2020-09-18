import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtDataVisualization 1.0
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.3

import VirtualWarehouse 1.0


ApplicationWindow {
    id: window
    title: qsTr("Virtual Warehouse")
    width: 1000
    height: 600
    visible: true

    menuBar: MenuBar {
        id: menuBar
        Menu {
            title: qsTr("&File")

            MenuItem {
                text: qsTr("&Open")
                onTriggered: openDialog.open()
            }
            MenuItem {
                text: qsTr("&Save As...")
            }
            MenuItem {
                text: qsTr("&Quit")
                onTriggered: Qt.quit()
            }
        }

        Menu {
            title: qsTr("&Edit")

            MenuItem {
                text: qsTr("&Copy")
            }
            MenuItem {
                text: qsTr("Cu&t")
            }
            MenuItem {
                text: qsTr("&Paste")
            }
        }

        Menu {
            title: qsTr("&Options")

            MenuItem {
                text: qsTr("&Help")
            }
            MenuItem {
                text: qsTr("&Settings")
            }
        }
    }

    Column {
        id: contentView
        x: 0
        y: 0
        width: window.width - sidebar.width
        height: window.height

        Item {
            id: surfaceView
            width: contentView.width
            height: contentView.height
            anchors.top: window.top
            anchors.left: window.left

            ColorGradient {
                id: surfaceGradient
                ColorGradientStop { position: 0.0; color: "darkslategray" }
                ColorGradientStop { id: middleGradient; position: 0.25; color: "peru" }
                ColorGradientStop { position: 1.0; color: "red" }
            }

//            ViewController {
//                id: surfacePlot


            Surface3D {
                id: surfacePlot
                objectName: "surfacePlot"
                width: surfaceView.width
                height: surfaceView.height
                theme: Theme3D {
                    type: Theme3D.ThemeStoneMoss
                    font.family: "STCaiyun"
                    font.pointSize: 35
                    colorStyle: Theme3D.ColorStyleRangeGradient
                    baseGradients: [surfaceGradient]
                }


            /*
            Surface3D {
                id: surfacePlot
                width: surfaceView.width
                height: surfaceView.height
                theme: Theme3D {
                    type: Theme3D.ThemeStoneMoss
                    font.family: "STCaiyun"
                    font.pointSize: 35
                    colorStyle: Theme3D.ColorStyleRangeGradient
                    baseGradients: [surfaceGradient]
                }
                shadowQuality: AbstractGraph3D.ShadowQualityMedium
                selectionMode: AbstractGraph3D.SelectionSlice | AbstractGraph3D.SelectionItemAndRow

                scene.activeCamera.cameraPreset: Camera3D.CameraPresetIsometricLeft
                axisY.min: 0.0
                axisY.max: 500.0
                axisX.segmentCount: 10
                axisX.subSegmentCount: 2
                axisX.labelFormat: "%i"
                axisZ.segmentCount: 10
                axisZ.subSegmentCount: 2
                axisZ.labelFormat: "%i"
                axisY.segmentCount: 5
                axisY.subSegmentCount: 2
                axisY.labelFormat: "%i"
                axisY.title: "Height"
                axisX.title: "Latitude"
                axisZ.title: "Longitude"
*/
            }
        }
    }

    Column {
        id: sidebar
        x: contentView.width
        y: 0
        width: 300
        height: window.height


        TabBar {
            id: tabBar
            y: 0
            width: sidebar.width

            TabButton {
                id: tabButton
                text: qsTr("Locations")
            }

            TabButton {
                id: tabButton1
                text: qsTr("Items")
            }

            TabButton {
                id: tabButton2
                text: qsTr("Orders")
            }

        }

        StackLayout {
            y: tabBar.height
            width: parent.width
            currentIndex: tabBar.currentIndex
            Item {
                id: locationTab

                Text {
                    id: element
                    width: 164
                    height: 94
                    text: qsTr("locationTab")
                    horizontalAlignment: Text.AlignLeft
                    font.pixelSize: 20
                    padding: 10
                }
            }
            Item {
                id: itemTab

                Text {
                    id: elementx
                    width: 164
                    height: 94
                    text: qsTr("Item Tab")
                    font.pixelSize: 20
                    padding: 10
                }
            }
            Item {
                id: orderTab

                Text {
                    id: elementy
                    width: 164
                    height: 94
                    text: qsTr("Order Tab")
                    font.pixelSize: 20
                    padding: 10
                }
            }
        }
    }

    FileDialog {
         id: openDialog
         title: "Please select a warehouse file"
         nameFilters: ["Excel file (*.xls)", "CSV file (*.csv)"]
         folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
         onAccepted: document.load(file)
     }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.5}
}
##^##*/
