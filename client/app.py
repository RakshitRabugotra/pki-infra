from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from config import ApplicationConfig
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import hashlib
# The models for our application
from models import db, now, User, Session, Message
# The logger for the app
from logger import logger

# Initialize the app
app = Flask(__name__)
# Set the configurations from external object
app.config.from_object(ApplicationConfig)

# Initialize the password hash object
bcrypt = Bcrypt(app)

# Initialize the Database
db.init_app(app)
with app.app_context():
    db.create_all()
# Initialize the migrator
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)

# Helper functions
def hash_password(password):
    return bcrypt.generate_password_hash(password)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        # Get active users based on session information
        active_sessions = Session.query.filter(Session.user_id != current_user.id).all()
        active_users = [session.user for session in active_sessions]
        return render_template('home.html', active_users=active_users)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = hash_password(request.form['password'])

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(full_name=full_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user is None and (email is not None and password is not None):
            # Then return an unauthorized response
            logger.error(f"User not found for email={email}")
            flash('User not found', 'danger')

            return render_template('login.html')
    
        # The user exists in the database
        if not bcrypt.check_password_hash(user.password, password):
            # Unauthorized access
            flash('Invalid login credentials.', 'danger')
            return render_template("login.html")

        # User authenticated, start session
        login_user(user)

        # Create session record
        session_id = hashlib.sha256(f"{user.id}{now()}".encode()).hexdigest()
        new_session = Session(user_id=user.id, session_id=session_id, login_time=now())
        db.session.add(new_session)
        db.session.commit()

        flash('Login successful!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session_data = Session.query.filter_by(user_id=current_user.id).first()
    if session_data:
        db.session.delete(session_data)
        db.session.commit()
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    receiver = User.query.get_or_404(user_id)
    if request.method == 'POST':
        message = request.form['message']
        new_message = Message(sender_id=current_user.id, receiver_id=receiver.id, message=message)
        db.session.add(new_message)
        db.session.commit()

        # Emit message to receiver via WebSocket (real-time update)
        socketio.emit('new_message', {
            'sender': current_user.full_name,
            'message': message,
            'receiver_id': receiver.id,
            'sender_id': current_user.id
        }, room=f"user_{receiver.id}")

        return redirect(url_for('chat', user_id=user_id))
    
    # Get chat history
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver.id)) |
        ((Message.receiver_id == current_user.id) & (Message.sender_id == receiver.id))
    ).order_by(Message.timestamp).all()
    
    return render_template('chat.html', receiver=receiver, messages=messages, sender=current_user)

# SocketIO communication for real-time updates
@socketio.on('connect')
def handle_connect():
    # Join a room for each user, using the user id
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
    
@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")  # User leaves the room when disconnecting


@socketio.on('new_message')
def handle_new_message(data):
    # When a new message is received, broadcast it to the correct user
    receiver_id = data['receiver_id']
    emit('new_message', data, room=f"user_{receiver_id}")

@app.route('/inbox')
@login_required
def inbox():
    # Get all received messages for the logged-in user
    received_messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('inbox.html', messages=received_messages)

# SocketIO communication for real-time updates
@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

# Run the app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
