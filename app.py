import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from database import init_db, insert_user, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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
    # print("Đã vào hàm login", flush=True)
    if request.method == 'GET':
        # Nếu là GET thì chỉ render trang đăng nhập
        return render_template('login.html')
    # Lấy dữ liệu từ form đăng nhập
    username = (request.form.get('username') or "").strip()
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
        session['role'] = user['role'] # Lưu vai trò, ví dụ: 'user' hoặc 'admin'
        return jsonify({"status": "success", "role": user['role']}), 200
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

@app.route('/exam/<subject>/<grade>')
def exam(subject, grade):
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, question_text, question_type, choices, answer FROM questions WHERE subject = ? AND grade = ?",
        (subject, grade)
    )
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        questions.append({
            "id": row["id"],
            "question": row["question_text"],
            "question_type": row["question_type"],
            "choices": row["choices"],  # Nếu cho dạng MCQ, đây là chuỗi JSON; JS sẽ parse.
            "answer": row["answer"]
        })

    question_count = len(questions)
    time_limit = 3  # 3 phút

    return render_template('exam.html',
                           subject=subject,
                           grade=grade,
                           questions=questions,
                           question_count=question_count,
                           time_limit=time_limit)

@app.route('/choose_exam', methods=['GET', 'POST'])
def choose_exam():
    if request.method == 'GET':
        return render_template('choose_exam.html')
    
    # Khi form được submit, lấy dữ liệu subject và grade
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    
    # Kiểm tra dữ liệu: nếu không có, render lại trang với thông báo lỗi
    if not subject or not grade:
        flash("Vui lòng chọn môn thi và lớp học.")
        return render_template('choose_exam.html')
    
    # Chuyển hướng sang route exam với subject và grade đã chọn
    return redirect(url_for('exam', subject=subject, grade=grade))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash("Bạn không có quyền truy cập trang này.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/admin', methods=['GET'])
@admin_required
def admin_dashboard():
    # Lấy tham số page từ URL, mặc định nếu không có là 'questions'
    page = request.args.get('page', 'questions')

    # Truy vấn dữ liệu (ví dụ, danh sách câu hỏi) nếu cần cho trang 'questions'
    conn = get_db_connection()
    questions = []
    if page == 'questions':
        cursor = conn.execute("SELECT id, subject, grade, question_text, question_type, answer FROM questions")
        questions = cursor.fetchall()
    conn.close()

    # Dựa vào giá trị của page, render nội dung phù hợp
    if page == 'questions':
        content = render_template('partials/admin_questions.html', questions=questions)
    elif page == 'add':
        content = render_template('partials/add_question.html')
    elif page == 'edit':
        # Ví dụ: Khi hiện trang sửa, bạn cần truyền thêm câu hỏi hiện hành
        # content = render_template('partials/edit_question.html', question=question)
        content = "<p>Chức năng sửa câu hỏi (edit) chưa được tích hợp đầy đủ.</p>"
    else:
        content = "<p>Trang quản trị không xác định.</p>"

    return render_template('admin_base.html', page_title="Quản trị - " + page.capitalize(), content=content)


@app.route('/add_question', methods=['POST'])
@admin_required
def add_question():
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    choices = request.form.get('choices') or None
    answer = request.form.get('answer')

    if not subject or not grade or not question_text or not question_type or not answer:
        flash("Vui lòng điền đầy đủ thông tin.")
        return redirect(url_for('admin_dashboard', page='add'))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO questions (subject, grade, question_text, question_type, choices, answer) VALUES (?, ?, ?, ?, ?, ?)",
        (subject, grade, question_text, question_type, choices, answer)
    )
    conn.commit()
    conn.close()

    flash("Câu hỏi đã được thêm thành công.")
    return redirect(url_for('admin_dashboard', page='questions'))

    
@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_question(id):
    conn = get_db_connection()
    question = conn.execute("SELECT * FROM questions WHERE id = ?", (id,)).fetchone()
    if not question:
        flash("Câu hỏi không tồn tại.")
        return redirect(url_for('admin_dashboard', page='questions'))
    if request.method == 'POST':
        # Xử lý cập nhật câu hỏi
        conn.execute(
            "UPDATE questions SET subject = ?, grade = ?, question_text = ?, question_type = ?, choices = ?, answer = ? WHERE id = ?",
            (request.form.get('subject'), request.form.get('grade'), request.form.get('question_text'),
             request.form.get('question_type'), request.form.get('choices') or None, request.form.get('answer'), id)
        )
        conn.commit()
        conn.close()
        flash("Câu hỏi đã được cập nhật.")
        return redirect(url_for('admin_dashboard', page='questions'))
    return render_template('admin_base.html', page_title="Chỉnh sửa Câu hỏi", page="edit", question=question)


    
@app.route('/delete_question/<int:id>', methods=['POST'])
@admin_required
def delete_question(id):
    # Kết nối với cơ sở dữ liệu
    conn = get_db_connection()
    question = conn.execute("SELECT * FROM questions WHERE id = ?", (id,)).fetchone()
    
    # Kiểm tra nếu câu hỏi tồn tại
    if not question:
        flash("Câu hỏi không tồn tại.")
        conn.close()
        return redirect(url_for('admin_dashboard', page='questions'))
    
    # Xóa câu hỏi
    conn.execute("DELETE FROM questions WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Câu hỏi đã được xóa thành công.")
    return redirect(url_for('admin_dashboard', page='questions'))



def create_admin():
    conn = get_db_connection()
    # Đặt dữ liệu admin, ví dụ:
    admin_fullname = "Admin"
    admin_email = "admin@example.com"
    admin_username = "admin"
    admin_password = "123456"  # Bạn nên chọn mật khẩu an toàn hơn trong thực tế
    hashed_password = generate_password_hash(admin_password)
    
    try:
        conn.execute(
            "INSERT INTO users (fullname, email, username, password, role) VALUES (?, ?, ?, ?, ?)",
            (admin_fullname, admin_email, admin_username, hashed_password, "admin")
        )
        conn.commit()
        print("Admin được tạo thành công!")
    except sqlite3.IntegrityError:
        print("Tài khoản admin này đã tồn tại!")
    finally:
        conn.close()

@app.route('/logout')
def logout():
    # Xóa hết các dữ liệu trong session
    session.clear()
    flash("Bạn đã đăng xuất thành công.")
    # Chuyển hướng trở lại trang đăng nhập
    return redirect(url_for('login'))



if __name__ == '__main__':
    init_db()
    # Chạy hàm tạo admin (chạy một lần để cài đặt tài khoản admin)
    #create_admin()
    app.run(debug=True)
