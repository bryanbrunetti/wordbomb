from redis import Redis

r = Redis()
words = open("words_alpha.txt").readlines()
doublet_list = dict()

print(f"Found {len(words)} words, clearing existing entries ...")
r.delete("words")
r.delete("letterpairs")
count = 0


for word in words:
    word = word.rstrip()
    if len(word) >= 2:
        r.sadd("words", word)
        for i,j in enumerate(word):
            doublet = word[i:i+2]
            if len(doublet) == 2:
                doublet_list.setdefault(doublet, 0)
                doublet_list[doublet] += 1

for pair,freq in doublet_list.items():
    r.zadd("letterpairs", {pair: freq})