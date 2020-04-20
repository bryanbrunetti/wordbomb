$(document).ready(function () {
    var socket = io();
    socket.on('newGameStarted', function () {
        $("#startGame").hide()
    })❤
    socket.on('newLetterPair', function (data) {
        $("#letterpair").text(data['letterpair']);
    });
    socket.on("validWord", function (isValid) {
        if(isValid) {
            $("#guessWord").css("font-color", "green")
        } else {
            $("#guessWord").effect("shake")
        }
    });

    socket.on("guessUpdate", function (data) {
        $("#guessWord").text(data.guess)
    })
    socket.on("wrong", function () {
        $("#letterpair").effect("shake")
        $("#guessWord").effect("shake")
    })
    socket.on("current_players", function (data) {
        console.log(data);
    });
    socket.on("time", function (data) {
        $("#progressbar").progressbar({value: data["time"]*10});
        $("#progressbar .progress-label").text(data["time"]);
    });
    socket.on("gamestate", function (data) {
        console.log(data);
    });
    socket.on("nextPlayer", function(player) {
        $("#guessWord").empty();
        $(".player").each(function(i,playerDiv) {
            if(playerDiv.id.split(":")[1] == player.id) {
                console.log(player)
                $(playerDiv).css("border", "1px solid black")
            } else {
                $(playerDiv).css("border", "none")
            }
        })
    })
    socket.on("playerJoined", function (data) {
        $("#players").empty();
        for (let player of data.players) {
            $("#players").append("<div class='player' id='player:" + player.id + "'>" + player.name + "</div>")
        }
    });
    socket.on("playerLeft", function (data) {
        $("#players").empty();
        for (let player of data.players) {
            $("#players").append("<div class='player' id='player:" + player.id + "'>" + player.name + "</div>")
        }
    })

    $(document).keypress(function (event) {
        if (event.key.length == 1 && event.key.match(/^[a-z]+$/i)) {
            key = event.key.toLowerCase();
            $("#guessWord").append(key);
            socket.emit("guessUpdate", $("#guessWord").text())
        } else if (event.keyCode == 8) {
            $("#guessWord").text($("#guessWord").text().slice(0, -1))
            socket.emit("guessUpdate", $("#guessWord").text())
        } else if (event.keyCode == 13) {
            socket.emit("validWord", $("#guessWord").text())
        }
    });



    $("#getNewLetterpair").click(function () {
        socket.emit('getNewLetterPair');
    });
    $("#startGame").click(function () {
        socket.emit("startGame")
    });

    $("#submitGuess").click(function () {
        socket.emit("validWord", { word: $("#guess").val() });
    });

    window.setInterval(function () { socket.emit('keepalive'); }, 10000);
}
);