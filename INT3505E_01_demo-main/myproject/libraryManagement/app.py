from flask import Flask, request, jsonify
from db import get_db, close_db, init_db
from datetime import datetime

app = Flask(__name__)
app.teardown_appcontext(close_db)

@app.route('/')
def hello():
    return 'Hello, World!'

# Khởi tạo database
@app.route("/init-db", methods=["GET"])
def init_database():
    init_db(app)
    return jsonify({"message": "Database initialized!"})

#  USERS
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    db = get_db()
    db.execute("INSERT INTO users (name) VALUES (?)", (data["name"],))
    db.commit()
    return jsonify({"message": "User created!"})

# BOOKS

# getBook
@app.route("/books/getallbooks", methods=["GET"])
def get_books():
    db = get_db()
    books = db.execute("SELECT * FROM books").fetchall()
    return jsonify([dict(b) for b in books])

# addBook
@app.route("/books/add", methods=["POST"])
def add_book():
    data = request.json
    db = get_db()
    db.execute("INSERT INTO books (title, author) VALUES (?, ?)",
               (data["title"], data["author"]))
    db.commit()
    return jsonify({"message": "Book added!", "data": {"title": data["title"], "author": data["author"]}})

# editBook
@app.route("/books/edit/<int:id>", methods=["PUT"])
def update_book(id):
    data = request.json
    db = get_db()
    db.execute("UPDATE books SET title=?, author=? WHERE id=?",
               (data["title"], data["author"], id))
    db.commit()
    return jsonify({"message": "Book updated!","data": { "id" : id, "new_title": data["title"], "new_author": data["author"]}})

@app.route("/books/delete/<int:id>", methods=["DELETE"])
def delete_book(id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id=?", (id,))
    db.commit()
    return jsonify({"message": "Book deleted!"})

@app.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.json
    db = get_db()
    # Kiểm tra sách còn không
    book = db.execute("SELECT available FROM books WHERE id=?", (data["book_id"],)).fetchone()
    if not book or book["available"] == 0:
        return jsonify({"error": "Book not available"}), 400

    db.execute("INSERT INTO borrows (user_id, book_id, borrow_date) VALUES (?, ?, ?)",
               (data["user_id"], data["book_id"], datetime.now().isoformat()))
    db.execute("UPDATE books SET available=0 WHERE id=?", (data["book_id"],))
    db.commit()
    return jsonify({"message": "Book borrowed!"})

@app.route("/return", methods=["POST"])
def return_book():
    data = request.json
    db = get_db()
    db.execute("UPDATE borrows SET return_date=? WHERE user_id=? AND book_id=? AND return_date IS NULL",
               (datetime.now().isoformat(), data["user_id"], data["book_id"]))
    db.execute("UPDATE books SET available=1 WHERE id=?", (data["book_id"],))
    db.commit()
    return jsonify({"message": "Book returned!"})

if __name__ == "__main__":
    app.run(debug=True)