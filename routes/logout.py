from flask import Blueprint, redirect, session

logout_bp = Blueprint("logout", __name__)


# Bấm logout -> trở về trang chủ
@logout_bp.route("/logout")
def logout():
    # Xóa hết session
    session.clear()
    # Về lại trang chủ
    return redirect("/")
