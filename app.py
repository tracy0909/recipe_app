from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from recipes import recipes_bp

# 藍圖
from auth.routes import auth_bp
from routes import main_bp

import os  # ADD


def create_app():
    app = Flask(__name__)

    # CHANGE: 先載入原本的 Config 設定
    app.config.from_object(Config)

    # CHANGE: 如果有設定 DATABASE_URL（例如在 Render 上），就覆寫資料庫連線字串
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    return app


# 讓 flask CLI / gunicorn 可以找到 app
app = create_app()

if __name__ == "__main__":
    # CHANGE: 本機開發時用這個啟動，Render 會用 gunicorn app:app
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True,
    )
