from dotenv import load_dotenv
import os
import redis

load_dotenv()


class ApplicationConfig:
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
    except KeyError:
        print("[ERROR]: Couldn't find a environment configuration for 'SECRET_KEY'")
        exit(-1)

    UPLOAD_FOLDER = "uploads/"
    ALLOWED_EXTENSIONS = {"pem"}
    SQLALCHEMY_TRACK_NOTIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "session:"
    SESSION_REDIS = redis.StrictRedis(host="localhost", port=6379, db=0)

    # Session information
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Information about other backend
    RA_ADDRESS = "http://127.0.0.1:5000"
    CA_ADDRESS = "http://127.0.0.1:5001"
