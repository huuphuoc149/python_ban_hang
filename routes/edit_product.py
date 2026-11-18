from flask import Blueprint, render_template, request, redirect, session
from db import get_connection
import os
from flask import current_app  # trỏ tới app đang chạy, để lấy root_path (thư mục dự án)
from werkzeug.utils import secure_filename

edit_product_bp = Blueprint("edit_product", __name__)

ALLOWED_EXTENSION = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 1


def allowed_file(filename):
    # Phải có dấu "." mới có đuôi file
    # rsplit(".",1): tách 1 lần từ bên phải, để "a.b.jpg" vẫn lấy đúng "jpg"
    # lower(): "PNG" & "png" đều hợp lệ
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION


def handle_file_upload(file):
    # Trả về dict để nơi gọi biết vừa thành công hay thất bại, vừa có câu báo lỗi
    result = {"success": False, "error": None}

    # Không chọn file thì trình duyệt vẫn gửi lên, nhưng tên rỗng
    if file.filename == "":
        result["error"] = "Vui lòng chọn 1 file"
        return result
    if not allowed_file(file.filename):
        result["error"] = "Chỉ chấp nhận file ảnh [PNG,JPG,JPEG,GIF]"
        return result

    file.seek(0, os.SEEK_END)  # đưa con trỏ về CUỐI file
    file_size = file.tell()  # vị trí con trỏ lúc này = dung lượng file (byte)
    file.seek(0)  # đưa con trỏ trở về ĐẦU file, thiếu dòng này thì save() ra file rỗng

    # 1MB = 1024 * 1024 byte, dùng ">=" vì yêu cầu NHỎ HƠN 1MB (đúng 1MB cũng bị chặn)
    if file_size >= MAX_FILE_SIZE_MB * 1024 * 1024:
        result["error"] = "File quá lớn ! Chỉ được phép tối đa 1MB"
        return result

    result["success"] = True
    return result


@edit_product_bp.route("/edit_product/<id>", methods=["GET", "POST"])
def edit_product(id):
    # Chặn truy cập nếu chưa LOGIN
    if not session.get("user_id"):
        return redirect("/login")
    errors = {}

    # Kết nối database
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM product WHERE id = %s AND id_user = %s",
        (
            id,
            session["user_id"],
        ),
    )
    product = cur.fetchone()

    cur.close()
    conn.close()

    if not product:
        return redirect("/my_product")

    # Nếu user bấm UPDATE
    if request.method == "POST":
        # Lây data từ form
        # strip(): bỏ khoảng trắng 2 đầu, chỉ gõ dấu cách cũng tính là trống
        title = request.form["title"].strip()
        price = request.form["price"].strip()
        image = request.files["image"]

        if not title:
            errors["title"] = "Vui lòng nhập tên sản phẩm"
        if not price:
            errors["price"] = "Vui lòng nhập giá"

        # ẢNH kh bắt buộc : chỉ ktr khi user chọn file
        if image.filename != "":
            upload_result = handle_file_upload(image)
            if not upload_result["success"]:
                errors["image"] = upload_result["error"]

        if not errors:
            conn = get_connection()
            cur = conn.cursor()

            # Đường dẫn tới static/uploads, chạy app ở thư mục nào cũng đúng
            UPLOAD_FOLDER = os.path.join(current_app.root_path, "static", "uploads")

            if image.filename != "":  # Chỉ lưu khi khi có chọn file
                # Chưa có thư mục nào thì tạo, tránh lỗi khi save
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                filename = secure_filename(image.filename)

                # ảnh lưu vào thư mục, database chỉ lưu tên file
                image.save(os.path.join(UPLOAD_FOLDER, filename))

                cur.execute(
                    "UPDATE product SET title = %s,price = %s, image = %s WHERE id =%s AND id_user = %s",
                    (
                        title,
                        price,
                        filename,
                        id,
                        session["user_id"],
                    ),
                )
            else:
                cur.execute(
                    "UPDATE product SET title = %s,price =%s WHERE id = %s AND id_user =%s",
                    (title, price, id, session["user_id"]),
                )

            # thiếu COMMIT thì data KHÔNG vào bảng
            conn.commit()

            cur.close()
            conn.close()

            return redirect("/my_product")

    return render_template("edit_product.html", errors=errors, product=product)
