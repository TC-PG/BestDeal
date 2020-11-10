from flask import redirect, render_template, request, session, jsonify
from functools import wraps

errorMessage = {
    "message": None
}

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            errorMessage["message"] = '請先登入'
            return jsonify(errorMessage), 500
        return f(*args, **kwargs)
    return decorated_function
