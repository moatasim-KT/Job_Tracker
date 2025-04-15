from datetime import datetime
from job_tracker import db

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
    parsed_data = db.Column(db.Text)  # JSON string with structured job description data
    company_data = db.Column(db.Text)  # JSON string with structured company information
    company_reviews = db.Column(db.Text)  # JSON string with structured company reviews
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

class CompanySource(db.Model):
    """Model for tracking company information sources."""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    linkedin_url = db.Column(db.String(500))
    website_url = db.Column(db.String(500))
    glassdoor_url = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanySource {self.company_name}>'
