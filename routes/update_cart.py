from flask import Blueprint, request, session, jsonify

update_cart_bp = Blueprint("update_cart", __name__)


@update_cart_bp.route("/update_cart", methods=["POST"])
def update_cart():
    # id sản phẩm đổi sang số
    product_id = int(request.json.get("id"))
    # Loại thao tác: "increase" (nút +), "decrease" (nút −), "delete" (nút x)
    action = request.json.get("action")
    # Lấy giỏ trong session, chưa có thì là danh sách rỗng
    cart = session.get("cart", [])
    # Lây từng món
    for item in cart:
        print("DANG XET:", item["id"], "| action:", action)
        if item["id"] == product_id:
            if action == "increase":
                item["qty"] += 1
            elif action == "decrease":
                # Chặn ở cả Python: dù có ai gửi thẳng yêu cầu (không qua nút) thì qty cũng không xuống dưới 1
                if item["qty"] > 1:
                    item["qty"] -= 1
            elif action == "delete":
                cart.remove(item)
            break
    # Gán lại giỏ vào session để Flask lưu
    session["cart"] = cart
    # Cộng lại tổng số lượng sau khi tăng/giảm/xóa; đặt sau khi lưu giỏ để đếm đúng số mới
    cart_count = 0
    for item in cart:
        cart_count += item["qty"]  # không break: phải cộng HẾT các món
    # Cất tổng vào session → lúc tải lại trang header kiểm tra có thì hiển thị
    session["cart_count"] = cart_count
    # Báo cho JS biết đã cập nhật xong
    return jsonify({"status": "success", "cart_count": cart_count})
