from flask import Blueprint, render_template, request, redirect, url_for, flash
from job_tracker.models import Job, Note, Contact
from job_tracker import db
from datetime import datetime
import json

job_bp = Blueprint('job', __name__)

@job_bp.route('/jobs')
def list_jobs():
    """List all jobs."""
    status_filter = request.args.get('status', None)
    
    if status_filter and status_filter != 'All':
        jobs = Job.query.filter_by(status=status_filter).order_by(Job.date_added.desc()).all()
    else:
        jobs = Job.query.order_by(Job.date_added.desc()).all()
    
    return render_template('jobs/list.html', jobs=jobs, current_status=status_filter or 'All')

@job_bp.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    """Add a new job manually."""
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')
        url = request.form.get('url')
        salary = request.form.get('salary')
        job_type = request.form.get('job_type')
        status = request.form.get('status', 'Saved')
        
        if not title or not company:
            flash('Job title and company are required!', 'danger')
            return redirect(url_for('job_bp.add_job'))
        
        job_instance = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            url=url,
            salary=salary,
            job_type=job_type,
            status=status,
            date_added=datetime.utcnow()
        )
        
        # Handle date_applied if status is Applied or beyond
        if status in ['Applied', 'Phone Interview', 'Technical Interview', 'Onsite Interview', 'Offer', 'Rejected']:
            date_applied = request.form.get('date_applied')
            if date_applied:
                job_instance.date_applied = datetime.strptime(date_applied, '%Y-%m-%d')
        
        db.session.add(job_instance)
        db.session.commit()
        
        flash('Job added successfully!', 'success')
        return redirect(url_for('job_bp.view_job', job_id=job_instance.id))
    
    return render_template('jobs/add.html')


