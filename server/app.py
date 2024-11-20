from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_session import Session
import requests
import hashlib
import os

# The configuration for the client
from config import ApplicationConfig

# The models for our application
from models import db, now, User, Message

# The forms for the program
from forms import RegistrationForm

# The logger for the app
from logger import logger

# Initialize the app
app = Flask(__name__)
# Set the configurations from external object
app.config.from_object(ApplicationConfig)

# Ensure the upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Initialize the password hash object
bcrypt = Bcrypt(app)

# Initialize the Database
db.init_app(app)
with app.app_context():
    db.create_all()
# Initialize the migrator
migrate = Migrate(app, db)
# Initialize the session manager
Session(app)

login_manager = LoginManager(app)
login_manager.login_view = None
socketio = SocketIO(app)


# Helper functions
def hash_password(password):
    return bcrypt.generate_password_hash(password)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Routes
# @app.route("/")
# def index():
#     """
#     Returns the currently active sessions
#     """

#     if current_user.is_authenticated:
#         # Get active users based on session information
#         redis_conn = app.config["SESSION_REDIS"]
#         session_keys = redis_conn.keys(f"{app.config['SESSION_KEY_PREFIX']}*")

#         session_data = None
#         for key in session_keys:
#             session_data = redis_conn.get(key)
#         # // do whatever you want to do with the session_data  e.g. close any session associated with the username that requested to close other sessions

#         # Pass verification status to the template
#         return jsonify(
#             status="success", message="Active sessions", active_user=session_data
#         )

#     return jsonify(status="error", message="User not authenticated"), 401


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(status="error", message="Unauthorized"), 401


@app.route("/@me", methods=["GET"])
@login_required
def get_user_info():
    # If the current user is found, return it
    if current_user:
        return (
            jsonify(
                status="success",
                message="Found logged-in user",
                user=User.serialize(current_user),
            ),
            200,
        )
    # Else, return not found
    return jsonify(status="error", message="User not logged", user=None), 404


@app.route("/register", methods=["POST"])
def register():
    """
    Registers the user from the form data in request
    """
    # Get the data from the form
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    password = request.form.get("password")

    # Process the public key upload
    public_key_file = request.files["public_key"]

    try:
        filename = secure_filename(
            fullname.lower().replace(" ", "-") + "-" + public_key_file.filename
        )
        public_key_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        public_key_file.save(public_key_path)
    except Exception as e:
        return (
            jsonify(status="error", message="Error while uploading file" + str(e)),
            500,
        )

    # Check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already exists!", "danger")
        return jsonify(status="error", message="User already exists, try login"), 409

    # Get user details and save to the database
    new_user = User(
        full_name=fullname,
        email=email,
        password=hash_password(password),  # assuming hash_password is defined
        public_key=public_key_path,  # Store the file path or public key string
    )
    db.session.add(new_user)
    db.session.commit()
    flash("Account created! Please log in.", "success")
    return jsonify(status="success", message="User created successfully"), 200


@app.route("/login", methods=["POST"])
def login():

    # Get the data from the form
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()

    if user is None and (email is not None and password is not None):
        # Then return an unauthorized response
        logger.error(f"User not found for email={email}")
        flash("User not found", "danger")
        return jsonify({"status": "error", "message": "User not found"}), 404

    # The user exists in the database
    if not bcrypt.check_password_hash(user.password, password):
        # Unauthorized access
        flash("Invalid login credentials.", "danger")
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    # Add the user to the database session
    session["user_id"] = user.id

    # User authenticated, start session
    login_user(user)

    flash("Login successful!", "success")
    return jsonify({"status": "success", "message": "User has been logged in"}), 200


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify(status="success", message="User logged out successfully"), 200
    except Exception as e:
        return (
            jsonify(status="error", message="Error while logging user out: " + str(e)),
            500,
        )


@app.route("/request-verification", methods=["GET"])
@login_required
def request_verification():

    try:
        # Get the current user's email and public key
        response = requests.post(
            app.config["RA_ADDRESS"] + "/ra/request_certificate",
            files={"public-key": open(current_user.public_key, "rb")},
            data={"identifier": current_user.email},
        )

        json = response.json()
        if response.status_code == 200:
            # Logic to send verification email goes here
            return jsonify(status="success", message=json["message"]), 200
        else:
            # Logic to send verification email goes here
            return jsonify(status="error", message=json["message"]), 500

    except Exception as e:
        # Logic to send verification email goes here
        return (
            jsonify(
                status="error",
                message="Error while requesting for verification: " + str(e),
            ),
            500,
        )


@app.route("/verify-sign", methods=["POST"])
@login_required
def verify_sign():
    certificate_sign = request.form["certificate_sign"]

    try:
        # Send a verification request to the server
        response = requests.post(
            app.config["CA_ADDRESS"] + "/ca/verify_certificate",
            files={"public-key": open(current_user.public_key, "rb")},
            data={"sign": certificate_sign},
        )
        # If the certificate is valid, then let the user be verified
        if response.status_code == 200:
            current_user.is_verified = True
            db.session.commit()

        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return (
            jsonify(
                status="error",
                message="Error while requesting for verification: " + str(e),
            ),
            500,
        )


@app.route("/chat/<int:user_id>", methods=["GET", "POST"])
@login_required
def chat(user_id):
    receiver = User.query.get_or_404(user_id)
    if request.method == "POST":
        message = request.form["message"]
        new_message = Message(
            sender_id=current_user.id, receiver_id=receiver.id, message=message
        )
        db.session.add(new_message)
        db.session.commit()

        # Emit message to receiver via WebSocket (real-time update)
        socketio.emit(
            "new_message",
            {
                "sender": current_user.full_name,
                "message": message,
                "receiver_id": receiver.id,
                "sender_id": current_user.id,
            },
            room=f"user_{receiver.id}",
        )

        return redirect(url_for("chat", user_id=user_id))

    # Get chat history
    messages = (
        Message.query.filter(
            (
                (Message.sender_id == current_user.id)
                & (Message.receiver_id == receiver.id)
            )
            | (
                (Message.receiver_id == current_user.id)
                & (Message.sender_id == receiver.id)
            )
        )
        .order_by(Message.timestamp)
        .all()
    )

    return render_template("chat.html", receiver=receiver, messages=messages)


# SocketIO communication for real-time updates
@socketio.on("connect")
def handle_connect():
    # Join a room for each user, using the user id
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")


@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")  # User leaves the room when disconnecting


@socketio.on("new_message")
def handle_new_message(data):
    # When a new message is received, broadcast it to the correct user
    receiver_id = data["receiver_id"]
    emit("new_message", data, room=f"user_{receiver_id}")


@app.route("/inbox")
@login_required
def inbox():
    # Get all received messages for the logged-in user
    received_messages = (
        Message.query.filter_by(receiver_id=current_user.id)
        .order_by(Message.timestamp.desc())
        .all()
    )
    return render_template("inbox.html", messages=received_messages)


# SocketIO communication for real-time updates
@socketio.on("message")
def handle_message(msg):
    send(msg, broadcast=True)


# Run the app
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
