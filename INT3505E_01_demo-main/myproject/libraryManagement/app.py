# app.py
from flask import Flask, jsonify, request, render_template, redirect, url_for
import models

app = Flask(__name__)

# --- CÁC ENDPOINT CỦA API SÁCH ---

@app.route('/api/v1/books/search', methods=['GET'])
def search_books():
    # Giả lập xác thực API key
    api_key = request.headers.get('X-API-KEY')
    if not models.is_api_key_valid(api_key):
        return jsonify({"error": "Invalid API Key"}), 401

    # Logic tìm kiếm
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    books = models.search_books_by_title(query, limit)
    
    # Ghi nhận lại lượt gọi API (phục vụ analytics)
    models.log_api_call(api_key, '/api/v1/books/search')
    
    return jsonify(books)

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_details(book_id):
    api_key = request.headers.get('X-API-KEY')
    if not models.is_api_key_valid(api_key):
        return jsonify({"error": "Invalid API Key"}), 401

    book = models.get_book_by_id(book_id)
    if book:
        models.log_api_call(api_key, f'/api/v1/books/{book_id}')
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

# --- CÁC ROUTE CHO DEVELOPER PORTAL ---

@app.route('/')
def developer_portal():
    return render_template('portal.html')

@app.route('/docs')
def documentation():
    return render_template('docs.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/register', methods=['POST'])
def register_developer():
    # Trong thực tế, bạn sẽ gửi email, lưu vào DB,... Ở đây ta giả lập
    email = request.form.get('email')
    new_key = models.generate_api_key(email)
    # Redirect tới trang dashboard với key mới
    return redirect(url_for('dashboard', api_key=new_key))

@app.route('/dashboard')
def dashboard():
    api_key = request.args.get('api_key')
    if not api_key or not models.is_api_key_valid(api_key):
        return "Invalid access", 401
    
    # Lấy dữ liệu analytics
    analytics = models.get_analytics_for_key(api_key)
    return render_template('dashboard.html', api_key=api_key, analytics=analytics)

if __name__ == '__main__':
    app.run(debug=True)