def _parse_job_data(job_data):
    """
    Parse JSON string into Python dictionary.
    
    Args:
        job_data: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    if not job_data:
        return None
        
    try:
        return json.loads(job_data)
    except (json.JSONDecodeError, TypeError):
        return None


def _clean_text_content(content):
    """
    Clean text content by removing artifacts and excessive whitespace.
    
    Args:
        content: String content to clean
        
    Returns:
        Cleaned string content
    """
    if not isinstance(content, str):
        return content
        
    # Clean excessive whitespace and newlines
    content = content.strip()
    content = content.replace('\n\n\n', '\n').replace('\n\n', '\n')
    
    # Remove "show more/less" text and similar artifacts
    artifacts = ['show more', 'show less', 'Show more', 'Show less', '...']
    for artifact in artifacts:
        content = content.replace(artifact, '')
        
    return content


def _clean_list_items(items):
    """
    Clean a list of text items.
    
    Args:
        items: List of string items to clean
        
    Returns:
        List of cleaned string items
    """
    cleaned_items = []
    
    for item in items:
        if isinstance(item, str) and (clean_item := _clean_text_content(item)):
            cleaned_items.append(clean_item)
            
    return cleaned_items


def _process_parsed_sections(sections):
    """
    Process and clean sections from parsed job data.
    
    Args:
        sections: List of section dictionaries
        
    Returns:
        Processed sections with cleaned content
    """
    if not sections:
        return sections
        
    for section in sections:
        if section['type'] == 'paragraph' and isinstance(section['content'], str):
            section['content'] = _clean_text_content(section['content'])
        elif section['type'] == 'list' and isinstance(section['content'], list):
            section['content'] = _clean_list_items(section['content'])
            
    return sections


def _prepare_job_parsed_data(job):
    """
    Process and prepare job's parsed data for display.
    
    Args:
        job: Job object with potential parsed_data
        
    Returns:
        Job object with processed parsed_data
    """
    # Skip processing if no parsed data exists
    if not (parsed_data := _parse_job_data(job.parsed_data)):
        return job
        
    job.parsed_data = parsed_data
    
    # Process sections if they exist
    if 'sections' in parsed_data:
        job.parsed_data['sections'] = _process_parsed_sections(parsed_data['sections'])
        
    return job

def _get_job_related_data(job_id):
    """
    Fetch notes and contacts related to a specific job.
    
    Args:
        job_id: ID of the job to get related data for
        
    Returns:
        Tuple containing (notes, contacts)
    """
    notes = Note.query.filter_by(job_id=job_id).order_by(Note.date_added.desc()).all()
    contacts = Contact.query.filter_by(job_id=job_id).all()
    return notes, contacts

@job_bp.route('/jobs/<int:job_id>')
def view_job(job_id):
    """
    View a specific job with its notes and contacts.
    
    Retrieves job details, associated notes and contacts, and processes
    any parsed job description data for display.
    
    Args:
        job_id: ID of the job to view
        
    Returns:
        Rendered template with job, notes, and contacts
    """
    # Get job by ID and process its parsed data in one step
    job = Job.query.get_or_404(job_id)
        
    # Get related data
    notes, contacts = _get_job_related_data(job_id)
    
    # Process any parsed data the job might have
    job = _prepare_job_parsed_data(job)
    
    return render_template(
        'jobs/view_with_tabs.html', 
        job=job, 
        notes=notes, 
        contacts=contacts
    )

@job_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    """Edit a job."""
    job_instance = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        job_instance.title = request.form.get('title')
        job_instance.company = request.form.get('company')
        job_instance.location = request.form.get('location')
        job_instance.description = request.form.get('description')
        job_instance.url = request.form.get('url')
        job_instance.salary = request.form.get('salary')
        job_instance.job_type = request.form.get('job_type')
        new_status = request.form.get('status')
        
        # If status changed to Applied and no date_applied set, set it to now
        if new_status == 'Applied' and job_instance.status != 'Applied' and not job_instance.date_applied:
            job_instance.date_applied = datetime.utcnow()
        
        job_instance.status = new_status
        
        # Update date_applied if provided
        date_applied = request.form.get('date_applied')
        if date_applied:
            job_instance.date_applied = datetime.strptime(date_applied, '%Y-%m-%d')
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('job_bp.view_job', job_id=job_instance.id))
    
    return render_template('jobs/edit.html', job=job_instance)

@job_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete a job."""
    job_instance = Job.query.get_or_404(job_id)
    
    db.session.delete(job_instance)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@job_bp.route('/jobs/<int:job_id>/add_note', methods=['POST'])
def add_note(job_id):
    """Add a note to a job."""
    job_instance = Job.query.get_or_404(job_id)
    note_content = request.form.get('note_content')
    
    if note_content:
        note = Note(content=note_content, job_id=job_instance.id)
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    
    return redirect(url_for('job_bp.view_job', job_id=job_instance.id))

@job_bp.route('/jobs/<int:job_id>/add_contact', methods=['POST'])
def add_contact(job_id):
    """Add a contact to a job."""
    job_instance = Job.query.get_or_404(job_id)
    
    name = request.form.get('contact_name')
    title = request.form.get('contact_title')
    email = request.form.get('contact_email')
    phone = request.form.get('contact_phone')
    linkedin = request.form.get('contact_linkedin')
    notes = request.form.get('contact_notes')
    
    if name:
        contact = Contact(
            name=name,
            title=title,
            email=email,
            phone=phone,
            linkedin=linkedin,
            notes=notes,
            job_id=job_instance.id
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
    
    return redirect(url_for('job_bp.view_job', job_id=job_instance.id))

@job_bp.route('/jobs/<int:job_id>/update_status', methods=['POST'])
def update_status(job_id):
    """Quick update of job status."""
    job_instance = Job.query.get_or_404(job_id)
    new_status = request.form.get('status')
    
    if new_status:
        # If changing to Applied and no date_applied, set it to now
        if new_status == 'Applied' and job_instance.status != 'Applied' and not job_instance.date_applied:
            job_instance.date_applied = datetime.utcnow()
            
        job_instance.status = new_status
        db.session.commit()
        flash(f'Status updated to {new_status}!', 'success')
    
    return redirect(request.referrer or url_for('main.dashboard'))
