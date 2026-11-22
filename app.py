DB_CONFIG = {
    "host": st.secrets["pingkai"]["host"],
    "port": st.secrets["pingkai"]["port"],
    "user": st.secrets["pingkai"]["user"],
    "password": st.secrets["pingkai"]["password"],
    "charset": "utf8mb4",
    "ssl": {"verify_cert": False},
    "autocommit": True
}
DB_NAME = st.secrets["pingkai"]["database"]

def get_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4;")
        cursor.close()
        conn.select_db(DB_NAME)
        return conn
    except Exception as e:
        st.error(f"数据库连接失败：{e}")
        raise e

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

# ===== 重要：注释下面这一行！不要自动执行！=====
# init_db()
