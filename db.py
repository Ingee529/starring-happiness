import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # 根據你自己的帳號
        password='ingee8952',  # 換成你自己 MySQL 密碼
        database='starring_happiness'  # 你已建立的資料庫名稱
    )