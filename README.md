# WordBomb
A web-based, multiplayer word game

You have ten seconds to type a word that contains a random bigram ( two consecutive letters).

Scoring is based on how rare the bigram appears in English words.

![ScreenShot](screenshot.png)

Written with Python 3.8, but should work with 3.7

## Running locally ###
Once you have the right version of Python and a Redis server running, install the required libraries:

```pip install -r requirements.txt```

Populate the Redis DB with the words and bigrams:

```python db_setup.py```

Run the application:

```python app.py```

Then navigate to http://localhost:5000/

