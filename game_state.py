
class GameState:
    def __init__(self, app):
        self.redis = app.redis
        self.players = app.players
        self.words = app.words

        app.game_state = self

    def all_players(self):
        waiting = []
        for player in self.redis.scan(0, "player:*")[1]:
            player_data = {"name": self.redis.get(player), "id": player.split(":")[1]}
            if self.game_in_progress():
                player_data.update(self.get_player_state(player_data))
            waiting.append(player_data)
        return waiting

    # Active player is whose turn it currently is
    def get_active_player_id(self):
        return self.redis.get("active_player")

    def get_active_player(self):
        id = self.get_active_player_id()
        return self.players.get_by_id(id)

    def set_active_player_id(self, id):
        active_id = self.redis.set("active_player", id)
        self.redis.expire("active_player", 20)
        return active_id

    def current_players(self):
        active_players = []
        for player_id,player_state in self.player_states().items():
            active_players.append({"id": player_id, "name": player_state["name"]})
        return active_players

    def start_new_game(self):
        for player in self.all_players():
            self.add_new_player(player)
            self.refresh_game()

    def remove_player_id(self, player_id):
        self.redis.hdel("player_state", player_id)
        self.refresh_game()

    def add_new_player(self, player):
        self.redis.hset("player_state", player["id"], f"name:{player['name']},lives:2,score:0")
        self.refresh_game()

    def refresh_game(self):
        self.redis.expire("player_state", 60)

    def remove_life(self, player):
        player_state = self.get_player_state(player)
        if player_state:
            player_state["lives"] = int(player_state["lives"]) - 1
            self.set_player_state(player, player_state)
            self.refresh_game()
        return player_state["lives"]

    def set_player_state(self, player, state):
        self.redis.hset("player_state", player["id"], f"name:{player['name']},lives:{state['lives']},score:{state['score']}")
        self.refresh_game()

    def get_player_state(self,player):
        player_details = self.redis.hget("player_state", player["id"])
        if player_details:
            return dict(item.split(":") for item in player_details.split(","))
        else:
            return dict()

    def current_letterpair(self):
        return self.redis.get("current_letterpair")

    def set_current_letterpair(self, letterpair):
        self.redis.set("current_letterpair", letterpair)
        self.redis.expire("current_letterpair", 20)

    def next_letterpair(self):
        letterpair = self.words.random_pair("easy")
        self.set_current_letterpair(letterpair)
        return letterpair

    def valid_word(self, word):
        letterpair = self.current_letterpair()
        val = self.words.valid_word(word)
        if self.words.valid_word(word) and letterpair in word:
            return True
        else:
            return False
    
    def player_states(self):
        player_states = dict()
        for player_id,state in self.redis.hgetall("player_state").items():
            player_states[player_id] = dict(item.split(":") for item in state.split(","))
        return player_states
    
    def player_state(self, player):
        if self.game_in_progress():
            state_values = self.redis.hget("player_state", player["id"])
            return dict(item.split(":") for item in state_values.split(","))

    def player_add_points(self, player, points):
        if self.game_in_progress():
            player_values = self.player_state(player)
            player_values["score"] = int(player_values["score"]) + points
            self.set_player_state(player,player_values)
            return player_values["score"]


    def game_in_progress(self):
        return True if self.redis.hlen("player_state") else False

    def end_game(self):
        return self.redis.hdel("player_state")

    def next_player(self):
        players = self.current_players()
        active_player = self.get_active_player()

        # No players? return None
        if not len(players):
            return None
        # Playing alone? return the only player
        if len(players) == 1:
            return players[0]

        # Turn order will be based on the id they were assigned
        players = sorted(players, key=lambda item: item["id"])

        # No active player? first player to join goes first
        if not active_player:
            self.set_active_player_id(players[0]["id"])
            return players[0]
        else:
            i = players.index(active_player)

            if i == len(players)-1:
                self.set_active_player_id(players[0]["id"])
                return players[0]
            else:
                self.set_active_player_id(players[i+1]["id"])
                return players[i+1]
