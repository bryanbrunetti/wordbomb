import random

class Words:
    def __init__(self, app):
        self.redis = app.redis
        app.words = self

    def random_pair(self, difficulty="medium"):
        """
        Returns a random pair of letters based on how frequently
        The letters appear in the english dictionary

        difficulty: string of either 'easy', 'medium' or 'hard'
        str: two letter string
        """

        count = self.redis.zcard("letterpairs")
        step = int(count / 3)
        difficulty_ranges = {
            "hard": (0, step),
            "medium": (step, step * 2),
            "easy": (step * 2, count)
        }

        rand = random.randrange(difficulty_ranges[difficulty][0], difficulty_ranges[difficulty][1])
        return self.redis.zrange("letterpairs", rand, rand)[0]

    def valid_word(self, word):
        return True if self.redis.sismember("words", word) else False
    
    def points_for(self, letterpair, word=None):
        total_pairs = self.redis.zcard("letterpairs")
        letterpair_rank = self.redis.zrank("letterpairs", letterpair)
        return total_pairs - letterpair_rank

