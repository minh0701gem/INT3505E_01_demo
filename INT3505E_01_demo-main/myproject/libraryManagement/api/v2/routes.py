from flask import Blueprint, request, jsonify

# Tạo một Blueprint riêng cho v2
v2_blueprint = Blueprint('v2', __name__, url_prefix='/api/v2')

@v2_blueprint.route('/payments', methods=['POST'])
def create_payment_v2():
    data = request.get_json()

    # Kiểm tra cấu trúc request mới của v2
    if not data or not all(key in data for key in ['amount', 'currency', 'paymentMethod']):
        return jsonify({'error': 'Invalid request body for v2'}), 400

    # Logic xử lý thanh toán giả lập cho v2
    print(f"Processing v2 payment via {data['paymentMethod'].get('type', 'UNKNOWN')}")

    amount = data['amount']
    processing_fee = amount * 0.01  # Giả sử phí 1%

    # Phản hồi có cấu trúc mới của v2
    response = {
        'transactionId': f'txn_v2_{int(1000000 * __import__("time").time())}',
        'status': 'success',
        'amountDetails': {
            'originalAmount': amount,
            'currency': data['currency'],
            'feeDetails': {
                'processingFee': processing_fee,
                'totalAmount': amount + processing_fee,
            }
        }
    }
    return jsonify(response), 201