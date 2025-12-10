from flask import Flask, request, jsonify, url_for
import uuid
import requests
import threading

app = Flask(__name__)

# --- DATABASE GIẢ LẬP (In-memory) ---
books_db = {}  # Lưu sách: {id: {data}}
webhooks_db = [] # Lưu các URL đăng ký nhận thông báo: [{'url': '...', 'event': 'new_book'}]

# --- HELPER: HATEOAS BUILDER ---
def build_book_hateoas(book_id):
    """Tạo các link liên quan cho 1 cuốn sách"""
    return {
        "self": url_for('get_book', book_id=book_id, _external=True),
        "update": url_for('update_book', book_id=book_id, _external=True),
        "delete": url_for('delete_book', book_id=book_id, _external=True),
        "all_books": url_for('get_books', _external=True)
    }

# --- HELPER: WEBHOOK TRIGGER (EVENT-DRIVEN SIMULATION) ---
def trigger_webhooks(event_type, payload):
    """Gửi HTTP Request đến các bên đã đăng ký (Subscriber)"""
    print(f"--- [EVENT] Triggering event: {event_type} ---")
    for hook in webhooks_db:
        if hook['event'] == event_type:
            try:
                # Giả lập gửi bất đồng bộ (Fire and Forget)
                print(f"Sending webhook to: {hook['target_url']}")
                requests.post(hook['target_url'], json=payload, timeout=1)
            except Exception as e:
                print(f"Failed to send webhook: {e}")

# ==========================================
# 1. PATTERN: CRUD & 2. PATTERN: QUERY
# ==========================================

@app.route('/books', methods=['GET'])
def get_books():
    """
    Query Pattern:
    - Filtering: ?author=NamCao
    - Pagination: ?page=1&limit=10
    """
    # Lấy tham số query
    author_filter = request.args.get('author')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    # Lọc dữ liệu
    results = list(books_db.values())
    
    if author_filter:
        results = [b for b in results if author_filter.lower() in b['author'].lower()]

    # Phân trang (Pagination)
    start = (page - 1) * limit
    end = start + limit
    paginated_data = results[start:end]

    return jsonify({
        "data": paginated_data,
        "meta": {
            "page": page,
            "limit": limit,
            "total": len(results)
        }
    })

@app.route('/books', methods=['POST'])
def create_book():
    """Tạo sách mới và Kích hoạt Webhook"""
    data = request.json
    book_id = str(uuid.uuid4())
    
    new_book = {
        "id": book_id,
        "title": data.get("title"),
        "author": data.get("author"),
        "price": data.get("price")
    }
    books_db[book_id] = new_book

    # ---> WEBHOOK PATTERN: Kích hoạt sự kiện
    # Sử dụng Thread để không chặn response trả về cho user (Non-blocking)
    webhook_payload = {"event": "new_book", "book": new_book}
    threading.Thread(target=trigger_webhooks, args=("new_book", webhook_payload)).start()

    return jsonify(new_book), 201

# ==========================================
# 3. PATTERN: HATEOAS
# ==========================================

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = books_db.get(book_id)
    if not book:
        return jsonify({"error": "Not found"}), 404
    
    # Nhúng thêm _links vào response
    response = book.copy()
    response['_links'] = build_book_hateoas(book_id)
    
    return jsonify(response)

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    if book_id not in books_db:
        return jsonify({"error": "Not found"}), 404
    data = request.json
    books_db[book_id].update(data)
    return jsonify(books_db[book_id])

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    if book_id in books_db:
        del books_db[book_id]
        return jsonify({"message": "Deleted"}), 204
    return jsonify({"error": "Not found"}), 404

# ==========================================
# 4. PATTERN: WEBHOOK REGISTRATION
# ==========================================

@app.route('/webhooks', methods=['POST'])
def register_webhook():
    """
    Cho phép bên thứ 3 đăng ký nhận thông báo.
    Body: { "target_url": "https://client-app.com/callback", "event": "new_book" }
    """
    data = request.json
    target_url = data.get('target_url')
    event = data.get('event')

    if not target_url or not event:
        return jsonify({"error": "Missing url or event"}), 400

    webhooks_db.append({"target_url": target_url, "event": event})
    return jsonify({"message": "Webhook registered successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)