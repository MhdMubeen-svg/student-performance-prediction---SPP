from flask import Flask, render_template, request, jsonify, session
import sqlite3
import hashlib
from datetime import date

app = Flask(__name__)
app.secret_key = 'mubeen_secret_key_2024'
DB = 'mubeen.db'

# ══ DATABASE ══════════════════════════════
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username  TEXT UNIQUE NOT NULL,
        email     TEXT UNIQUE NOT NULL,
        password  TEXT NOT NULL,
        firstName TEXT NOT NULL,
        lastName  TEXT DEFAULT '',
        createdAt TEXT DEFAULT (date('now'))
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id        INTEGER NOT NULL,
        name           TEXT NOT NULL,
        register_no    TEXT NOT NULL,
        dept           TEXT DEFAULT '',
        semester       TEXT DEFAULT '',
        acad_year      TEXT DEFAULT '',
        gender         TEXT DEFAULT '',
        attendance     INTEGER DEFAULT 0,
        hour_study     INTEGER DEFAULT 0,
        internal       INTEGER DEFAULT 0,
        arrears        INTEGER DEFAULT 0,
        projects       INTEGER DEFAULT 0,
        internships    INTEGER DEFAULT 0,
        sports         INTEGER DEFAULT 0,
        outer_programs INTEGER DEFAULT 0,
        certs          INTEGER DEFAULT 0,
        leader         INTEGER DEFAULT 0,
        class_rank     TEXT DEFAULT '',
        score          INTEGER DEFAULT 0,
        level          TEXT DEFAULT 'basic',
        date_added     TEXT DEFAULT (date('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()

# ══ HELPERS ═══════════════════════════════
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def calc_score(d):
    att  = min(int(d.get('attendance',0)),100)
    hrs  = min(int(d.get('hour_study',0)),16)
    intl = min(int(d.get('internal',0)),100)
    proj = min(int(d.get('projects',0)),5)
    intr = min(int(d.get('internships',0)),3)
    sp   = min(int(d.get('sports',0)),1)
    out  = min(int(d.get('outer_programs',0)),2)
    lead = min(int(d.get('leader',0)),2)
    cert = min(int(d.get('certs',0)),3)
    return max(0,min(100,round(
        att/100*25 + hrs/16*10 + intl/100*25 +
        proj/5*15  + intr/3*10 + sp*4 +
        out/2*4    + lead/2*4  + cert/3*3
    )))

def get_level(score, arrears):
    if arrears>0 or score<30: return 'ineligible'
    if score>=80: return 'advanced'
    if score>=60: return 'adv_intermediate'
    if score>=50: return 'intermediate'
    return 'basic'

def current_user():
    uid = session.get('user_id')
    if not uid: return None
    conn = get_db()
    u = conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    conn.close()
    return dict(u) if u else None

def user_dict(u):
    return {'id':u['id'],'username':u['username'],'email':u['email'],
            'firstName':u['firstName'],'lastName':u['lastName'] or '',
            'createdAt':u['createdAt']}

# ══ PAGE ══════════════════════════════════
@app.route('/')
def index():
    return render_template('index.html')

# ══ AUTH API ══════════════════════════════
@app.route('/api/login', methods=['POST'])
def api_login():
    d  = request.get_json()
    ident = d.get('identifier','').strip()
    pw    = d.get('password','')
    if not ident or not pw:
        return jsonify({'ok':False,'msg':'Please fill in all fields.'})
    conn = get_db()
    u = conn.execute('SELECT * FROM users WHERE username=? OR email=?',(ident,ident.lower())).fetchone()
    conn.close()
    if not u:
        return jsonify({'ok':False,'msg':'No account found with that username or email.'})
    if u['password'] != hash_pw(pw):
        return jsonify({'ok':False,'msg':'Incorrect password. Please try again.'})
    session['user_id'] = u['id']
    return jsonify({'ok':True,'user':user_dict(u)})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    d  = request.get_json()
    fn = d.get('firstName','').strip()
    ln = d.get('lastName','').strip()
    un = d.get('username','').strip()
    em = d.get('email','').strip().lower()
    pw = d.get('password','')
    if not fn or not un or not em or not pw:
        return jsonify({'ok':False,'msg':'Please fill in all required fields.'})
    if len(un)<3:
        return jsonify({'ok':False,'field':'username','msg':'Username must be at least 3 characters.'})
    if len(pw)<6:
        return jsonify({'ok':False,'field':'password','msg':'Password must be at least 6 characters.'})
    if '@' not in em:
        return jsonify({'ok':False,'field':'email','msg':'Please enter a valid email address.'})
    conn = get_db()
    if conn.execute('SELECT id FROM users WHERE username=?',(un,)).fetchone():
        conn.close(); return jsonify({'ok':False,'field':'username','msg':'Username already taken.'})
    if conn.execute('SELECT id FROM users WHERE email=?',(em,)).fetchone():
        conn.close(); return jsonify({'ok':False,'field':'email','msg':'Email already registered.'})
    conn.execute('INSERT INTO users (username,email,password,firstName,lastName) VALUES (?,?,?,?,?)',
                 (un,em,hash_pw(pw),fn,ln))
    conn.commit()
    u = conn.execute('SELECT * FROM users WHERE username=?',(un,)).fetchone()
    conn.close()
    session['user_id'] = u['id']
    return jsonify({'ok':True,'user':user_dict(u)})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear(); return jsonify({'ok':True})

@app.route('/api/me')
def api_me():
    u = current_user()
    if not u: return jsonify({'ok':False})
    return jsonify({'ok':True,'user':u})

@app.route('/api/check-username')
def api_check_username():
    un = request.args.get('u','').strip()
    conn = get_db()
    taken = conn.execute('SELECT id FROM users WHERE username=?',(un,)).fetchone() is not None
    conn.close()
    return jsonify({'taken':taken})

# ══ STUDENTS API ══════════════════════════
@app.route('/api/students', methods=['GET'])
def api_get_students():
    u = current_user()
    if not u: return jsonify({'ok':False,'msg':'Not logged in'}),401
    conn = get_db()
    rows = conn.execute('SELECT * FROM students WHERE user_id=? ORDER BY score DESC',(u['id'],)).fetchall()
    conn.close()
    return jsonify({'ok':True,'students':[dict(r) for r in rows]})

@app.route('/api/students', methods=['POST'])
def api_add_student():
    u = current_user()
    if not u: return jsonify({'ok':False,'msg':'Not logged in'}),401
    d = request.get_json()
    if not d.get('name') or not d.get('register_no'):
        return jsonify({'ok':False,'msg':'Name and Register Number are required.'})
    score = calc_score(d)
    level = get_level(score, int(d.get('arrears',0)))
    today = date.today().strftime('%d/%m/%Y')
    conn = get_db()
    cur = conn.execute('''INSERT INTO students
        (user_id,name,register_no,dept,semester,acad_year,gender,
         attendance,hour_study,internal,arrears,projects,internships,
         sports,outer_programs,certs,leader,class_rank,score,level,date_added)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
        u['id'], d.get('name','').strip(), d.get('register_no','').strip(),
        d.get('dept',''), d.get('semester',''), d.get('acad_year',''), d.get('gender',''),
        int(d.get('attendance',0)), int(d.get('hour_study',0)), int(d.get('internal',0)),
        int(d.get('arrears',0)), int(d.get('projects',0)), int(d.get('internships',0)),
        int(d.get('sports',0)), int(d.get('outer_programs',0)), int(d.get('certs',0)),
        int(d.get('leader',0)), d.get('class_rank',''), score, level, today
    ))
    new_id = cur.lastrowid
    conn.commit()
    student = conn.execute('SELECT * FROM students WHERE id=?',(new_id,)).fetchone()
    conn.close()
    return jsonify({'ok':True,'student':dict(student),'score':score,'level':level})

@app.route('/api/students/<int:sid>', methods=['DELETE'])
def api_delete_student(sid):
    u = current_user()
    if not u: return jsonify({'ok':False}),401
    conn = get_db()
    conn.execute('DELETE FROM students WHERE id=? AND user_id=?',(sid,u['id']))
    conn.commit(); conn.close()
    return jsonify({'ok':True})

@app.route('/api/students/clear', methods=['DELETE'])
def api_clear_students():
    u = current_user()
    if not u: return jsonify({'ok':False}),401
    conn = get_db()
    conn.execute('DELETE FROM students WHERE user_id=?',(u['id'],))
    conn.commit(); conn.close()
    return jsonify({'ok':True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
