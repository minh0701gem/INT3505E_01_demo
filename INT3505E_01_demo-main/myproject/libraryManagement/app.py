# app.py (ĐÃ SỬA LỖI HOÀN CHỈNH)

from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, JWTManager
from . import db
# ======================================================================
# --- KHỞI TẠO VÀ CẤU HÌNH APP (TẤT CẢ TRONG MỘT CHỖ) ---
# ======================================================================

app = Flask(__name__)

# --- CẤU HÌNH DATABASE ---
# Đặt tên file CSDL. Nó sẽ được tạo trong thư mục instance của Flask.
app.config['DATABASE'] = 'library.sqlite'
# Đăng ký các hàm quản lý database (close_db) và lệnh CLI (init-db) với app
db.init_app(app)

# --- CẤU HÌNH JWT (JSON Web Token) ---
# Thay thế "your-super-secret-key" bằng một chuỗi bí mật, ngẫu nhiên và an toàn
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-change-this-in-production"
jwt = JWTManager(app)

# --- CẤU HÌNH FLASGGER (OpenAPI / Swagger) ---
template = {
    "swagger": "2.0",
    "info": {
        "title": "Library Management API",
        "description": "API for a simple library management system with JWT authentication.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your bearer token in the format **Bearer &lt;token&gt;**"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}
swagger = Swagger(app, template=template)


# ======================================================================
# --- CÁC API ENDPOINTS ---
# ======================================================================

# === API AUTHENTICATION ===

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username:
              type: string
              example: newuser
            password:
              type: string
              format: password
              example: mysecretpassword
    responses:
      201:
        description: User created successfully.
      400:
        description: Missing username or password.
      409:
        description: Username already exists.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        abort(400, description="Missing username or password")

    if db.get_user_by_username(data['username']):
        return jsonify({"msg": "Username already exists"}), 409

    db.create_user(data['username'], data['password'])
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Log in a user and return access and refresh tokens.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username:
              type: string
              example: adminuser
            password:
              type: string
              format: password
              example: adminpass
    responses:
      200:
        description: Login successful. Returns access and refresh tokens.
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
      401:
        description: Bad username or password.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        abort(400, description="Missing username or password")
        
    user = db.get_user_by_username(data['username'])

    if user and db.check_password(user['password'], data['password']):
        user_identity = {
            "id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
        access_token = create_access_token(identity=user_identity)
        refresh_token = create_refresh_token(identity=user_identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    return jsonify({"msg": "Bad username or password"}), 401


# === CÁC API ĐƯỢC BẢO VỆ VÀ PHÂN QUYỀN ===

# --- API Endpoints cho Author ---

@app.route('/authors', methods=['GET'])
@jwt_required()
def list_authors():
    """
    Get a list of all authors. (Requires login)
    ---
    tags:
      - Authors
    responses:
      200:
        description: A list of authors.
    """
    authors = db.get_all_authors()
    return jsonify(authors)

@app.route('/authors', methods=['POST'])
@jwt_required()
def add_author():
    """
    Add a new author. (Requires admin role)
    ---
    tags:
      - Authors
    parameters:
      - name: body
        in: body
        required: true
        schema:
            type: object
            required: [name]
            properties:
                name:
                    type: string
                    example: "J.K. Rowling"
                bio:
                    type: string
                    example: "Author of Harry Potter series."
    responses:
      201:
        description: Author created successfully.
      403:
        description: Admins only!
    """
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({"msg": "Admins only!"}), 403

    data = request.json
    new_id = db.create_author(data['name'], data.get('bio'))
    return jsonify({'id': new_id, 'message': 'Author created successfully'}), 201


# --- API Endpoints cho Book ---

@app.route('/books', methods=['GET'])
@jwt_required()
def list_books():
    """
    Get a list of all books. (Requires login)
    ---
    tags:
      - Books
    responses:
      200:
        description: A list of books with their authors.
    """
    books = db.get_all_books()
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_single_book(book_id):
    """
    Get a single book by its ID. (Requires login)
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Book details.
      404:
        description: Book not found
    """
    book = db.get_book_by_id(book_id)
    if book is None:
        abort(404, description="Book not found")
    return jsonify(book)

@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    """
    Add a new book. (Requires admin role)
    ---
    tags:
      - Books
    parameters:
      - name: body
        in: body
        required: true
        schema:
            type: object
            required: [title, author_id]
            properties:
                title:
                    type: string
                    example: "The Lord of the Rings"
                isbn:
                    type: string
                    example: "978-0-618-05326-7"
                published_year:
                    type: integer
                    example: 1954
                quantity:
                    type: integer
                    example: 10
                author_id:
                    type: integer
                    example: 1
    responses:
      201:
        description: Book created successfully.
      403:
        description: Admins only!
    """
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({"msg": "Admins only!"}), 403

    data = request.json
    new_id = db.create_book(
        data['title'],
        data.get('isbn'),
        data.get('published_year'),
        data.get('quantity', 1),
        data['author_id']
    )
    return jsonify({'id': new_id, 'message': 'Book created successfully'}), 201


if __name__ == '__main__':
    app.run(debug=True)