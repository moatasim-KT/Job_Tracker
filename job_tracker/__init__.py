from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import jinja2
from markupsafe import Markup

# Initialize extensions
db = SQLAlchemy()

def create_app():
    """Application factory function"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = '../uploads'
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database with app
    db.init_app(app)
    
    # Import and register blueprints
    from job_tracker.routes.main_routes import main_bp
    from job_tracker.routes.job_routes import job_bp
    from job_tracker.routes.parser_routes import parser_bp
    from job_tracker.routes.company_routes import company_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(parser_bp, url_prefix='/parse')
    app.register_blueprint(company_bp, url_prefix='/company')
    
    # Add template context processor for global template variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Add custom template filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if text:
            return Markup(text.replace('\n', '<br>'))
        return ''
    
    return app
