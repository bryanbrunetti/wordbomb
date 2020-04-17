$(document).ready(function() {
    var socket = io();
    socket.on('connect', function() {
//        socket.emit('connected', {data: 'I\'m connected!'});
    });
    socket.on('letterpair',function(data) {
        $("#letterpair").val(data['letterpair']);
    });

    socket.on("validWord", function(data) {
        console.log("valid word: " + data['valid']);
        $("#isValid").text(data['valid'])

    });

    $("#getNewLetterpair").click(function() {
        socket.emit('getNewLetterPair');
    });
    $("#submitGuess").click(function() {
        socket.emit("validWord", {word: $("#guess").val()});
    });
}
);