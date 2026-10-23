import os
import secrets
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# --- KONFIGURATION ---
OPENWEBUI_CHANNEL_URL = "https://ki.wizard.de/channels/cd0c970a-1ee5-4f4c-bfde-f89dfe2711a9"

# --- TEST-USER DATENBANK ---
TEST_USERS = {
    'irsan': {'name': 'Irsan Sefer', 'email': 'is@wizard.de', 'rolle': 'admin', 'pw': 'admin123'},
    'flo': {'name': 'Flo', 'email': 'flo@wizard.de', 'rolle': 'admin', 'pw': 'admin123'},
    'patrick': {'name': 'Patrick', 'email': 'patrick@wizard.de', 'rolle': 'user', 'pw': 'user123'},
    'till': {'name': 'Till', 'email': 'till@wizard.de', 'rolle': 'user', 'pw': 'user123'},
    'lucas': {'name': 'Lucas', 'email': 'lucas@wizard.de', 'rolle': 'user', 'pw': 'user123'}
}

def get_current_user():
    if 'user' in session:
        return TEST_USERS.get(session['user'], {})
    return {}

@app.context_processor
def inject_globals():
    return dict(
        is_logged_in=lambda: 'user' in session,
        get_current_user=get_current_user
    )

posts = [{'author': 'Irsan', 'category': 'Info', 'content': 'Willkommen bei Wizard-KI-Connect v2.0!', 'date': 'Vor 1 Tag'}]
curiosities = [{'author': 'System', 'category': 'WTF Moment', 'content': 'Das beste Beispiel: KAI wollte "IT-Support-Assistant" schreiben, aber das Timing-Skript hat es zu "IT-Support-Arsch" korrigiert.', 'date': 'Vor 1 Monat'}]
SUBMITTED_PROMPTS = []
SUBMITTED_CURIOSITIES = []

LEADERBOARD = [
    {'name': 'Patrick', 'score': 150, 'badge': '🏆 Master Prompter', 'role': 'user'},
    {'name': 'Lucas', 'score': 120, 'badge': '🥈 Excel Wizard', 'role': 'user'},
    {'name': 'Till', 'score': 90, 'badge': '🥉 Bug Hunter', 'role': 'user'},
    {'name': 'Flo', 'score': 85, 'badge': '🚀 AI Evangelist', 'role': 'admin'},
    {'name': 'Irsan', 'score': 70, 'badge': '🧙‍♂️ Admin', 'role': 'admin'}
]

DAILY_PROMPT = {
    'title': '✨ Prompt des Tages',
    'author': 'KAI (Automatisch)',
    'content': 'Der beste Prompt der Community gestern war: "Generiere eine Excel-Tabelle mit 3 Spalten und formatiere sie wie ein Dashboard." – Gefunden von Patrick.',
    'image': 'https://img.icons8.com/ios-filled/50/0072C6/brain.png'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        if user_input in TEST_USERS and TEST_USERS[user_input]['pw'] == pass_input:
            session['user'] = user_input
            return redirect(url_for('dashboard'))
        flash('Falscher Benutzername oder Passwort!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')
    image_data = request.form.get('image_data', '')
    image_html = ''
    if image_data:
        image_html = f'<img src="{image_data}" class="mt-2 rounded shadow-sm" style="max-width: 100%; height: auto; max-height: 300px; display: block; margin: 0 auto;">'
    if title and content:
        new_post = {'author': user['name'], 'category': category, 'content': content, 'date': 'Gerade eben', 'image_html': image_html}
        if 'Fail' in category or 'Curiosities' in category or 'WTF' in category:
            SUBMITTED_CURIOSITIES.insert(0, new_post)
        else:
            SUBMITTED_PROMPTS.insert(0, new_post)
        flash('Beitrag erfolgreich gesendet! (+10 Punkte)', 'success')
    else:
        flash('Bitte Titel und Inhalt ausfüllen.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    all_posts = posts + SUBMITTED_PROMPTS
    all_curiosities = curiosities + SUBMITTED_CURIOSITIES
    return render_template('dashboard.html', user=user, all_posts=all_posts, curiosities=all_curiosities, leaderboard=LEADERBOARD, daily_prompt=DAILY_PROMPT, now=datetime.now(), channel_url=OPENWEBUI_CHANNEL_URL)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
