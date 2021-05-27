import Qt.labs.platform 1.1
import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Material 2.14
import QtQuick.Dialogs 1.3
import QtQml 2.2

Item {

    function openHelpDialog() {
        helpDialog.open()
    }

    function openSettingsDialog() {
        settingsDialog.open()
    }

    function openImportFileDialog() {
        importFileDialog.open()
    }

    function openImportAgentsDialog() {
        importAgentsDialog.open()
    }

    function openSaveFileDialog() {
        saveFileDialog.open()
    }

    function openCreateClassDialog() {
        classDialogTextArea.text = ""
        classNameField.text = ""
        cErrorText.text = ""
        createClassDialog.open()
    }

    function openCreateQueryDialog(name="", cls="", query="") {
        queryNameField.text = name
        queryDialogTextArea.text = query
        let idx = queryComboBox.find(cls)
        queryComboBox.currentIndex = (idx === -1) ? queryComboBox.currentIndex : idx
        qErrorText.text = ""
        createQueryDialog.open()
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
                text: "Version: " + versionNumber
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

    Dialog {
        id: settingsDialog
        title: "Settings"
        standardButtons: StandardButton.Close

        contentItem: Rectangle {
            implicitWidth: 600
            implicitHeight: 200
            color: "#eee"

            Text {
                id: sTitle
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 8
                font.capitalization: Font.AllUppercase
                font.pointSize: 10
                color: "#333"
                text: "Java Settings"
            }

            Text {
                id: sText
                anchors.top: sTitle.bottom
                anchors.left: parent.left
                anchors.margins: 8
                text: "Java executable:"
            }

            TextField {
                id: javaExec
                selectByMouse: true
                anchors.left: sText.right
                anchors.right: parent.right
                anchors.baseline: sText.baseline
                anchors.margins: 8
                anchors.rightMargin: 32
                text: ""
                placeholderText: "Java path (e.g. C:\\Program Files\\Java\\jdk1.8.0\\bin\\java.exe)"
                font.pixelSize: 12

                onTextChanged: ViewController.onto_manager.java = text

                Component.onCompleted: text = ViewController.onto_manager.java
            }

            Rectangle {
                radius: 8
                height: 16
                width: 16
                anchors.bottom: sText.baseline
                anchors.left: javaExec.right
                color: ViewController.onto_manager.java_correct ? Material.accent : "red"

                Text {
                    id: sTextCheck
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.margins: 8
                    text: ViewController.onto_manager.java_correct ? "✔️" : "✕"
                    color: "white"
                }
            }

            DialogButtonBox {
                position: DialogButtonBox.Footer

                anchors.bottom: parent.bottom
                width: parent.width
                standardButtons: DialogButtonBox.Close

                onRejected: settingsDialog.close()
            }
        }
    }

    FileDialog {
        id: saveFileDialog
        modality: Qt.WindowModal
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        selectExisting: false
        nameFilters: ["RDF/XML format (*.rdf)"]
        onAccepted: ViewController.save_ontology(saveFileDialog.fileUrl)
    }

    FileDialog {
        id: importAgentsDialog
        modality: Qt.WindowModal
        title: "Please select a file with picker agents description"
        nameFilters: ["CSV file (*.csv)"]
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: {
            ViewController.agent_manager.load_data(importAgentsDialog.fileUrl)
        }
    }

    FileDialog {
        id: importFileDialog
        modality: Qt.WindowModal
        title: "Please select a warehouse file"
        // nameFilters: ["Excel file (*.xls *.xlsx)", "CSV file (*.csv)"]
        nameFilters: ["Excel file (*.xls *.xlsx)"]
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

        property var fileUrl: ""
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
            implicitHeight: 460
            implicitWidth: 500
            color: "#eee"


            Rectangle {
                id: header
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 85
                z: 10

                Text {
                    id: fileUrlTitle
                    text: "Opening file:"
                    anchors.left: parent.left
                    anchors.baseline: fileUrlText.baseline
                    anchors.baselineOffset: 1
                    anchors.margins: 8
                }

                TextField {
                    id: fileUrlText
                    selectByMouse: true
                    anchors.left: fileUrlTitle.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 8
                    anchors.rightMargin: 32
                    text: importFileDialog.fileUrl.toString()
                    font.pixelSize: 12
                    readOnly: true
                    activeFocusOnPress: false

                    MouseArea {
                        anchors.fill: parent
                        onClicked: importFileDialog.open()
                    }
                }

                Text {
                    id: dialogHeader
                    text: "Select types of sheets:"
                    anchors.left: parent.left
                    anchors.top: fileUrlText.bottom
                    anchors.margins: 8
                }
            }

            ScrollView {
                anchors.top: header.bottom
                anchors.bottom: dialogButtons.top
                anchors.right: parent.right
                anchors.left: parent.left
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                ListView {
                    id: sheetsTypesList
                    model: fileImportSheetsModel

                    property var mModel: model

                    anchors.fill: parent
                    anchors.margins:  16
                    anchors.bottomMargin: 4
                    anchors.topMargin: 4

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


    Dialog {
        id: createClassDialog
        title: "Create Class"
        standardButtons: StandardButton.Cancle | StandardButton.Ok

        contentItem: Rectangle {
            implicitWidth: 500
            implicitHeight: 400
            color: "#eee"

            Text {
                id: nameClassText
                anchors.left: parent.left
                anchors.baseline: classNameField.baseline
                anchors.margins: 8
                text: "Name:"
            }

            TextField {
                id: classNameField
                selectByMouse: true
                anchors.left: nameClassText.right
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 8
                placeholderText: "NameOfNewClass"
                text: ""
            }

            Text {
                id: baseClassText
                anchors.left: parent.left
                anchors.verticalCenter: classComboBox.verticalCenter
                anchors.margins: 8
                text: "Base class:"
            }

            ComboBox {
                id: classComboBox
                anchors.left: baseClassText.right
                anchors.top: classNameField.bottom
                anchors.margins: 8
                textRole: "type"

                model: ListModel {
                    ListElement { type: "RackLocation" }
                    ListElement { type: "Item" }
                    ListElement { type: "Order" }
                }
            }

            TextArea {
                id: classDialogTextArea
                selectByMouse: true
                anchors.top: classComboBox.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: cErrorText.top
                anchors.margins: 4
                wrapMode: Text.Wrap
                padding: 8
                placeholderText: "Conditions..."
                text: qsTr("")

                background: Rectangle {
                    color: "white"
                }
            }

            Text {
                id: cErrorText
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: classDialogButtons.top
                padding: 8
                height: (text === "") ? 0 : 50
                Behavior on height {
                    NumberAnimation {}
                }
                font.pixelSize: 12
                wrapMode: Text.Wrap
                text: ""
                color: "red"
            }

            DialogButtonBox {
                id: classDialogButtons
                position: DialogButtonBox.Footer

                anchors.bottom: parent.bottom
                width: parent.width
                standardButtons: DialogButtonBox.Close | DialogButtonBox.Save

                onRejected: {
                    createClassDialog.close()
                }
                onAccepted: {
                    cErrorText.text = ""
                    cErrorText.text = ViewController.onto_manager.check_create_class(
                                classNameField.text,
                                classComboBox.currentText,
                                classDialogTextArea.text)

                    if (cErrorText.text === "") {
                        ViewController.onto_manager.create_class(
                                    classNameField.text,
                                    classComboBox.currentText,
                                    classDialogTextArea.text)
                        createClassDialog.close()
                    }
                }
            }
        }
    }


    Dialog {
        id: createQueryDialog
        title: "Create SPARQL Query"
        standardButtons: StandardButton.Cancle | StandardButton.Ok

        contentItem: Rectangle {
            implicitWidth: 500
            implicitHeight: 400
            color: "#eee"

            LoadingOverlay {
                progressValue: ViewController.onto_manager.progress_value
            }

            Text {
                id: nameQueryText
                anchors.left: parent.left
                anchors.baseline: queryNameField.baseline
                anchors.margins: 8
                text: "Name:"
            }

            TextField {
                id: queryNameField
                selectByMouse: true
                anchors.left: nameQueryText.right
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 8
                placeholderText: "Name of query"
                text: ""
            }

            Text {
                id: baseQueryText
                anchors.left: parent.left
                anchors.verticalCenter: queryComboBox.verticalCenter
                anchors.margins: 8
                text: "Base class:"
            }

            ComboBox {
                id: queryComboBox
                anchors.left: baseQueryText.right
                anchors.top: queryNameField.bottom
                anchors.margins: 8
                textRole: "type"

                model: ListModel {
                    ListElement { type: "RackLocation" }
                    ListElement { type: "Item" }
                    ListElement { type: "Order" }
                }
            }

            TextArea {
                id: queryDialogStartTextArea
                anchors.top: queryComboBox.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 4
                wrapMode: Text.Wrap
                readOnly: true
                padding: 8
                text: "PREFIX : <http://warehouse/onto.owl#>\n" +
                      "SELECT DISTINCT ?obj WHERE {"

                background: Rectangle {
                    color: "white"
                }
            }

            ScrollView {
                id: view
                clip: true
                anchors.top: queryDialogStartTextArea.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: queryDialogEndTextArea.top
                anchors.topMargin: 1
                anchors.bottomMargin: 1
                anchors.margins: 4

                TextArea {
                    id: queryDialogTextArea
                    selectByMouse: true

                    wrapMode: Text.Wrap
                    padding: 8
                    leftPadding: 16
                    placeholderText: "SPARQL Query..."
                    text: qsTr("")

                    background: Rectangle {
                        color: "white"
                    }
                }
            }

            TextArea {
                id: queryDialogEndTextArea
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: qErrorText.top
                anchors.margins: 4
                wrapMode: Text.Wrap
                readOnly: true
                padding: 8
                text: "  ?obj a :" + queryComboBox.currentText + " .\n}"

                background: Rectangle {
                    color: "white"
                }
            }


            Text {
                id: qErrorText
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: queryDialogButtons.top
                padding: 8
                height: (text === "") ? 0 : 50
                Behavior on height {
                    NumberAnimation {}
                }
                font.pixelSize: 12
                wrapMode: Text.Wrap
                text: ""
                color: "red"
            }

            DialogButtonBox {
                id: queryDialogButtons
                position: DialogButtonBox.Footer

                anchors.bottom: parent.bottom
                width: parent.width
                standardButtons: DialogButtonBox.Close | DialogButtonBox.Save

                onRejected: createQueryDialog.close()
                onAccepted: {
                    qErrorText.text = ""
                    qErrorText.text = ViewController.onto_manager.check_create_query(
                                queryNameField.text,
                                queryComboBox.currentText,
                                queryDialogTextArea.text)
                    if (qErrorText.text === "") {
                        ViewController.onto_manager.create_query(
                                    queryNameField.text,
                                    queryComboBox.currentText,
                                    queryDialogTextArea.text)
                        createQueryDialog.close()
                    }
                }
            }
        }
    }
}




/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
