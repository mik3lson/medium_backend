from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from extensions import db, bcrypt, jwt
from config import Config
import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import Blueprints
    from auth.routes import auth_bp
    from users.routes import users_bp
    from posts.routes import posts_bp
    from replies.routes import replies_bp

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(replies_bp, url_prefix="/replies")

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)