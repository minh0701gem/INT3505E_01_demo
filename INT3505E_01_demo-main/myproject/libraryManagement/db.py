# db.py
import sqlite3

DATABASE_NAME = 'library.db'

def get_db_connection():
    """Tạo kết nối đến CSDL. Trả về các hàng dưới dạng dictionary."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Dòng này rất quan trọng!
    return conn

# --- Các hàm cho Author ---

def get_all_authors():
    conn = get_db_connection()
    authors = conn.execute('SELECT * FROM authors').fetchall()
    conn.close()
    return [dict(author) for author in authors]

def get_author_by_id(author_id):
    conn = get_db_connection()
    author = conn.execute('SELECT * FROM authors WHERE id = ?', (author_id,)).fetchone()
    conn.close()
    return dict(author) if author else None

def create_author(name, bio=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO authors (name, bio) VALUES (?, ?)', (name, bio))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

# --- Các hàm cho Book ---

def get_all_books():
    conn = get_db_connection()
    # Sử dụng JOIN để lấy cả tên tác giả
    query = """
        SELECT b.id, b.title, b.isbn, b.published_year, b.quantity, a.name as author_name
        FROM books b
        JOIN authors a ON b.author_id = a.id
    """
    books = conn.execute(query).fetchall()
    conn.close()
    return [dict(book) for book in books]

def get_book_by_id(book_id):
    conn = get_db_connection()
    query = """
        SELECT b.id, b.title, b.isbn, b.published_year, b.quantity,
               a.id as author_id, a.name as author_name
        FROM books b
        JOIN authors a ON b.author_id = a.id
        WHERE b.id = ?
    """
    book = conn.execute(query, (book_id,)).fetchone()
    conn.close()
    if not book:
        return None
    # Định dạng lại dữ liệu trả về cho đẹp
    book_dict = dict(book)
    book_dict['author'] = {
        'id': book_dict.pop('author_id'),
        'name': book_dict.pop('author_name')
    }
    return book_dict


def create_book(title, isbn, published_year, quantity, author_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, isbn, published_year, quantity, author_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, isbn, published_year, quantity, author_id))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

# Bạn có thể viết thêm các hàm cho Member và Loan theo logic tương tự
# Ví dụ: get_all_members, create_member, create_loan, ...
# (Giữ lại các hàm cũ liên quan đến sách)

import sqlite3
import bcrypt # Cần cài đặt: pip install bcrypt

# ... (Hàm get_db() của bạn) ...

def create_user(username, password, role='member'):
    """Thêm người dùng mới vào database với mật khẩu đã được hash."""
    db = get_db()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, role),
        )
        db.commit()
    except db.IntegrityError:
        # Xử lý lỗi nếu username đã tồn tại
        return None
    # Lấy lại user vừa tạo để trả về
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    return user

def get_user_by_username(username):
    """Tìm người dùng theo username."""
    db = get_db()
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    return user

def check_password(hashed_password, user_password):
    """Kiểm tra mật khẩu người dùng nhập vào có khớp với hash trong DB không."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)