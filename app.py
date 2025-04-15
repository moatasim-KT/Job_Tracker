from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Add context processor to inject current UTC datetime as 'now'
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

from job_tracker.models import Job, Note, Contact

# Import route modules
from routes.job_routes import job
from routes.parser_routes import parser
from routes.main_routes import main
from routes.company_routes import company

# Register blueprints
app.register_blueprint(job, url_prefix='/jobs')
app.register_blueprint(parser, url_prefix='/parser')
app.register_blueprint(main)
app.register_blueprint(company, url_prefix='/company')

@app.route('/')
def index():
    """Home page route that shows job listings."""
    jobs = Job.query.order_by(Job.date_added.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/dashboard')
def dashboard():
    """Dashboard with statistics and overview."""
    total_jobs = Job.query.count()
    applied_jobs = Job.query.filter_by(status='Applied').count()
    interview_jobs = Job.query.filter(
        (Job.status == 'Phone Interview') | 
        (Job.status == 'Technical Interview') | 
        (Job.status == 'Onsite Interview')
    ).count()
    offers = Job.query.filter_by(status='Offer').count()
    rejected = Job.query.filter_by(status='Rejected').count()
    
    status_data = {
        'labels': ['Applied', 'Interview', 'Offer', 'Rejected', 'Saved'],
        'data': [
            applied_jobs,
            interview_jobs,
            offers,
            rejected,
            total_jobs - (applied_jobs + interview_jobs + offers + rejected)
        ]
    }
    
    return render_template('dashboard.html', 
                          total_jobs=total_jobs,
                          applied=applied_jobs,
                          interviews=interview_jobs,
                          offers=offers,
                          rejected=rejected,
                          status_data=json.dumps(status_data))

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
