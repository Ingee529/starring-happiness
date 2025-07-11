from dotenv import load_dotenv
import os
import psycopg2
from flask import Flask, render_template
from flask import request, redirect, url_for, flash
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

    app.run(debug=True, port=8000)
