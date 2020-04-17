import random


class Words:
    def __init__(self, redis):
        self.redis = redis

    def random_pair(self, difficulty="medium") -> str:
        """
        Returns a random pair of letters based on how frequently
        The letters appear in the english dictionary

        difficulty: 1 - 3, 1 being easiest, 3 most difficult
        str: two letter string
        """

        count = self.redis.zcard("letterpairs")
        step = count / 3
        difficulty_ranges = {
            "hard": (0, step),
            "medium": (step, step * 2),
            "easy": (step * 2, count)
        }

        rand = random.randrange(difficulty_ranges[difficulty][0], difficulty_ranges[difficulty][1])
        return self.redis.zrange("letterpairs", rand, rand)[0].decode("utf-8")

    def valid_word(self, word):
        return True if self.redis.sismember("words", word) == 1 else False
