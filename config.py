import os
import redis
from dotenv import load_dotenv

def load(app):
    APP_ROOT = os.path.join(os.path.dirname(__file__))
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)
    app.secret_key = os.environ["SESSION_SECRET"]
    app.redis = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    app.round_time = 5