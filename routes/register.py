from flask import Blueprint, render_template, redirect, request
import re  # biểu thức chính quy, dùng để kiểm tra định dạng email
import os  # làm việc với đường dẫn, thư mục, con trỏ file
from flask import current_app  # trỏ tới app đang chạy, để lấy root_path (thư mục dự án)
from db import get_connection
from werkzeug.security import generate_password_hash

register_bp = Blueprint("register", __name__)

ALLOWED_EXTENSION = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 1


def is_value_email(email):
    # Mẫu: phần trước @, rồi @, rồi tên miền, dấu chấm, đuôi (vd abc@gmail.com)
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # re.match trả về None nếu không khớp → so "is not None" để ra True/False
    return re.match(pattern, email) is not None


def allowed_file(filename):
    # Phải có dấu "." mới có đuôi file
    # rsplit(".", 1): tách 1 lần từ BÊN PHẢI, để "a.b.jpg" vẫn lấy đúng "jpg"
    # lower(): "PNG" và "png" đều hợp lệ
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION


def handle_file_upload(file):
    # Trả về dict để nơi gọi biết vừa thành công hay thất bại, vừa có câu báo lỗi
    result = {"success": False, "error": None}

    if (
        file.filename == ""
    ):  # không chọn file thì trình duyệt vẫn gửi lên, nhưng tên rỗng
        result["error"] = "Vui lòng chọn 1 file"
        return result
    if not allowed_file(file.filename):
        result["error"] = "Chỉ chấp nhận file ảnh [PNG,JPG,JPEG,GIF]"
        return result

    file.seek(0, os.SEEK_END)  # đưa con trỏ về CUỐI file
    file_size = file.tell()  # vị trí con trỏ lúc này = dung lượng file (byte)
    file.seek(0)  # đưa con trỏ về ĐẦU file; thiếu dòng này thì save() ra file rỗng

    # 1MB = 1024 * 1024 byte; dùng ">=" vì đề yêu cầu NHỎ HƠN 1MB (đúng 1MB cũng bị chặn)
    if file_size >= MAX_FILE_SIZE_MB * 1024 * 1024:
        result["error"] = "File quá lớn ! Chỉ được phép tối đa 1MB"
        return result

    result["success"] = True
    return result


@register_bp.route(
    "/register", methods=["GET", "POST"]
)  # GET: mở form; POST: bấm Signup
def register():
    # Khai báo trước để lần GET vẫn có biến gửi sang HTML, không bị lỗi "chưa định nghĩa"
    errors = {}
    name = ""
    email = ""
    password = ""
    # Nếu user bấm submit
    if request.method == "POST":
        # Lấy data từ form
        # strip(): bỏ khoảng trắng 2 đầu, chỉ gõ dấu cách cũng tính là trống
        name = request.form["name"].strip()
        # không strip: dấu cách có thể là một phần mật khẩu
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
            # mã hóa, không lưu mật khẩu thật
            hashed_password = generate_password_hash(password)
            # Đường dẫn tuyệt đối tới static/uploads, chạy app ở thư mục nào cũng đúng
            UPLOAD_FOLDER = os.path.join(current_app.root_path, "static", "uploads")

            # chưa có thư mục thì tạo, tránh lỗi khi save
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            filename = avatar.filename
            # ảnh lưu vào thư mục, database chỉ lưu tên file
            avatar.save(os.path.join(UPLOAD_FOLDER, filename))

            conn = get_connection()
            cur = conn.cursor()
            # cột ở vị trí nào thì giá trị ở vị trí đó
            # `user` có backtick vì trùng từ khóa MySQL; %s để pymysql tự điền, chặn SQL injection
            cur.execute(
                "INSERT INTO `user` (name,email,password,avatar) VALUES(%s,%s,%s,%s)",
                (name, email, hashed_password, filename),
            )

            # thiếu commit thì dữ liệu KHÔNG vào bảng
            conn.commit()

            cur.close()
            conn.close()

            # redirect để F5 không gửi lại form, tránh đăng ký 2 lần
            return redirect("/login")

    # GET, hoặc POST còn lỗi: trả form kèm lỗi
    # Gửi lại name, email để điền sẵn, người dùng khỏi gõ lại; không gửi password vì lý do bảo mật
    return render_template("register.html", errors=errors, name=name, email=email)
