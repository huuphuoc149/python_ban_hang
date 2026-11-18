from flask import Flask, render_template, request, redirect
from routes.index import index_bp
from routes.register import register_bp
from routes.login import login_bp
from routes.logout import logout_bp
from routes.account import account_bp
from routes.my_product import my_product_bp
from routes.add_product import add_product_bp
from routes.edit_product import edit_product_bp
from routes.delete_product import delete_product_bp
from routes.add_to_cart import add_to_cart_bp
from routes.show_cart import show_cart_bp
from routes.update_cart import update_cart_bp

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.register_blueprint(index_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(account_bp)
app.register_blueprint(my_product_bp)
app.register_blueprint(add_product_bp)
app.register_blueprint(edit_product_bp)
app.register_blueprint(delete_product_bp)
app.register_blueprint(add_to_cart_bp)
app.register_blueprint(show_cart_bp)
app.register_blueprint(update_cart_bp)

if __name__ == "__main__":
    app.run(debug=True)
