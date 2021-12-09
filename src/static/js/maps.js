function createAdjMatrix(n) {
    var result = new Array(n);
    for (var i = 0; i < n; i++) {
    	result[i] = new Array(n - 1);
    }

    return result;
}

function createInfoDetail(name, nameArr, throughput) {

    // Need to include throughput details

    var image = name == "Control Hub" ? "</b> <img src='../static/images/hub.jpg' />" :
        "</b> <img src='../static/images/gateway.jpg'/>"

    var tableHeader = 
    `<table id="info-window">
        <tr id="info-header">
            <td>
                Communication
            </td>
            <td>
                Throughput
            </td>
        </tr>
    `

    var tableInfo = "";

    var tableFooter = "</table>";

    if (throughput != null) {
        // Parse the information into HTML format
        for (var i = 0; i < throughput.length; i++) {
            var currVal = throughput[i];

            if (currVal != undefined) {
                tableInfo += ("<tr><td>" + nameArr[i]  + "</td><td>" + currVal + "</td></tr>");
            }
        }
    }

    return "<b>" + name + image + "<br><br>" + tableHeader + tableInfo + tableFooter;
}


// Alter the animation speed of the symbol
function animateSymbol(line, isReport) {
    var count = 0;
    var offsetVal = 1;
    window.setInterval(() => {
        if (Boolean(isReport)) {
            count = (count + 1) % 200;
        } else {
            count += offsetVal;
            if (count > 200) {
                offsetVal = -1;
            } else if (count < 0) {
                offsetVal = 1;
            }
        }
        var icons = line.get('icons');
        icons[0].offset = (count / 2) + '%';
        line.set('icons', icons);
    }, 20);
}