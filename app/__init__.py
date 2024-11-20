from flask import Flask, abort,request
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from flask_bcrypt import Bcrypt
from .utilities.response_utils import response_handler
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

db = SQLAlchemy()
bcrypt = Bcrypt()
load_dotenv()

def create_app():
    app = Flask(__name__)
    print(config.SQLALCHEMY_DATABASE_URI)
    app.config.from_object(config)

    db.init_app(app)
    bcrypt.init_app(app)

    # Database checkpoint
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        if not database_exists(engine.url):
            create_database(engine.url)
        from .models import user_model, image_model, verification_model
        db.create_all()
        
    @app.before_request
    def limit_http_methods():
        if request.method in ['OPTIONS', 'HEAD']:
            return response_handler(405)
        
    # Health check route
    from app.routes.health_check_route import health_bp
    app.register_blueprint(health_bp, url_prefix='/')
        
    # User route
    from app.routes.user_route import user_bp
    app.register_blueprint(user_bp, url_prefix='/v1/')
    
    from app.routes.user_route import verify_bp
    app.register_blueprint(verify_bp, url_prefix='/')
    
    # Login user route
    from app.routes.login_user_route import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/') 
    
    # Image route
    from app.routes.image_route import profile_picture_bp
    app.register_blueprint(profile_picture_bp, url_prefix='/')

    # Error handling
    @app.errorhandler(404)
    def page_not_found_error(e):
        return response_handler(404) 

    @app.errorhandler(400)
    def bad_request_error(e):
        return response_handler(400)

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        return response_handler(405)
    
    @app.errorhandler(415)
    def method_not_allowed_error(e):
        return response_handler(400)

    return app