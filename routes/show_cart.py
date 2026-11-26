from flask import Blueprint, render_template, session

show_cart_bp = Blueprint("show_cart", __name__)


# Mở trang xem giỏ hàng → mặc định GET, không cần methods
@show_cart_bp.route("/show_cart")
def show_cart():

    # Lấy giỏ hàng từ session, chưa mua gì thì là danh sách rỗng (không báo lỗi)
    cart = session.get("cart", [])
    # Cộng tiền tất cả món (giá × số lượng) → tải lại trang vẫn đúng tổng
    # Không có if/break: món nào cũng phải cộng, và phải cộng HẾT
    sub_total = 0
    for item in cart:
        sub_total += item["price"] * item["qty"]

    # Gửi giỏ (products) + tổng tiền (sub_total) sang cart.html
    # Trong HTML: lặp {% for p in products %}, hiện tổng bằng {{ sub_total }}
    return render_template("cart.html", products=cart, sub_total=sub_total)
