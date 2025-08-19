import os, subprocess, sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY','change_me')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    id = 1
    username = os.getenv('UI_ADMIN_USER','admin')
    password = os.getenv('UI_ADMIN_PASS','admin')

@login_manager.user_loader
def load_user(user_id):
    u = User(); u.id = user_id
    return u

DB='ui.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        campaign_id TEXT,
        timestamp TEXT
    )''')
    conn.commit(); conn.close()

init_db()

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == User.username and request.form['password'] == User.password:
            u=User(); login_user(u)
            return redirect(url_for('index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    last_id = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            last_id = f.read().strip()
    return render_template('index.html', last_campaign_id=last_id)

@app.route('/start', methods=['POST'])
@login_required
def start_campaign():
    cmd = ["ansible-playbook","-i","ansible/inventory.ini","ansible/playbooks/start_campaign.yml"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    cid = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            cid = f.read().strip()
    log_action('start', cid)
    flash(f"Campaña iniciada: {cid}")
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
@login_required
def stop_campaign():
    cmd = ["ansible-playbook","-i","ansible/inventory.ini","ansible/playbooks/stop_campaign.yml"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    cid = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            cid = f.read().strip()
    log_action('stop', cid)
    flash(f"Campaña detenida: {cid}")
    return redirect(url_for('index'))

@app.route('/report', methods=['POST'])
@login_required
def report():
    cmd = ["ansible-playbook","-i","ansible/inventory.ini","ansible/playbooks/report.yml"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    cid = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            cid = f.read().strip()
    log_action('report', cid)
    flash(f"Reporte generado para campaña: {cid}")
    return redirect(url_for('history'))

@app.route('/history')
@login_required
def history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, action, campaign_id, timestamp FROM history ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    reports = []
    rep_dir = os.path.abspath('../reports')
    if os.path.exists(rep_dir):
        for f in os.listdir(rep_dir):
            if f.endswith('.pdf'):
                reports.append(f)
    return render_template('history.html', rows=rows, reports=reports)

@app.route('/reports/<path:filename>')
@login_required
def download_report(filename):
    return send_from_directory('../reports', filename, as_attachment=True)

def log_action(action, cid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO history(action, campaign_id, timestamp) VALUES(?,?,?)', (action, cid, datetime.now().isoformat()))
    conn.commit(); conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
