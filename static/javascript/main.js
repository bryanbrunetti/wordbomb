$(document).ready(function() {
    var socket = io();
    socket.on('connect', function() {

    });
    socket.on('letterpair',function(data) { $("#letterpair").text(data['letterpair']); });
    socket.on("validWord", function(data) { $("#isValid").text(data['valid']) });
    socket.on("current_players", function(data) {
        console.log(data);
    });
    socket.on("time", function(data) {
        $("#countdown").text(data["time"]);
    });
    socket.on("gamestate", function(data) {
        console.log(data);
    });

    $(document).keypress(function(event) {
        if(event.key.length == 1 && event.key.match(/^[a-z]+$/i)) {
            key = event.key.toLowerCase();
            if(key == $("#letterpair").text()[0]) {
                console.log("first letter")
            }
        }
    });



    $("#getNewLetterpair").click(function() {
        socket.emit('getNewLetterPair');
    });
    $("#startGame").click(function() {
        socket.emit("startGame")
    });

    $("#submitGuess").click(function() {
        socket.emit("validWord", {word: $("#guess").val()});
    });

    window.setInterval(function() { socket.emit('keepalive');}, 10000);
}
);