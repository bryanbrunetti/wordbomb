import time


class Players:
    keepalive_seconds = 30

    def __init__(self, app):
        self.redis = app.redis
        app.players = self

    def get_next_id(self):
        return self.redis.incr("player_ids")

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def name(self, name):
        return "Guest" + str(time.time()) if not name else name

    def add(self, player):
        if self.redis.set(f"player:{player['id']}", player["name"]):
            return self.keepalive(player)

    def get_by_id(self, id):
        if id is None:
            return None
        name = self.redis.get(f"player:{id}")
        return {"id": id, "name": name} if name else None

    def remove(self, player):
        return self.redis.delete(f"player:{player['id']}")

    def keepalive(self, player):
        result = self.redis.expire(
            f"player:{player['id']}", self.keepalive_seconds)
        print(f"Keepalive result: {result}")
        return self.redis.expire(f"player:{player['id']}", self.keepalive_seconds)
