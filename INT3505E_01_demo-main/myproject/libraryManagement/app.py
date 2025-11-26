from flask import Flask

# Import các blueprints từ các file routes tương ứng
from api.v1.routes import v1_blueprint
from api.v2.routes import v2_blueprint

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Đăng ký blueprint v1
app.register_blueprint(v1_blueprint)

# Đăng ký blueprint v2
app.register_blueprint(v2_blueprint)

@app.route('/')
def index():
    return "MiniPay API Server is running. Use /api/v1/ or /api/v2/ endpoints."

if __name__ == '__main__':
    app.run(debug=True, port=5000)