from dotenv import load_dotenv
import os
import psycopg2
from flask import Flask, render_template, abort
from flask import request, redirect, url_for, flash
import time
import logging
from collections import defaultdict
from werkzeug.security import generate_password_hash
from db import get_db_connection
from flask import session
from werkzeug.security import check_password_hash

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# 優化的安全配置
app.config['SESSION_COOKIE_SECURE'] = False  # HTTP環境設為False，HTTPS設為True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 簡化的速率限制 - 使用內存快取
request_counts = defaultdict(int)
blocked_ips = {}
last_cleanup = time.time()

# 簡化的日誌設定
logging.basicConfig(
    filename='flask_security.log',
    level=logging.WARNING,
    format='%(asctime)s %(levelname)s %(message)s'
)

# 優化的安全中間件
@app.before_request
def security_middleware():
    global last_cleanup
    
    # 獲取真實IP
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
    # 快速檢查IP封鎖狀態
    if client_ip in blocked_ips:
        if time.time() - blocked_ips[client_ip] < 3600:  # 封鎖1小時
            abort(403)
        else:
            del blocked_ips[client_ip]
    
    # 簡化的惡意請求檢查 - 只檢查最危險的模式
    dangerous_patterns = ['<script', 'union select', 'drop table', '../']
    request_url = request.url.lower()
    
    for pattern in dangerous_patterns:
        if pattern in request_url:
            logging.warning(f'Dangerous request from {client_ip}: {request.url}')
            blocked_ips[client_ip] = time.time()
            abort(403)
    
    # 簡化的速率限制 - 每分鐘檢查
    now = int(time.time())
    minute_key = f"{client_ip}:{now // 60}"
    request_counts[minute_key] += 1
    
    # 檢查當前分鐘的請求數
    if request_counts[minute_key] > 30:  # 每分鐘最多30個請求
        logging.warning(f'Rate limit exceeded for {client_ip}')
        blocked_ips[client_ip] = time.time()
        abort(429)
    
    # 定期清理舊資料（每5分鐘）
    if now - last_cleanup > 300:
        current_minute = now // 60
        old_keys = [k for k in request_counts.keys() if int(k.split(':')[1]) < current_minute - 5]
        for key in old_keys:
            del request_counts[key]
        last_cleanup = now


# 首頁
@app.route('/')
def home():
    return render_template('index.html')

# 文章列表頁
@app.route('/articles')
def articles():
    return render_template('articles.html')

# 課程介紹頁
@app.route('/courses')
def courses():
    return render_template('courses.html')

# 常見問題
@app.route('/faq')
def faq():
    return render_template('faq.html')

# 聯絡我們
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 各篇文章子頁面
@app.route('/music-style')
def music_style():
    return render_template('music-style.html')

@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

@app.route('/emotion')
def emotion():
    return render_template('emotion.html')

@app.route('/confidence')
def confidence():
    return render_template('confidence.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        display_name = request.form.get('display_name', '')

        if not username or not password or not email:
            return "請填寫所有必要欄位（帳號、密碼、Email）"

        conn = get_db_connection()
        cursor = conn.cursor()

        # 檢查帳號是否已存在
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            flash('帳號已存在，請使用其他帳號。', 'error')
            return redirect(url_for('register'))

        # 檢查 Email 是否已存在
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            conn.close()
            flash('此 Email 已註冊過。', 'error')
            return redirect(url_for('register'))

        # 密碼加密後寫入資料庫
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, display_name) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, email, display_name)
        )
        conn.commit()
        conn.close()
        flash('註冊成功，請登入', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # user[2] 是 password_hash
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            return "登入失敗，帳號或密碼錯誤。"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("test_db.html", users=users)

if __name__ == '__main__':
    try:
        conn = get_db_connection()
        print("✅ 資料庫連線成功！")
        conn.close()
    except Exception as e:
        print("❌ 資料庫連線失敗：", e)

    # 改用port 5000供本地開發
    app.run(host='127.0.0.1', port=8000, debug=False)
