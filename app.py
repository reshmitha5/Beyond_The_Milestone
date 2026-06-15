from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import random
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =========================================================================
# 1. PASTE YOUR GOOGLE API KEY HERE (Inside the quotes!)
# =========================================================================
GOOGLE_API_KEY = API Key

# 2. CONFIGURE AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_level = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    journal_pin = db.Column(db.String(200), nullable=True) 
    moods = db.relationship('MoodEntry', backref='author', lazy=True)
    journals = db.relationship('JournalEntry', backref='author', lazy=True)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood_score = db.Column(db.Integer, nullable=False)
    mood_label = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(200), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --- HELPER FUNCTIONS ---
TRIGGER_WORDS = ["kill myself", "suicide", "end it all", "want to die", "self harm", "mer jaana"]
def check_triggers(text):
    if not text: return False
    for word in TRIGGER_WORDS:
        if word in text.lower(): return True
    return False

# --- ROUTES ---

@app.route('/')
def home(): 
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user); return redirect(url_for('dashboard'))
        flash('Invalid Email or Password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pwd = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        new_user = User(full_name=request.form.get('full_name'), email=request.form.get('email'), password_hash=hashed_pwd)
        db.session.add(new_user); db.session.commit()
        flash('Registration successful!', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user, date=datetime.now().strftime("%B %d, %Y"), quote="You are doing great!")

@app.route('/ai-mentor')
@login_required
def ai_mentor(): return render_template('ai_mentor.html', user=current_user)

@app.route('/chat-api', methods=['POST'])
@login_required
def chat_api():
    msg = request.json.get('message')
    
    # 1. Check Triggers (Safety First) - This always works
    if check_triggers(msg): 
        return jsonify({
            'response': 'I am concerned about you. Please reach out for help. \n\n🇮🇳 India Helplines:\n- iCall: 91529-87821\n- Emergency: 112', 
            'alert': True
        })

    # 2. Try the Real AI (Google)
    try:
        response = model.generate_content(msg)
        return jsonify({'response': response.text, 'alert': False})
        
    except Exception as e:
        # 3. BACKUP MODE (If Google fails, the app WON'T crash!)
        print(f"Google AI Error: {e}")
        print("Using Backup Brain instead.")
        
        # Simple logic so you can still demo the feature
        msg_lower = msg.lower()
        backup_reply = "I hear you. I'm here to support you. Can you tell me more about that?"
        
        if "hello" in msg_lower or "hi" in msg_lower:
            backup_reply = "Hello there! I'm your AI Mentor. How is your day going?"
        elif "sad" in msg_lower or "cry" in msg_lower or "lonely" in msg_lower:
            backup_reply = "I'm sorry you're feeling down. Remember, it's okay to not be okay. I'm listening."
        elif "stress" in msg_lower or "exam" in msg_lower or "study" in msg_lower:
            backup_reply = "Academic stress is very real. Take a deep breath. 5-4-3-2-1 grounding might help. You've got this!"
        elif "happy" in msg_lower or "good" in msg_lower:
            backup_reply = "That's wonderful! It makes me happy to see you happy. What made your day special?"
        elif "thanks" in msg_lower or "thank you" in msg_lower:
            backup_reply = "You are very welcome. I'm always here for you."
            
        return jsonify({'response': backup_reply, 'alert': False})

@app.route('/mood-tracker', methods=['GET', 'POST'])
@login_required
def mood_tracker():
    if request.method == 'POST':
        new_mood = MoodEntry(mood_score=request.form.get('mood_score'), mood_label=request.form.get('mood_label'), author=current_user)
        db.session.add(new_mood); db.session.commit(); return redirect(url_for('mood_tracker'))
    moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date_posted.desc()).all()
    mood_dates = [m.date_posted.strftime('%m-%d') for m in reversed(moods)]
    mood_scores = [m.mood_score for m in reversed(moods)]
    return render_template('mood_tracker.html', user=current_user, moods=moods, mood_dates=mood_dates, mood_scores=mood_scores)

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    # 1. New Entry Logic
    if request.method == 'POST':
        title = request.form.get('title'); content = request.form.get('content')
        if check_triggers(content): flash("Concerning words detected. We care about you.", "error")
        new_entry = JournalEntry(title=title, content=content, author=current_user)
        db.session.add(new_entry); db.session.commit(); return redirect(url_for('journal'))
    
    # 2. Unlock Check Logic
    is_unlocked = session.get('journal_unlocked', False)
    entries = []
    if is_unlocked:
        entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_posted.desc()).all()
        
    return render_template('journal.html', user=current_user, entries=entries, is_unlocked=is_unlocked)

@app.route('/set-pin', methods=['GET', 'POST'])
@login_required
def set_pin():
    if request.method == 'POST':
        pin = request.form.get('pin')
        current_user.journal_pin = generate_password_hash(pin, method='pbkdf2:sha256')
        db.session.commit(); session['journal_unlocked'] = True; return redirect(url_for('journal'))
    return render_template('journal_set_pin.html')

@app.route('/unlock-journal', methods=['POST'])
@login_required
def unlock_journal():
    if not current_user.journal_pin: return redirect(url_for('set_pin'))
    pin = request.form.get('pin')
    if check_password_hash(current_user.journal_pin, pin):
        session['journal_unlocked'] = True
    else:
        flash("Incorrect PIN", "error")
    return redirect(url_for('journal'))

@app.route('/suggestions')
@login_required
def suggestions():
    last_mood = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date_posted.desc()).first()
    mood_category = "General"
    if last_mood:
        if last_mood.mood_score >= 4: mood_category = "Happy"
        elif last_mood.mood_score == 3: mood_category = "Neutral"
        else: mood_category = "Low"
    return render_template('suggestions.html', user=current_user, category=mood_category)

@app.route('/helpline')
@login_required
def helpline():
    return render_template('helpline.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    session.pop('journal_unlocked', None); logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
