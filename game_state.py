
class GameState:
    def __init__(self, app):
        self.redis = app.redis
        self.players = app.players
        app.game_state = self

    def get_active_player_id(self):
        return self.redis.get("active_player")

    def get_active_player(self):
        id = self.get_active_player_id()
        return self.players.get_by_id(id)

    def set_active_player_id(self, id):
        return self.redis.set("active_player", id)

    def current_players(self):
        active_players = []
        for player in self.redis.scan(0, "player:*")[1]:
            active_players.append(
                {"name": self.redis.get(player), "id": player.split(":")[1]})
        return active_players

    def next_player(self):
        players = self.current_players()
        active_player = self.get_active_player()

        print(f"Players: {players}")
        print(f"Active Player: {active_player}")

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
            return players[0]
        else:
            i = players.index(active_player)
            return players[0] if i == len(players)-1 else players[i+1]
