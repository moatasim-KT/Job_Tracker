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

# Define models here to avoid circular imports
class Job(db.Model):
    """Model for job listings."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    salary = db.Column(db.String(100))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    date_posted = db.Column(db.DateTime)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Saved')  # Saved, Applied, Interview, Offer, Rejected
    date_applied = db.Column(db.DateTime)
    notes = db.relationship('Note', backref='job', lazy=True, cascade="all, delete-orphan")
    contacts = db.relationship('Contact', backref='job', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'
        
class Note(db.Model):
    """Model for notes related to job applications."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    
    def __repr__(self):
        return f'<Note {self.id} for Job {self.job_id}>'

class Contact(db.Model):
    """Model for contacts related to job applications."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    linkedin = db.Column(db.String(200))
    notes = db.Column(db.Text)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    
    def __repr__(self):
        return f'<Contact {self.name} for Job {self.job_id}>'

# Import route modules
from routes.job_routes import job_routes
from routes.parser_routes import parser_routes

# Register blueprints
app.register_blueprint(job_routes)
app.register_blueprint(parser_routes)

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
