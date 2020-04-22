$(document).ready(function () {
    var socket = io();

    socket.on("welcome", function(data) {
        $("#players").empty();
        localStorage.setItem("playerId", data.player.id)
        for(let player of data.gameState.currentPlayers) {
            if($("#player"+player.id).length) {
                $("#player"+player.id).css("opacity", "1.0")
            } else {
                addPlayerElem(player);
            }
        }

        if(data.gameState.gameInProgress) {
            $("#startGame").hide()
            $("#timerBox").show()
            if(data.gameState.activePlayer) {
                localStorage.setItem("currentPlayerId", data.gameState.activePlayer.id)
                playerElement = $("#player" + data.gameState.activePlayer.id)
                setActivePlayerElem(playerElement)
                $("#timerBox").detach().appendTo(playerElement)
            }
            if(data.gameState.letterPair) { $("#letterpair").text(data.gameState.letterPair) }
        } else {
            $("#letterpair").hide()
            $("#startGame").show()
            $("#timerBox").hide()
        }
    })

    socket.on('newGameStarted', function () {
        $("#startGame").hide()
        $("#timerBox").show()
        $("#letterpair").show()
        $("#guessWordContainer").show()
        $(".player .playerName").css("text-decoration", "none")
        $(".lives").html(heartTemplate() + heartTemplate())
        $(".score").html(0)
    })
    
    socket.on('newLetterPair', function (data) {
        $("#letterpair").text(data['letterpair']);
        stopAnimateCSS("#letterpair")
        stopAnimateCSS("#guessWord")
    });

    socket.on("validWord", function (isValid) {
        if(isValid) {
            // animateCSS("#guessWord", "tada")
            // animateCSS("#letterpair", "tada")
        } else {
            animateCSS("#guessWord", "shake")
        }
    });

    socket.on("guessUpdate", function (data) {
        $("#guessWord").text(data.guess)
    })
    socket.on("wrong", function () {
        animateCSS("#letterpair", "wobble")
        animateCSS("#guessWord", "wobble")
    })

    socket.on("time", function (data) {
        $("#timer").css("width", data["time"] * 10 + "%").attr("aria-valuenow", data["time"]).text(data["time"]);
    });

    socket.on("disconnect", function(data) {
        // alert("Lost Connection");
    })

    socket.on("nextPlayer", function(player) {
        $("#guessWord").empty();
        localStorage.setItem("currentPlayerId", player.id)
        $(".player").each(function(i,playerDiv) {
            if($(playerDiv).data("playerid") == player.id) {
                $("#timerBox").detach().appendTo($(playerDiv))
                setActivePlayerElem($(playerDiv));
            } else {
                $(playerDiv).css("border", "none")
            }
        })
    })
    socket.on("playerJoined", function (player) {
        if(player.id != localStorage.getItem("playerId")) {
            if($("#player"+player.id).length == 0) {
                addPlayerElem(player);
            } else {
                $("#player"+player.id).css("opacity", "1.0")
            }
            
        }
    });

    socket.on("playerLeft", function (player) {
        $(".player").each(function(i,playerDiv) {
            if($(playerDiv).data("playerid") == player.id) {
                $(playerDiv).css("opacity","0.3")
            }
        })
    });

    socket.on("playerLost", function(player) {
        $("#player" + player.id + " .playerName").css("text-decoration","line-through")
    });

    socket.on("gameOver", function(){
        $("#letterpair").hide()
        // $("#timerBox").hide()
        // $("#guessWordContainer").hide()
        $("#startGame").show()
    });

    socket.on("playerScore", function(data) {
        animateCSS("#player"+data.player.id + " .score", "tada")
        $("#player"+data.player.id + " .score").text(data.score)
    });

    socket.on("playerLifeChange", function(data) {
        setPlayerLives(data.player.id,data.lives);
    })

    function setPlayerLives(player_id, lives) {
        current_lives = $("#player"+player_id+" .life").length
        if(current_lives > lives) {
            for(i=current_lives;i>lives;i--) {
                animateCSS("#player"+player_id+" .life", "rotateOut", i-1, true)
            }
        } else {
            for(i=lives;i<current_lives;i++) {
                $("#player"+player_id+" .lives").append(heartTemplate());
                animateCSS("#player"+player_id+" .life", "tada", i-1);
            }
        }

    }

    function setActivePlayerElem(playerDiv) {
        $(playerDiv).css("border", "1px solid black")
    }

    function addPlayerElem(player) {
        $("#players").append('<div class="player row" data-playerid="'+player.id+'" id="player'+player.id+'"><div class="playerName col-md-1">'+player.name+'</div><div class="lives col-md-1">' + heartTemplate() + '' + heartTemplate() + '</div><div class="col-md-1">score:</div><div class="score col-md-1">0</div></div>')
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

function heartTemplate() {
    return '<svg class="bi bi-heart-fill life text-danger" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z" clip-rule="evenodd"/></svg>';
}
function cssAnimate(target, name) {
    target.removeClass().addClass(name + ' animated').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
      $(this).removeClass();
    });
  };

  function animateCSS(element, animationName, index=0, remove=false) {
    const node = document.querySelectorAll(element)[index]
    node.classList.add('animated', animationName)

    function handleAnimationEnd() {
        node.classList.remove('animated', animationName)
        node.removeEventListener('animationend', handleAnimationEnd)
        if(remove) { node.remove() }
    }
    node.addEventListener('animationend', handleAnimationEnd)
};

function stopAnimateCSS(element) {
    const node = document.querySelector(element)
    node.classList.remove('animated', 'wobble')
    node.classList.remove('animated', 'pulse')
}
