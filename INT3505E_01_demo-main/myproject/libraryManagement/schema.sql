-- schema.sql (PHIÊN BẢN HOÀN CHỈNH)

-- Xóa các bảng cũ nếu tồn tại để tránh lỗi khi khởi tạo lại
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS user;

-- Bảng lưu trữ thông tin tác giả
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bio TEXT
);

-- Bảng lưu trữ thông tin sách
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    isbn TEXT UNIQUE,
    published_year INTEGER,
    quantity INTEGER NOT NULL DEFAULT 1,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors (id)
);

-- Bảng lưu trữ thông tin thành viên thư viện
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    join_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lưu trữ thông tin người dùng hệ thống (để đăng nhập)
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL, -- Sẽ lưu password đã được hash
  role TEXT NOT NULL DEFAULT 'member' -- Vai trò: 'member' hoặc 'admin'
);

-- Bảng lưu trữ thông tin mượn sách
CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    loan_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    -- 'borrowed' (đang mượn), 'returned' (đã trả)
    status TEXT NOT NULL CHECK(status IN ('borrowed', 'returned')) DEFAULT 'borrowed',
    FOREIGN KEY (book_id) REFERENCES books (id),
    FOREIGN KEY (member_id) REFERENCES members (id)
);

-- TẠO DỮ LIỆU MẪU --

-- Tạo một user admin mẫu để test
-- Mật khẩu là 'adminpass', đã được hash sẵn.
INSERT INTO user (username, password, role) VALUES 
('admin', 'scrypt:32768:8:1$y5bZ8tH3xR2fP6qV$5a5d85a3c0356c9a7276710188b22a59a7238295f7c00e167c1368945f34044c688344155b57f08149e1a2f9011e403487f7a7f4337d1d283627048154625b6d', 'admin');

-- Tạo một vài tác giả
INSERT INTO authors (name, bio) VALUES
('J.K. Rowling', 'Author of the Harry Potter series.'),
('J.R.R. Tolkien', 'Author of The Lord of the Rings.');

-- Tạo một vài cuốn sách
INSERT INTO books (title, isbn, published_year, quantity, author_id) VALUES
('Harry Potter and the Sorcerer''s Stone', '978-0590353427', 1997, 5, 1),
('The Hobbit', '978-0618260300', 1937, 3, 2),
('The Fellowship of the Ring', '978-0618346257', 1954, 2, 2);