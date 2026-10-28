from flask import Blueprint, render_template, redirect, request
import re
import os
from flask import current_app
from db import get_connection
from werkzeug.security import generate_password_hash

register_bp = Blueprint("register", __name__)

ALLOWED_EXTENSION = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 1


def is_value_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION


def handle_file_upload(file):
    result = {"success": False, "error": None}

    if file.filename == "":
        result["error"] = "Vui lòng chọn 1 file"
        return result
    if not allowed_file(file.filename):
        result["error"] = "Chỉ chấp nhận file ảnh [PNG,JPG,JPEG,GIF]"
        return result

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size >= MAX_FILE_SIZE_MB * 1024 * 1024:
        result["error"] = "File quá lớn ! Chỉ được phép tối đa 1MB"
        return result

    result["success"] = True
    return result


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    errors = {}
    name = ""
    email = ""
    password = ""
    # Nếu user bấm submit
    if request.method == "POST":
        # Lấy data từ form
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        avatar = request.files["avatar"]

        if not name:
            errors["name"] = "Vui lòng nhập tên"
        if not email:
            errors["email"] = "Vui lòng nhập email"
        if not password:
            errors["password"] = "Vui lòng nhập password"

        upload_result = handle_file_upload(avatar)
        if not upload_result["success"]:
            errors["avatar"] = upload_result["error"]

        if not errors:

            hashed_password = generate_password_hash(password)
            UPLOAD_FOLDER = os.path.join(current_app.root_path, "static", "uploads")

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            filename = avatar.filename
            avatar.save(os.path.join(UPLOAD_FOLDER, filename))

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO `user` (name,email,password,avatar) VALUES(%s,%s,%s,%s)",
                (name, email, hashed_password, filename),
            )

            conn.commit()

            cur.close()
            conn.close()

            return redirect("/login")

    return render_template("register.html", errors=errors, name=name, email=email)
