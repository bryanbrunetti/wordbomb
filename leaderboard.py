class LeaderBoard:
    keep_top = 10
    def __init__(self, app):
        self.redis = app.redis
        self.words = app.words

    def rankings(self):
        return_values = []
        rank = 1
        for player in self.redis.zrevrange("leaderboard", 0, self.keep_top, withscores=True):
            return_values.append((rank, player[0], int(player[1])))
            rank+=1
        return return_values

    def add_player(self, player, score):
        high_score = self.redis.zscore("leaderboard", player["name"]) or 0
        if int(score) > int(high_score):
            self.redis.zadd("leaderboard", {f"{player['name']}": score })
            self.redis.zremrangebyrank("leaderboard", 0, self.keep_top*-1)