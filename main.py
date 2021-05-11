import os

from flask import Flask, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api.login import blueprint as login_blueprint
from api.odoo import blueprint as odoo_blueprint

app = Flask(__name__)
ALLOW_ALL_ORIGINS = os.getenv("ALLOW_ALL_ORIGINS")
if ALLOW_ALL_ORIGINS:
    CORS(app)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

app.register_blueprint(login_blueprint)
app.register_blueprint(odoo_blueprint)


@app.route("/api/ping")
def ping():
    return jsonify({"name": "auto-conso", "status": "ok"})


@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, "index.html")
    return send_file(index_path)


# Everything not declared before (not a Flask route / API endpoint)...
@app.route("/<path:path>")
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # ...or should be handled by the SPA's "router" in front end
    else:
        index_path = os.path.join(app.static_folder, "index.html")
        return send_file(index_path)


if __name__ == "__main__":
    app.run(debug=True)
