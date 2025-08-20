import os, subprocess, sqlite3, json, requests
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from datetime import datetime
import shutil

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

def get_gophish_api_key():
    """Obtiene la API key de GoPhish desde el archivo .env"""
    try:
        with open('../.env', 'r') as f:
            for line in f:
                if line.startswith('GOPHISH_API_KEY='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return None

def get_campaign_stats(campaign_id):
    """Obtiene estadísticas de la campaña desde GoPhish API"""
    api_key = get_gophish_api_key()
    if not api_key or not campaign_id:
        return None
    
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(f'http://gophish:3333/api/campaigns/{campaign_id}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            stats = {
                'total': len(results),
                'sent': 0,
                'opened': 0,
                'clicked': 0,
                'submitted': 0,
                'reported': 0,
                'details': []
            }
            
            for result in results:
                status = result.get('status', '')
                email = result.get('email', '')
                
                stats['details'].append({
                    'email': email,
                    'status': status,
                    'time': result.get('time', '')
                })
                
                if 'Sent' in status:
                    stats['sent'] += 1
                if 'Opened' in status:
                    stats['opened'] += 1
                if 'Clicked' in status:
                    stats['clicked'] += 1
                if 'Submitted' in status:
                    stats['submitted'] += 1
                if 'Reported' in status:
                    stats['reported'] += 1
            
            return stats
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
    
    return None

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
    
    # Obtener estadísticas de la campaña actual
    stats = None
    if last_id:
        stats = get_campaign_stats(last_id)
    
    return render_template('index.html', last_campaign_id=last_id, stats=stats)

@app.route('/api/campaign-stats/<campaign_id>')
@login_required
def api_campaign_stats(campaign_id):
    """API endpoint para obtener estadísticas en tiempo real"""
    stats = get_campaign_stats(campaign_id)
    return jsonify(stats) if stats else jsonify({'error': 'No se pudieron obtener las estadísticas'})

@app.route('/start', methods=['POST'])
@login_required
def start_campaign():
    # Verificar si ansible-playbook está disponible
    ansible_path = shutil.which("ansible-playbook")
    if not ansible_path:
        flash("❌ Error: Ansible no está instalado. Instala con: pip install ansible")
        return redirect(url_for('index'))
    
    try:
        cmd = [ansible_path, "-i", "ansible/inventory.ini", "ansible/playbooks/start_campaign.yml"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
        
        if res.returncode != 0:
            flash(f"❌ Error ejecutando Ansible: {res.stderr}")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"❌ Error: {str(e)}")
        return redirect(url_for('index'))
    
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
    # Verificar si ansible-playbook está disponible
    ansible_path = shutil.which("ansible-playbook")
    if not ansible_path:
        flash("❌ Error: Ansible no está instalado. Instala con: pip install ansible")
        return redirect(url_for('index'))
    
    try:
        cmd = [ansible_path, "-i", "ansible/inventory.ini", "ansible/playbooks/stop_campaign.yml"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
        
        if res.returncode != 0:
            flash(f"❌ Error ejecutando Ansible: {res.stderr}")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"❌ Error: {str(e)}")
        return redirect(url_for('index'))
    
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
    # Verificar si ansible-playbook está disponible
    ansible_path = shutil.which("ansible-playbook")
    if not ansible_path:
        flash("❌ Error: Ansible no está instalado. Instala con: pip install ansible")
        return redirect(url_for('index'))
    
    try:
        cmd = [ansible_path, "-i", "ansible/inventory.ini", "ansible/playbooks/report.yml"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
        
        if res.returncode != 0:
            flash(f"❌ Error ejecutando Ansible: {res.stderr}")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"❌ Error: {str(e)}")
        return redirect(url_for('index'))
    
    cid = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            cid = f.read().strip()
    log_action('report', cid)
    flash(f"Reporte generado para campaña: {cid}")
    return redirect(url_for('history'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Vista del dashboard con gráficas detalladas"""
    last_id = None
    if os.path.exists('.last_campaign_id'):
        with open('.last_campaign_id') as f:
            last_id = f.read().strip()
    
    stats = None
    if last_id:
        stats = get_campaign_stats(last_id)
    
    return render_template('dashboard.html', campaign_id=last_id, stats=stats)

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
    app.run(host='0.0.0.0', port=8080, debug=True)