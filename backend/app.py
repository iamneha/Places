"""Create the flask app and set the configurations."""
import os

from flask import Flask, redirect, url_for
from flask_cors import CORS

from backend.models.database import db
from backend.config import POSTGRES_CONN

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_CONN
app.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app)
db.init_app(app)


def create_app(*args, **kwargs):
    """Register api routes and initialize app, database schemas."""
    from backend.api.api_v1 import API_V1

    app.debug = os.getenv("DEBUG", "false") == "true"

    SWAGGER_DOC = "api_v1.doc"

    app.register_blueprint(API_V1)

    with app.app_context():
        db.create_all()

    @app.route("/")
    @app.route("/spec")
    def index():
        return redirect(url_for(SWAGGER_DOC))

    return app
