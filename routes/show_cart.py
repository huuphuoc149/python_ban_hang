from flask import Blueprint, render_template, session

show_cart_bp = Blueprint("show_cart", __name__)


# Mở trang xem giỏ hàng → mặc định GET, không cần methods
@show_cart_bp.route("/show_cart")
def show_cart():
    # Lấy giỏ hàng từ session, chưa mua gì thì là danh sách rỗng (không báo lỗi)
    cart = session.get("cart", [])
    # Gửi giỏ sang cart.html với tên products (nhiều món → số nhiều), trong HTML lặp {% for p in products %}
    return render_template("cart.html", products=cart)
