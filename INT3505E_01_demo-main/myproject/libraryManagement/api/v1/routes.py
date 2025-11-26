from flask import Blueprint, request, jsonify

# Tạo một Blueprint cho v1. `url_prefix` sẽ tự động thêm '/api/v1' vào trước mọi route
v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

@v1_blueprint.route('/payments', methods=['POST'])
def create_payment_v1():
    data = request.get_json()

    # Kiểm tra các trường bắt buộc của v1
    if not data or not all(key in data for key in ['amount', 'currency', 'cardNumber']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Logic xử lý thanh toán giả lập
    print(f"Processing v1 payment for {data['amount']} {data['currency']}")

    # Phản hồi của v1
    response = {
        'transactionId': f'txn_{int(1000000 * __import__("time").time())}',
        'status': 'success',
        'message': 'Payment processed successfully.'
    }
    return jsonify(response), 201