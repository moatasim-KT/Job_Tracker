"""
Main routes for the application.
"""

from flask import Blueprint, render_template, json, redirect, url_for
from job_tracker.models import Job
from job_tracker import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page route that redirects to the dashboard."""
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
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
