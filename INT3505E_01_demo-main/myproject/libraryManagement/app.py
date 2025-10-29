# app.py
from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, JWTManager

import db  # Import file db.py của bạn

app = Flask(__name__)

# --- CẤU HÌNH JWT (JSON Web Token) ---
# Thay thế "your-super-secret-key" bằng một chuỗi bí mật, ngẫu nhiên và an toàn
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-change-this-in-production"
jwt = JWTManager(app)

# --- CẤU HÌNH FLASGGER (OpenAPI) ---
# Thêm cấu hình bảo mật cho Swagger UI để có thể test các API được bảo vệ
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
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
}
app.config['SWAGGER'] = {
    'title': 'Library Management API',
    'uiversion': 3,
}
swagger = Swagger(app, config=swagger_config, template=template)


# === CÁC API MỚI: USER AUTHENTICATION ===

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [username, password]
            properties:
              username: { type: string }
              password: { type: string, format: password }
    responses:
      201:
        description: User created successfully.
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
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [username, password]
            properties:
              username: { type: string }
              password: { type: string, format: password }
    responses:
      200:
        description: Login successful.
      401:
        description: Bad username or password.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        abort(400, description="Missing username or password")
        
    user = db.get_user_by_username(data['username'])

    # user['password'] là hash, data['password'] là mật khẩu thuần
    if user and db.check_password(user['password'], data['password']):
        # Tạo identity cho token, chứa các thông tin cần thiết về user
        user_identity = {
            "id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
        access_token = create_access_token(identity=user_identity)
        refresh_token = create_refresh_token(identity=user_identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    return jsonify({"msg": "Bad username or password"}), 401


# === CÁC API ĐÃ ĐƯỢC BẢO VỆ VÀ PHÂN QUYỀN ===

# --- API Endpoints cho Author ---

@app.route('/authors', methods=['GET'])
@jwt_required()  # YÊU CẦU ĐĂNG NHẬP
def list_authors():
    """
    Get a list of all authors. (Requires login)
    ---
    tags:
      - Authors
    security:
      - Bearer: []
    responses:
      200:
        description: A list of authors.
    """
    authors = db.get_all_authors()
    return jsonify(authors)

@app.route('/authors', methods=['POST'])
@jwt_required()  # YÊU CẦU ĐĂNG NHẬP
def add_author():
    """
    Add a new author. (Requires admin role)
    ---
    tags:
      - Authors
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/NewAuthor'
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
@jwt_required()  # YÊU CẦU ĐĂNG NHẬP
def list_books():
    """
    Get a list of all books. (Requires login)
    ---
    tags:
      - Books
    security:
      - Bearer: []
    responses:
      200:
        description: A list of books with their authors.
    """
    books = db.get_all_books()
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()  # YÊU CẦU ĐĂNG NHẬP
def get_single_book(book_id):
    """
    Get a single book by its ID. (Requires login)
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
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
@jwt_required()  # YÊU CẦU ĐĂNG NHẬP
def add_book():
    """
    Add a new book. (Requires admin role)
    ---
    tags:
      - Books
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/NewBook'
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


# --- Định nghĩa Schemas cho OpenAPI ---
# (Phần này giữ nguyên, không cần thay đổi)
@app.route('/schemas')
def schemas():
    """... (nội dung schemas không đổi) ..."""
    pass

if __name__ == '__main__':
    app.run(debug=True) 