"""
Main routes for the application.
"""

from flask import Blueprint, render_template, json, redirect, url_for
from job_tracker.models import Job
from job_tracker import db
from job_tracker.routes.cv_routes import cv_bp
from job_tracker.routes.cover_letter_routes import cover_letter_bp
from job_tracker.routes.document_routes import document_bp
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route that redirects to the dashboard."""
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
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
    
    # List uploaded cover letters and other docs
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
    cover_letters_dir = os.path.join(uploads_dir, 'cover_letters')
    other_docs_dir = os.path.join(uploads_dir, 'other_docs')
    cover_letters = os.listdir(cover_letters_dir) if os.path.exists(cover_letters_dir) else []
    other_docs = os.listdir(other_docs_dir) if os.path.exists(other_docs_dir) else []
    
    return render_template('dashboard.html', 
                          total_jobs=total_jobs,
                          applied=applied_jobs,
                          interviews=interview_jobs,
                          offers=offers,
                          rejected=rejected,
                          status_data=json.dumps(status_data),
                          cover_letters=cover_letters,
                          other_docs=other_docs)

# db.create_all()  # Removed: should be called inside app context in app factory
# Blueprint registration removed; handled in create_app()
