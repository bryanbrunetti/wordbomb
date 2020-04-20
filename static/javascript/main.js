$(document).ready(function () {
    var socket = io();

    socket.on("playerid", function(data) {
        localStorage.setItem("playerId", data.id)
    })
    socket.on('newGameStarted', function () {
        $("#startGame").hide()
    })
    socket.on('newLetterPair', function (data) {
        $("#letterpair").text(data['letterpair']);
    });
    socket.on("validWord", function (isValid) {
        if(isValid) {
            $("#guessWord").css("color", "green")
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

    socket.on("time", function (data) {
        $("#progressbar").progressbar({value: data["time"]*10});
        $("#progressbar .progress-label").text(data["time"]);
    });

    socket.on("nextPlayer", function(player) {
        $("#guessWord").empty();
        localStorage.setItem("currentPlayerId", player.id)
        $(".player").each(function(i,playerDiv) {
            if(playerDiv.id.split(":")[1] == player.id) {
                $(playerDiv).css("border", "1px solid black")
            } else {
                $(playerDiv).css("border", "none")
            }
        })
    })
    socket.on("playerJoined", function (data) {
        refreshPlayers(data)
    });
    socket.on("playerLeft", function (data) {
        refreshPlayers(data)
    })

    function refreshPlayers(data) {
        $("#players").empty();
        for (let player of data.players) {
            $("#players").append("<div class='player' id='player:" + player.id + "'>" + player.name + "</div>")
        }
    }
    $(document).on("keydown", function(event) {
        if(localStorage.getItem("playerId") != localStorage.getItem("currentPlayerId")) {
            return;
        }
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
    })

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