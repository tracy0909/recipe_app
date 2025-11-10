from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from recipes import recipes_bp


# 藍圖
from auth.routes import auth_bp
from routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(recipes_bp, url_prefix="/recipes")  

    return app


# 讓 flask CLI 可以找到 app
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

