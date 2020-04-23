class LeaderBoard:
    def __init__(self, app):
        self.redis = app.redis
        self.words = app.words

    def top(self,count=10):
        return_values = []
        rank = 1
        for player in self.redis.zrevrange("leaderboard", 0, count, withscores=True):
            return_values.append((rank, player[0], int(player[1])))
            rank+=1
        return return_values

    def add_player(self, player, score):
        self.redis.zadd("leaderboard", {f"{player['name']}": score })
        self.redis.zremrangebyrank("leaderboard", 0, -10)