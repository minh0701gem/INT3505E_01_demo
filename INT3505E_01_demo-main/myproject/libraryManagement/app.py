# app.py
from flask import Flask, jsonify, request, abort
from flasgger import Swagger
import db  # Import file db.py của bạn

app = Flask(__name__)

# --- Cấu hình Flasgger (OpenAPI) ---
# (Giữ nguyên như hướng dẫn trước)
app.config['SWAGGER'] = {
    'title': 'Library Management API',
    'uiversion': 3,
    'openapi': '3.0.2',
    # ... các thông tin khác
}
swagger = Swagger(app)


# --- API Endpoints cho Author ---

@app.route('/authors', methods=['GET'])
def list_authors():
    """
    Get a list of all authors.
    ---
    tags:
      - Authors
    responses:
      200:
        description: A list of authors.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Author'
    """
    authors = db.get_all_authors()
    return jsonify(authors)

@app.route('/authors', methods=['POST'])
def add_author():
    """
    Add a new author.
    ---
    tags:
      - Authors
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/NewAuthor'
    responses:
      201:
        description: Author created successfully.
        content:
          application/json:
            schema:
              properties:
                id:
                  type: integer
                message:
                  type: string
    """
    data = request.json
    new_id = db.create_author(data['name'], data.get('bio'))
    return jsonify({'id': new_id, 'message': 'Author created successfully'}), 201


# --- API Endpoints cho Book ---

@app.route('/books', methods=['GET'])
def list_books():
    """
    Get a list of all books.
    ---
    tags:
      - Books
    responses:
      200:
        description: A list of books with their authors.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Book'
    """
    books = db.get_all_books()
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_single_book(book_id):
    """
    Get a single book by its ID.
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Book details.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookDetail'
      404:
        description: Book not found
    """
    book = db.get_book_by_id(book_id)
    if book is None:
        abort(404, description="Book not found")
    return jsonify(book)

@app.route('/books', methods=['POST'])
def add_book():
    """
    Add a new book.
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
        description: Book created successfully.
    """
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

@app.route('/schemas')
def schemas():
    """
    ---
    components:
      schemas:
        Author:
          type: object
          properties:
            id: { type: integer }
            name: { type: string }
            bio: { type: string }
        NewAuthor:
          type: object
          properties:
            name: { type: string, example: 'George Orwell' }
            bio: { type: string, example: 'English novelist, essayist, journalist and critic.' }
        Book:
          type: object
          properties:
            id: { type: integer }
            title: { type: string }
            isbn: { type: string }
            published_year: { type: integer }
            quantity: { type: integer }
            author_name: { type: string }
        BookDetail:
          type: object
          properties:
            id: { type: integer }
            title: { type: string }
            isbn: { type: string }
            published_year: { type: integer }
            quantity: { type: integer }
            author:
              type: object
              properties:
                id: { type: integer }
                name: { type: string }
        NewBook:
          type: object
          required: [title, author_id]
          properties:
            title: { type: string }
            isbn: { type: string }
            published_year: { type: integer }
            quantity: { type: integer }
            author_id: { type: integer }
    """
    pass

if __name__ == '__main__':
    app.run(debug=True)