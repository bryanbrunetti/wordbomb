import random


class Words:
    def __init__(self, redis):
        self.redis = redis

    def random_pair(self, difficulty=2) -> str:
        """
        Returns a random pair of letters based on how frequently
        The letters appear in the english dictionary

        difficulty: 1 - 3, 1 being easiest, 3 most difficult
        str: two letter string
        """

        count = self.redis.zcard("letterpairs")
        low = count/3 * (3-difficulty)
        high = count/3 * difficulty
        rand = random.randrange(low, high)
        return self.redis.zrange("letterpairs", rand, rand)[0].decode("utf-8")

    def valid_word(self, word):
        return True if self.redis.sismember("words", word) == 1 else False