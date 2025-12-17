# models.py
import random
import string
import time
from collections import defaultdict

# --- Giả lập Database Sách ---
BOOKS_DB = {
    1: {"id": 1, "title": "Lão Hạc", "author": "Nam Cao", "available": True},
    2: {"id": 2, "title": "Số Đỏ", "author": "Vũ Trọng Phụng", "available": False},
    3: {"id": 3, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài", "available": True},
}

# --- Giả lập Database User và API Keys ---
USERS_DB = {
    "dev_free_key_123": {"email": "free@example.com", "plan": "freemium", "call_count": 0},
    "dev_pro_key_789": {"email": "pro@example.com", "plan": "pro", "call_count": 0}
}

# --- Giả lập Analytics ---
ANALYTICS_DB = defaultdict(list)

def is_api_key_valid(api_key):
    return api_key in USERS_DB

def log_api_call(api_key, endpoint):
    USERS_DB[api_key]['call_count'] += 1
    ANALYTICS_DB[api_key].append({"endpoint": endpoint, "timestamp": time.time()})

def get_analytics_for_key(api_key):
    user = USERS_DB.get(api_key)
    total_calls = len(ANALYTICS_DB.get(api_key, []))
    # Trong thực tế sẽ phức tạp hơn (tính error rate, call volume theo thời gian)
    return {"plan": user['plan'], "total_calls": total_calls}
    
def generate_api_key(email):
    key = "dev_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    USERS_DB[key] = {"email": email, "plan": "freemium", "call_count": 0}
    return key

def search_books_by_title(query, limit):
    results = [book for book in BOOKS_DB.values() if query.lower() in book['title'].lower()]
    return results[:limit]

def get_book_by_id(book_id):
    return BOOKS_DB.get(book_id)