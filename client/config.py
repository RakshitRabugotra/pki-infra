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

    SQLALCHEMY_TRACK_NOTIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")