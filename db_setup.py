from redis import Redis

r = Redis()
words = open("words_alpha.txt").readlines()
bigram_list = dict()

r.delete("words")
r.delete("letterpairs")
print(f"Processing {len(words)} words ", end='', flush=True)

count = 1
checkpoint = int(len(words) / 10)

for word in words:
    if not checkpoint % count:
        print(".", end='', flush=True)
    count += 1
    word = word.rstrip().lower()
    if len(word) >= 2:
        r.sadd("words", word)
        for i, j in enumerate(word):
            bigram = word[i:i + 2]
            if len(bigram) == 2:
                bigram_list.setdefault(bigram, 0)
                bigram_list[bigram] += 1

print(f"Processing {len(bigram_list)} bigrams ", end="", flush=True)
count = 1
checkpoint = int(len(bigram_list) / 10)

for pair, freq in bigram_list.items():
    if not checkpoint % count:
        print(".", end='', flush=True)
    count += 1
    r.zadd("letterpairs", {pair: freq})
