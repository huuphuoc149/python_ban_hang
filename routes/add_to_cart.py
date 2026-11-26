from flask import Blueprint, request, session, jsonify
from db import get_connection

add_to_cart_bp = Blueprint("add_to_cart", __name__)


@add_to_cart_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = int(request.json.get("id"))

    # Kết nối database
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM product WHERE id = %s", (product_id,))

    product = cur.fetchone()

    cur.close()
    conn.close()

    # Nếu kh có sản phẩm
    if not product:
        return jsonify({"status": "fail", "message": "Product not found"}), 404

    # Lấy giỏ hàng từ session, chưa có thì là khởi tạo rỗng
    cart = session.get("cart", [])
    # Ktr xem sp đã có trong cart chưa
    found = False
    for item in cart:  # Duyệt từng món trong giỏ hàng
        if item["id"] == product_id:  # Sp này có trùng với sp vừa bấm kh ?
            item["qty"] += 1  # Nếu có -> tăng qty lên 1
            found = True  # Đánh dấu đã thấy
            break  # Thoát vòng lặp, khỏi xét tiếp

    # Nếu chưa có thì thêm mới qty vào = 1
    if not found:
        product_data = {
            "id": product["id"],
            "title": product["title"],
            "price": float(product["price"]),
            "image": product["image"],
            "qty": 1,
        }
        # Thêm vào cuối giỏ
        cart.append(product_data)
    # gán lại giỏ vào session: để Flask biết session đã thay đổi và lưu lại
    # (chỉ sửa qty bên trong mà không gán lại thì Flask có thể không lưu)

    session["cart"] = cart
    # Cộng tổng số lượng các món; đặt sau khi lưu giỏ để đếm cả món vừa thêm
    cart_count = 0
    for item in cart:
        cart_count += item["qty"]  # không break: phải cộng HẾT các món
    # Cất tổng vào session → lúc tải lại trang header kiểm tra có thì hiển thị
    session["cart_count"] = cart_count
    # "product" = tên khóa tự đặt (theo cur.fetchone ở trên), chứa cả giỏ; "cart_count" để JS hiển thị lên header
    # trả JSON báo thành công kèm cả giỏ hàng → JS nhận ở await response.json()
    return jsonify(
        {
            "status": "success",
            "product": session["cart"],
            "cart_count": cart_count,
        }
    )
