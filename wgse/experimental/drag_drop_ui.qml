import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

Window {
    width: 400
    height: 300
    visible: true
    title: "WGSE-NG"


    Rectangle {
        id: dropArea
        anchors.centerIn: parent
        width: 200
        height: 100
        border.color: "#967E76" 
        border.width: 2

        Text {
            id: "center"
            anchors.centerIn: parent
            text: "Drag and drop a file here"
            color: "#527163" 
        }

        DropArea {           
            onEntered: dropArea.border.color = "#283845"
            onExited: dropArea.border.color = "#E8DDCB" 
            anchors.fill: parent
            onDropped: {
                //center.text = drop.urls[0].split("/")[1]; 
                console.log("File Dropped:", drop.urls);
            }
        }
    }
}
