
class GameState:
    def __init__(self, app):
        self.redis = app.redis
        self.players = app.players
        self.words = app.words
        app.game_state = self

    def get_active_player_id(self):
        return self.redis.get("active_player")

    def get_active_player(self):
        id = self.get_active_player_id()
        return self.players.get_by_id(id)

    def set_active_player_id(self, id):
        self.redis.expire("active_player", 20)
        return self.redis.set("active_player", id)

    def current_players(self):
        active_players = []
        for player in self.redis.scan(0, "player:*")[1]:
            active_players.append(
                {"name": self.redis.get(player), "id": player.split(":")[1]})
        return active_players
    
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
