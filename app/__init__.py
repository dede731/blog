from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .views import sitemap as sitemap_blueprint
    app.register_blueprint(sitemap_blueprint)

    return app