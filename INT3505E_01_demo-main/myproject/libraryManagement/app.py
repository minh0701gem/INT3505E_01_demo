# app.py
from flask import Flask, jsonify, request, abort
from flasgger import Swagger, swag_from

app = Flask(__name__)

# --- Cấu hình Flasgger (OpenAPI) ---
app.config['SWAGGER'] = {
    'title': 'Library Management API',
    'uiversion': 3,
    'openapi': '3.0.2',
    'description': 'An API for managing books in a library.',
    'version': '1.0.0',
    'contact': {
        'name': 'Your Name',
        'url': 'https://github.com/minh0701gem'
    },
    'servers': [
        {
            'url': 'http://127.0.0.1:5000',
            'description': 'Development server'
        }
    ]
}
swagger = Swagger(app)

# --- Dữ liệu giả lập để demo ---
# Trong dự án thực tế, bạn sẽ gọi các hàm từ db.py
books_data = [
    {'id': 1, 'title': 'The Lord of the Rings', 'author': 'J.R.R. Tolkien', 'published_year': 1954},
    {'id': 2, 'title': 'Dune', 'author': 'Frank Herbert', 'published_year': 1965}
]
next_book_id = 3


# --- Định nghĩa các API Endpoint ---

@app.route('/books', methods=['GET'])
def get_books():
    """
    Get a list of all books.
    This endpoint returns a list of all books in the library.
    ---
    tags:
      - Books
    responses:
      200:
        description: A list of books.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Book'
    """
    # Logic thực tế: gọi hàm từ db.py để lấy danh sách sách
    return jsonify(books_data)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get a single book by its ID.
    Returns the details of a specific book.
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        description: The ID of the book to retrieve.
        schema:
          type: integer
    responses:
      200:
        description: The book details.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Book'
      404:
        description: Book not found.
    """
    # Logic thực tế: tìm sách trong DB
    book = next((book for book in books_data if book['id'] == book_id), None)
    if book is None:
        abort(404, description="Book not found")
    return jsonify(book)


@app.route('/books', methods=['POST'])
def add_book():
    """
    Add a new book to the library.
    Creates a new book record.
    ---
    tags:
      - Books
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/NewBook'
    responses:
      201:
        description: The book was successfully created.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Book'
    """
    global next_book_id
    new_book_data = request.json
    new_book = {
        'id': next_book_id,
        'title': new_book_data['title'],
        'author': new_book_data['author'],
        'published_year': new_book_data['published_year']
    }
    books_data.append(new_book)
    next_book_id += 1
    return jsonify(new_book), 201


# --- Định nghĩa các Schema (Model) cho OpenAPI ---
# Điều này giúp tái sử dụng và làm cho spec của bạn sạch sẽ hơn

# Viết schema dưới dạng docstring của một hàm không dùng đến
@app.route('/schemas')
def schemas():
    """
    ---
    components:
      schemas:
        Book:
          type: object
          properties:
            id:
              type: integer
              description: The unique identifier of a book.
              example: 1
            title:
              type: string
              description: The title of the book.
              example: 'The Lord of the Rings'
            author:
              type: string
              description: The author of the book.
              example: 'J.R.R. Tolkien'
            published_year:
              type: integer
              description: The year the book was published.
              example: 1954
        NewBook:
          type: object
          properties:
            title:
              type: string
              description: The title of the book.
            author:
              type: string
              description: The author of the book.
            published_year:
              type: integer
              description: The year the book was published.
    """
    pass # Hàm này không cần làm gì cả


if __name__ == '__main__':
    app.run(debug=True)