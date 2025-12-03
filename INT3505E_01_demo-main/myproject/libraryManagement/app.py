# ==============================================================================
# PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT
# ==============================================================================
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

# ==============================================================================
# PHẦN 2: CẤU HÌNH BAN ĐẦU
# ==============================================================================

# --- Cấu hình logging ---
# Định dạng log: Thời gian - Tên logger - Cấp độ - Nội dung
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ghi log ra file 'app.log', xoay vòng khi file đạt 1MB, giữ lại 5 file backup
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# --- Khởi tạo ứng dụng Flask và các tiện ích ---
app = Flask(__name__)

# Tích hợp logger đã cấu hình vào ứng dụng Flask
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Tích hợp Prometheus Metrics
# Tự động tạo endpoint /metrics để thu thập số liệu
metrics = PrometheusMetrics(app)

# Tích hợp Rate Limiter
# Sử dụng địa chỉ IP của client để xác định và giới hạn
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"], # Giới hạn mặc định cho mọi endpoint
    storage_uri="memory://" # Lưu trữ trạng thái rate limit trong bộ nhớ (phù hợp cho demo)
)

# Ghi log khi ứng dụng khởi động
app.logger.info("Ứng dụng Bookstore API đã khởi động")

# ==============================================================================
# PHẦN 3: DỮ LIỆU GIẢ LẬP (DATABASE IN-MEMORY)
# ==============================================================================

books = [
    {"id": 1, "title": "Lược sử loài người", "author": "Yuval Noah Harari"},
    {"id": 2, "title": "Tư duy nhanh và chậm", "author": "Daniel Kahneman"}
]
next_id = 3

# ==============================================================================
# PHẦN 4: ĐỊNH NGHĨA CÁC API ENDPOINTS
# ==============================================================================

@app.route('/')
def index():
    """Endpoint chào mừng."""
    return "Welcome to the Bookstore API! Visit /books or /metrics."

@app.route('/books', methods=['GET'])
@limiter.limit("10 per minute") # Áp dụng giới hạn riêng, chặt hơn cho endpoint này
def get_books():
    """
    Lấy danh sách tất cả các cuốn sách.
    Endpoint này bị giới hạn 10 request mỗi phút cho mỗi IP.
    """
    app.logger.info(f"Yêu cầu lấy danh sách sách từ IP: {get_remote_address()}")
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
@limiter.limit("10 per minute")
def get_book(book_id):
    """
    Lấy thông tin chi tiết của một cuốn sách theo ID.
    """
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        app.logger.info(f"Tìm thấy sách ID {book_id}")
        return jsonify(book)
    else:
        app.logger.warning(f"Không tìm thấy sách với ID {book_id}")
        return jsonify({"error": "Book not found"}), 404

@app.route('/books', methods=['POST'])
@limiter.limit("5 per minute") # Endpoint tạo mới có giới hạn chặt chẽ nhất
def add_book():
    """
    Thêm một cuốn sách mới.
    Endpoint này bị giới hạn 5 request mỗi phút cho mỗi IP để chống spam.
    """
    global next_id
    if not request.json or 'title' not in request.json or 'author' not in request.json:
        app.logger.warning(f"Yêu cầu thêm sách thất bại do thiếu dữ liệu từ IP: {get_remote_address()}")
        return jsonify({"error": "Missing title or author"}), 400

    new_book = {
        "id": next_id,
        "title": request.json['title'],
        "author": request.json['author']
    }
    books.append(new_book)
    next_id += 1
    
    # Ghi log một audit log đơn giản
    app.logger.info(f"[AUDIT] Sách mới đã được tạo ID {new_book['id']}: '{new_book['title']}' bởi IP {get_remote_address()}")
    return jsonify(new_book), 201

# ==============================================================================
# PHẦN 5: KHỞI CHẠY ỨNG DỤNG
# ==============================================================================

if __name__ == '__main__':
    # Chạy ứng dụng trên cổng 5000 và bật chế độ debug
    # Trong môi trường production, bạn sẽ dùng một WSGI server như Gunicorn hoặc uWSGI
    app.run(host='0.0.0.0', port=5000, debug=True)