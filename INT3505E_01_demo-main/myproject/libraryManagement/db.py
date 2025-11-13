# db.py (PHIÊN BẢN HOÀN CHỈNH)

import sqlite3
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    """
    Kết nối tới CSDL, hoặc trả về kết nối đã có sẵn trong 'g'.
    'g' là một đối tượng đặc biệt, duy nhất cho mỗi request.
    Nó được dùng để lưu trữ dữ liệu có thể cần truy cập nhiều lần trong một request.
    """
    if 'db' not in g:
        # Tạo kết nối đến CSDL được định nghĩa trong config
        g.db = sqlite3.connect(
            current_app.config.get('DATABASE', 'library.sqlite'), # Thêm tên file CSDL mặc định
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Trả về các hàng dưới dạng dictionary-like object
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """
    Đóng kết nối CSDL nếu nó đã được tạo.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """
    Xóa dữ liệu cũ và tạo các bảng mới.
    """
    db = get_db()
    
    # Dùng file schema.sql để tạo bảng
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Tạo lệnh 'flask init-db' để khởi tạo CSDL."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """
    Đăng ký các hàm quản lý CSDL với ứng dụng Flask.
    """
    # Yêu cầu Flask gọi hàm close_db khi dọn dẹp sau khi trả về response
    app.teardown_appcontext(close_db)
    # Thêm lệnh 'init-db' vào CLI của Flask
    app.cli.add_command(init_db_command)

# --- CÁC HÀM TRUY VẤN CỦA BẠN (ĐÃ SỬA ĐỂ DÙNG get_db()) ---

def get_user_by_username(username):
    """Tìm người dùng theo username."""
    db = get_db()  # <-- SỬA Ở ĐÂY
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    return user

def create_user(username, password):
    """Tạo người dùng mới với mật khẩu đã được hash."""
    db = get_db()  # <-- SỬA Ở ĐÂY
    db.execute(
        "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), 'user'), # Mặc định là 'user'
    )
    db.commit()

def check_password(hashed_password, user_password):
    """Kiểm tra mật khẩu người dùng nhập vào có khớp với hash trong DB không."""
    return check_password_hash(hashed_password, user_password)

# --- Các hàm cho Author ---
def get_all_authors():
    db = get_db()
    authors = db.execute("SELECT * FROM author").fetchall()
    return [dict(row) for row in authors]

def create_author(name, bio):
    db = get_db()
    cursor = db.execute("INSERT INTO author (name, bio) VALUES (?, ?)", (name, bio))
    db.commit()
    return cursor.lastrowid

# --- Các hàm cho Book ---
def get_all_books():
    db = get_db()
    books = db.execute("""
        SELECT b.id, b.title, b.isbn, b.published_year, b.quantity, a.name as author_name
        FROM book b JOIN author a ON b.author_id = a.id
    """).fetchall()
    return [dict(row) for row in books]

def get_book_by_id(book_id):
    db = get_db()
    book = db.execute("""
        SELECT b.id, b.title, b.isbn, b.published_year, b.quantity, a.name as author_name
        FROM book b JOIN author a ON b.author_id = a.id
        WHERE b.id = ?
    """, (book_id,)).fetchone()
    return dict(book) if book else None

def create_book(title, isbn, published_year, quantity, author_id):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO book (title, isbn, published_year, quantity, author_id) VALUES (?, ?, ?, ?, ?)",
        (title, isbn, published_year, quantity, author_id)
    )
    db.commit()
    return cursor.lastrowid
# Thêm vào cuối file db.py

# --- Các hàm cho Member ---
def get_all_members():
    db = get_db()
    members = db.execute("SELECT * FROM members").fetchall()
    return [dict(row) for row in members]

def create_member(name, email):
    db = get_db()
    cursor = db.execute("INSERT INTO members (name, email) VALUES (?, ?)", (name, email))
    db.commit()
    return cursor.lastrowid

# --- Các hàm cho Loan ---
def create_loan(book_id, member_id):
    db = get_db()
    # TODO: Trước khi cho mượn, nên kiểm tra xem sách có còn không (quantity > 0)
    cursor = db.execute(
        "INSERT INTO loans (book_id, member_id) VALUES (?, ?)",
        (book_id, member_id)
    )
    # Giảm số lượng sách đi 1
    db.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
    db.commit()
    return cursor.lastrowid

def return_book(loan_id):
    db = get_db()
    # Lấy thông tin về lượt mượn để biết book_id là gì
    loan = db.execute("SELECT book_id FROM loans WHERE id = ?", (loan_id,)).fetchone()
    if not loan:
        return False # Không tìm thấy lượt mượn

    # Cập nhật trạng thái lượt mượn
    db.execute(
        "UPDATE loans SET status = 'returned', return_date = CURRENT_TIMESTAMP WHERE id = ?",
        (loan_id,)
    )
    # Tăng số lượng sách lên 1
    db.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (loan['book_id'],))
    db.commit()
    return True