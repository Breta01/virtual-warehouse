import QtQuick 2.0


ListView {
   id: locationList
   anchors.fill: locationTab
   topMargin: 8
   clip: true
   anchors.topMargin: 0
   spacing: 8
   anchors.rightMargin: 8
   anchors.leftMargin: 8


   model: ViewController.location_model

   delegate: Item {
       id: locationItem
       height: 200
       width: locationList.width

       Rectangle {
           id: rectangle
           x: 0
           y: 0
           anchors.fill: parent
           color: "#f1f1f1"
           border.color: "#f1f1f1"
       }

       Text {
           id: locationID
           x: 0
           y: 0
           width: 284
           height: 33
           text: location.name
           horizontalAlignment: Text.AlignLeft
           font.pixelSize: 12
           font.bold: true
       }

       Text {
           id: locationClass
           x: 0
           y: 39
           width: 150
           height: 37
           text: model.location.class_str
           font.pixelSize: 12
           horizontalAlignment: Text.AlignLeft
       }


       Text {
           id: locationSubclass
           x: 67
           y: 39
           width: 150
           height: 37
           text: ""
           font.pixelSize: 12
           horizontalAlignment: Text.AlignLeft
       }

       Text {
           id: locationDimenstion
           x: 0
           y: 74
           width: 150
           height: 52
           text: model.location.dimension_str
           font.pixelSize: 12
           horizontalAlignment: Text.AlignLeft
       }

       Text {
           id: locationMaxweight
           x: 116
           y: 74
           width: 117
           height: 32
           text: model.location.max_weight
           font.pixelSize: 12
           horizontalAlignment: Text.AlignLeft
       }

       Text {
           id: locationZone
           x: 0
           y: 103
           width: 150
           height: 50
           text: model.location.zone
           font.pixelSize: 12
           horizontalAlignment: Text.AlignLeft
       }

   }
}
