import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from database import init_db, insert_user, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Dùng để quản lý session
DATABASE = 'database.db'
# Route cho trang landing (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route cho trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Đã vào hàm login", flush=True)
    if request.method == 'GET':
        # Nếu là GET thì chỉ render trang đăng nhập
        return render_template('login.html')
    # Lấy dữ liệu từ form đăng nhập
    username = request.form.get('username').strip()
    password = request.form.get('password')

    # Kiểm tra các trường bắt buộc có được điền không
    if not username or not password:
        # Trả về JSON lỗi để phù hợp với xử lý AJAX từ script.js
        return jsonify({"status": "error", "message": "Vui lòng điền đầy đủ thông tin."}), 400
    
    # Truy vấn người dùng từ cơ sở dữ liệu dựa trên username và password
    conn = get_db_connection()  # Hàm này lấy kết nối tới database
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    
    # Nếu tìm thấy người dùng, đăng nhập thành công
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"status": "success"}), 200
    else:
        # Nếu không tìm thấy, render lại trang đăng nhập với thông báo lỗi
        return jsonify({"status": "error", "message": "Tài khoản hoặc mật khẩu không đúng."}), 401

# Route cho trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # Lấy dữ liệu từ form
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Kiểm tra dữ liệu nhập vào có đầy đủ không
    if not fullname or not email or not username or not password or not confirm_password:
        return render_template('register.html', error="Vui lòng điền đầy đủ thông tin.",
                               fullname=fullname, email=email, username=username)

    # Kiểm tra mật khẩu có khớp không
    if password != confirm_password:
        return render_template('register.html', error="Mật khẩu không khớp.",
                               fullname=fullname, email=email, username=username)

    # Hash mật khẩu trước khi lưu
    hashed_password = generate_password_hash(password)
    # Chèn người dùng vào cơ sở dữ liệu
    try:
        success = insert_user(fullname, email, username, hashed_password)  # Hàm trong database.py
        if success:
            flash("Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.")
            return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập nếu thành công
    except ValueError as e:
        return render_template('register.html', error=str(e),
                               fullname=fullname, email=email, username=username)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
