import os

# 1. Ordnerstruktur erstellen
if not os.path.exists('templates'):
    os.makedirs('templates')
    print("📁 Ordner 'templates' erstellt.")

# 2. Inhalt der Dateien definieren

# --- app.py ---
app_py = '''import os
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
'''

# --- base.html ---
base_html = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wizard-KI-Connect | v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --wizard-blue: #0072C6; --wizard-orange: #FF6600; --glass-bg: rgba(255, 255, 255, 0.05); --glass-border: rgba(255, 255, 255, 0.1); --text-main: #ffffff; --text-muted: #a0a0a0; }
        body { background: radial-gradient(circle at top right, #004b87 0%, #001a33 100%); font-family: 'Inter', sans-serif; color: var(--text-main); min-height: 100vh; }
        .wizard-header { background: rgba(0, 26, 51, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid var(--glass-border); padding: 15px 0; }
        .logo-text { font-weight: 800; color: white; } .logo-text span { color: var(--wizard-orange); }
        .btn-wizard { background: var(--wizard-orange); color: white; font-weight: 700; border: none; border-radius: 8px; padding: 10px 24px; }
        .btn-wizard:hover { background: #e65c00; color: white; }
        .glass-card { background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
        input, textarea, select { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: white; }
        input:focus, textarea:focus, select:focus { background: rgba(255,255,255,0.1); border-color: var(--wizard-orange); color: white; }
    </style>
</head>
<body>
    <nav class="wizard-header">
        <div class="container d-flex justify-content-between align-items-center">
            <a class="navbar-brand logo-text" href="/">🧙‍♂️ Wizard-KI-Connect <span>v3.0</span></a>
            <div class="d-flex align-items-center gap-3">
                {% if session.get('user') %}
                <div class="text-end d-none d-md-block"><div style="font-size: 0.8rem; color: var(--text-muted);">Dein Ruf</div><div style="font-weight: 700; color: var(--wizard-orange);">🔥 250 XP</div></div>
                <a href="/logout" class="btn btn-sm btn-outline-light">Logout</a>
                {% else %}
                <a href="/login" class="btn btn-sm btn-wizard">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

# --- index.html ---
index_html = '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-8 text-center">
        <h1 class="display-4 fw-bold mb-4">Willkommen bei Wizard-KI-Connect</h1>
        <p class="lead mb-5 text-white-50">Dein internes Portal für KI-Erfahrungen, Feedback und Community.</p>
        <a href="/login" class="btn btn-wizard btn-lg px-5">Jetzt einloggen</a>
    </div>
</div>
{% endblock %}'''

# --- login.html ---
login_html = '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-6 col-lg-4">
        <div class="glass-card p-4">
            <div class="text-center mb-4">
                <h3 class="fw-bold">Willkommen zurück</h3>
                <p class="text-muted">Bitte melde dich an.</p>
            </div>
            <form method="POST" action="/login">
                <div class="mb-3"><label class="form-label">Benutzername</label><input type="text" name="username" class="form-control" placeholder="z.B. irsan" required></div>
                <div class="mb-3"><label class="form-label">Passwort</label><input type="password" name="password" class="form-control" placeholder="Dein Passwort" required></div>
                <button type="submit" class="btn btn-wizard w-100">Einloggen</button>
            </form>
            <div class="text-center mt-3"><small class="text-muted">Test-User: irsan / admin123</small></div>
        </div>
    </div>
</div>
{% endblock %}'''

# --- dashboard.html ---
dashboard_html = '''{% extends "base.html" %}
{% block content %}
<div class="row g-4">
    <div class="col-lg-3">
        <div class="glass-card p-3 mb-4 text-center">
            <img src="https://ui-avatars.com/api/?name={{ user.name }}&background=0072C6&color=fff&size=128" class="rounded-circle mb-3 border border-3 border-dark">
            <h5 class="fw-bold mb-1">{{ user.name }}</h5>
            <span class="badge bg-danger mb-2">{{ user.rolle.upper() }}</span>
            <div class="text-muted small">{{ user.email }}</div>
        </div>
        <div class="glass-card p-0 overflow-hidden mb-4">
            <div class="p-3 border-bottom border-secondary bg-dark bg-opacity-25"><h6 class="mb-0 fw-bold">🏆 KI-Ranking</h6></div>
            {% for p in leaderboard %}
            <div class="sidebar-item d-flex align-items-center p-3 border-bottom border-secondary" style="border-color: var(--glass-border) !important;">
                <div class="me-3 text-warning">{{ ['🥇','🥈','🥉'][loop.index0] if loop.index <= 3 else loop.index }}</div>
                <div class="flex-grow-1"><div class="fw-bold small">{{ p.name }}</div><div class="text-muted" style="font-size: 0.7rem;">{{ p.badge }}</div></div>
                <div class="badge bg-warning text-dark rounded-pill">{{ p.score }} XP</div>
            </div>
            {% endfor %}
        </div>
        {% if user.rolle == 'admin' %}
        <div class="glass-card p-3 border-warning">
            <div class="text-warning fw-bold mb-2">👑 Admin Zone</div>
            <a href="#" class="text-decoration-none text-white d-block small">🧹 Trash leeren</a>
        </div>
        {% endif %}
    </div>
    <div class="col-lg-9">
        <div class="glass-card hero-kai p-4 mb-4" style="background: linear-gradient(135deg, var(--wizard-blue) 0%, #004b87 100%); border: 1px solid rgba(255,255,255,0.2);">
            <div class="d-flex align-items-center mb-3">
                <img src="{{ daily_prompt.image }}" class="rounded-circle me-3" style="width: 48px; height: 48px; border: 2px solid white;">
                <div><h5 class="mb-0 fw-bold">🤖 KAI's Daily Briefing</h5><small class="opacity-75">Kuratiert von KI für dich</small></div>
            </div>
            <p class="lead mb-3">{{ daily_prompt.content }}</p>
            <div class="d-flex justify-content-between align-items-center mt-4">
                <span class="badge bg-light text-dark fw-bold">Top UseCase: Excel Dashboarding</span>
                <a href="{{ channel_url }}" target="_blank" class="btn btn-light fw-bold">Zum War Room ⚡</a>
            </div>
        </div>
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold m-0">Community Feed</h4>
            <button class="btn btn-wizard" data-bs-toggle="modal" data-bs-target="#feedbackModal">+ Neuer Beitrag</button>
        </div>
        <ul class="nav nav-pills mb-4 gap-2">
            <li class="nav-item"><button class="nav-link active bg-white text-dark" data-bs-toggle="pill" data-bs-target="#all">🌍 Alles</button></li>
            <li class="nav-item"><button class="nav-link bg-secondary text-white" data-bs-toggle="pill" data-bs-target="#curiosities">🤡 Kurioses</button></li>
            <li class="nav-item"><button class="nav-link bg-secondary text-white" data-bs-toggle="pill" data-bs-target="#usecases">🚀 UseCases</button></li>
        </ul>
        <div class="tab-content">
            <div class="tab-pane fade show active" id="all">
                {% for post in all_posts %}
                <div class="glass-card mb-3">
                    <div class="p-3">
                        {% if post.image_html %}{{ post.image_html | safe }}{% endif %}
                        <div class="d-flex justify-content-between mb-2">
                            <h5 class="text-primary">{{ post.author }}</h5>
                            <span class="badge bg-secondary">{{ post.category }}</span>
                        </div>
                        <p>{{ post.content }}</p>
                        <div class="mt-3 d-flex gap-3">
                            <button class="btn btn-sm btn-outline-light">👍 Like</button>
                            <button class="btn btn-sm btn-outline-light">💬 Reply</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            <div class="tab-pane fade" id="curiosities"><p class="text-center text-muted py-5">Keine Kuriositäten.</p></div>
            <div class="tab-pane fade" id="usecases"><p class="text-center text-muted py-5">Keine UseCases.</p></div>
        </div>
    </div>
</div>
<div class="modal fade" id="feedbackModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <form action="/submit_feedback" method="POST">
                <div class="modal-header"><h5 class="modal-title">✨ Beitrag einreichen</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
                <div class="modal-body">
                    <div class="mb-3"><label class="form-label">Titel</label><input type="text" name="title" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label">Beschreibung</label><textarea name="content" class="form-control" rows="3" required></textarea></div>
                </div>
                <div class="modal-footer"><button type="submit" class="btn btn-wizard w-100">Absenden</button></div>
            </form>
        </div>
    </div>
</div>
{% endblock %}'''

# 3. Dateien schreiben
files = {
    'app.py': app_py,
    'templates/base.html': base_html,
    'templates/index.html': index_html,
    'templates/login.html': login_html,
    'templates/dashboard.html': dashboard_html
}

for filename, content in files.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Datei '{filename}' erstellt.")

print("\n🚀 Projekt erfolgreich generiert! Starte jetzt 'python app.py'")