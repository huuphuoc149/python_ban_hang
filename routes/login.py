from flask import Blueprint, render_template, redirect, request, session
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint("login", __name__)


# GET: mở form; POST: bấm Sign up
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # Khai báo trước để lần GET vẫn có biến gửi sang HTML, không bị lỗi
    errors = {}
    email = ""
    password = ""
    # Nếu user bấm submit
    if request.method == "POST":
        # Lấy data từ form
        # strip(): bỏ khoảng trắng 2 đầu, chỉ gõ dấu cách cũng tính là trống
        email = request.form["email"].strip()
        # không strip: dấu cách có thể là 1 phần mật khẩu
        password = request.form["password"]

        if not email:
            errors["email"] = "Vui lòng nhập email"
        if not password:
            errors["password"] = "Vui lòng nhập password"

        if not errors:
            # Kết nối database
            conn = get_connection()
            cur = conn.cursor()

            # Lấy data
            cur.execute("SELECT * FROM `user` WHERE email = %s  ", (email,))
            # Lấy 1 user
            user = cur.fetchone()

            cur.close()
            conn.close()

            # Ktr 2 trường hợp
            if not user:
                errors["login"] = "Email hoặc mật khẩu sai"
            # Chuỗi đã mã hóa, mật khẩu vừa gõ
            elif not check_password_hash(user["password"], password):
                errors["login"] = "Email hoặc mật khẩu sai"
            else:
                # session cần app.secret_key trong app.py, thiếu sẽ báo lỗi
                session["user_id"] = user["id"]
                return redirect("/")
    return render_template("login.html", errors=errors, email=email)
