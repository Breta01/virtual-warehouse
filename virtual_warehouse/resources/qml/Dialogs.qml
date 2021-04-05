import Qt.labs.platform 1.1
import QtQuick 2.0
import QtQuick.Controls 2.14
import QtQuick.Dialogs 1.3
import QtQml 2.2

Item {

    function openHelpDialog() {
        helpDialog.open()
    }

    function openImportFileDialog() {
        importFileDialog.open()
    }

    Dialog {
        id: helpDialog
        title: "Help"
        standardButtons: StandardButton.Close

        contentItem: Rectangle {
            implicitWidth: 500
            implicitHeight: 200
            color: "#eee"

            Image {
                id: imageLogo
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 8
                source: "qrc:/images/icon.png"
                sourceSize.height: 32
                sourceSize.width: 32
            }

            Text {
                id: title
                anchors.bottom: imageLogo.bottom
                anchors.left: imageLogo.right
                anchors.leftMargin: 8
                font.pointSize: 16
                text: "Virtual Warehouse"
            }

            Text {
                id: version
                anchors.top: imageLogo.bottom
                anchors.left: parent.left
                anchors.margins: 8
                text: "Version: " + ViewController.version
            }

            Text {
                id: textDoc
                anchors.top: version.bottom
                anchors.left: parent.left
                anchors.margins: 8
                text: "For more information look into:"
            }

            Text {
                anchors.top: textDoc.bottom
                anchors.left: parent.left
                anchors.leftMargin: 8
                onLinkActivated: Qt.openUrlExternally(
                                     "https://virtual-warehouse.readthedocs.io")
                text: "<a href='https://virtual-warehouse.readthedocs.io'>Documentation (virtual-warehouse.readthedocs.io)</a>"
            }

            DialogButtonBox {
                position: DialogButtonBox.Footer

                anchors.bottom: parent.bottom
                width: parent.width
                standardButtons: DialogButtonBox.Close

                onRejected: helpDialog.close()
            }
        }
    }

    FileDialog {
        id: importFileDialog
        modality: Qt.WindowModal
        title: "Please select a warehouse file"
        nameFilters: ["Excel file (*.xls *.xlsx)", "CSV file (*.csv)"]
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: {
            fileImportSettings.open()
            fileImportSettings.fileUrl = importFileDialog.fileUrl
            fileImportSheetsModel.clear()
            var sheets = ViewController.get_sheets(fileUrl)
            for (var i = 0; i < sheets.length; ++i) {
                fileImportSheetsModel.append({
                                                 "index": i,
                                                 "name": sheets[i][0],
                                                 "type": sheets[i][1]
                                             })
            }
        }
    }

    Dialog {
        id: fileImportSettings
        title: "File Import Settings"
        standardButtons: StandardButton.Open | StandardButton.Cancel

        property var fileUrl
        height: 200
        width: 300

        onAccepted: {
            var types = []
            for (var i = 0; i < sheetsTypesList.model.count; ++i) {
                var o = sheetsTypesList.model.get(i)
                types.push({
                               "name": o.name,
                               "type": o.type
                           })
            }

            ViewController.load(fileUrl, types)
            fileImportSettings.close()
        }

        contentItem: Rectangle {
            id: rectangle
            anchors.fill: parent
            implicitHeight: 400
            implicitWidth: 500
            color: "#eee"

            Text {
                id: dialogHeader
                text: "Select types of individual sheets:"
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: 8
            }

            ListView {
                id: sheetsTypesList
                model: fileImportSheetsModel

                property var mModel: model

                anchors.top: dialogHeader.bottom
                anchors.bottom: dialogButtons.top
                anchors.right: parent.right
                anchors.left: parent.left
                anchors.margins: 16

                delegate: Item {
                    id: sheetItem
                    height: 50
                    width: sheetsTypesList.width

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: comboBox.verticalCenter
                        text: model.name
                    }

                    function updateType(typeIndex) {
                        fileImportSheetsModel.setProperty(model.index, "type",
                                                          typeIndex)
                    }

                    function getType() { return model.type }

                    ComboBox {
                        id: comboBox
                        anchors.right: parent.right
                        textRole: "type"
                        Component.onCompleted: currentIndex = indexOfValue(getType())
                        onActivated: {
                            // Prevent (ComboBox) model and (ListView) model name collision
                            updateType(currentText)
                        }

                        model: sheetsTypesModel
                    }
                }
            }

            ListModel {
                id: fileImportSheetsModel
            }

            ListModel {
                id: sheetsTypesModel
                ListElement { type: "None" }
                ListElement { type: "Coordinates" }
                ListElement { type: "Inventory" }
                ListElement { type: "Items" }
                ListElement { type: "Locations" }
                ListElement { type: "Orders" }
            }

            DialogButtonBox {
                id: dialogButtons
                position: DialogButtonBox.Footer

                anchors.bottom: parent.bottom
                width: parent.width
                standardButtons: DialogButtonBox.Open | DialogButtonBox.Cancel

                onAccepted: fileImportSettings.accepted()
                onRejected: fileImportSettings.close()
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/

