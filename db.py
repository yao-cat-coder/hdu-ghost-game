import pymysql
import streamlit as st
DB_CONFIG = {
    "host": st.secrets["pingkai"]["host"],
    "port": st.secrets["pingkai"]["port"],
    "user": st.secrets["pingkai"]["user"],
    "password": st.secrets["pingkai"]["password"],
    "charset": "utf8mb4",
    "ssl": {"ssl": {}},
    "autocommit": True
}
DB_NAME = st.secrets["pingkai"]["database"]
def get_connection():
  conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4;")
    cursor.close()
    conn.select_db(DB_NAME)
    return conn
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            score INT NOT NULL,
            comment TEXT NOT NULL
        )
    ''')
    cursor.close()
    conn.close()
def add_review(user_name, password, location, name, score, comment):
    conn = get_connection()
    cursor = conn.cursor()
    # 注意：占位符从 SQLite 的 ? 变成了 MySQL 的 %s
    cursor.execute('''
        INSERT INTO reviews (user_name, password, location, name, score, comment)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_name, password, location, name, score, comment))
    cursor.close()
    conn.close()
def get_reviews(location=None):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor) 
    if location:
        cursor.execute("SELECT * FROM reviews WHERE location = %s ORDER BY id DESC", (location,))
    else:
        cursor.execute("SELECT * FROM reviews ORDER BY id DESC")
        
    rows = cursor.fetchall() 
    conn.close()
    
    return rows 
def delete_review(review_id, user_name, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM reviews WHERE id = %s AND user_name = %s AND password = %s
    ''', (review_id, user_name, password))
    rows_deleted = cursor.rowcount
    cursor.close()
    conn.close()
    
    return rows_deleted > 0
