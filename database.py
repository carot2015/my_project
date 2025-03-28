import sqlite3

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Kết quả trả về dưới dạng dictionary
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         fullname TEXT NOT NULL,
                         email TEXT UNIQUE NOT NULL,
                         username TEXT UNIQUE NOT NULL,
                         password TEXT NOT NULL,
                         role TEXT NOT NULL DEFAULT 'user'
                       );''')
    
    # Tạo bảng questions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                grade TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                choices TEXT,
                answer TEXT NOT NULL
            );''')
    conn.close()

def user_exists(email, username):
    conn = get_db_connection()
    cursor = conn.execute("SELECT email, username FROM users WHERE email = ? OR username = ?", (email, username))
    row = cursor.fetchone()
    conn.close()
    return row

# Hàm insert_user được cập nhật để nhận tham số role (mặc định là 'user')
def insert_user(fullname, email, username, hashed_password, role="user"):
    # Kiểm tra nếu email hoặc username đã tồn tại
    row = user_exists(email, username)
    if row:
        if row["email"].lower() == email.lower():
            raise ValueError("Email đã tồn tại.")
        if row["username"].lower() == username.lower():
            raise ValueError("Tên tài khoản đã tồn tại.")
    # Nếu không trùng, thực hiện INSERT
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('''
                INSERT INTO users (fullname, email, username, password, role) 
                VALUES (?, ?, ?, ?, ?)
            ''', (fullname, email, username, hashed_password, role))
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        conn.close()
        # Nếu có lỗi ngoài kiểm tra trên (ít khả năng xảy ra ở trường hợp này)
        raise ValueError("Đăng ký thất bại. Vui lòng thử lại.")

def delete_user_by_username(username):
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.close()
