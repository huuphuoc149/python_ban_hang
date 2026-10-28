from flask import Flask, render_template, request, redirect
from routes.index import index_bp
from routes.register import register_bp
from routes.login import login_bp

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.register_blueprint(index_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

if __name__ == "__main__":
    app.run(debug=True)
