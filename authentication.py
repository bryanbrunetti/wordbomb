from functools import wraps
from flask import redirect, url_for, session

def player_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("player"):
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function
