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