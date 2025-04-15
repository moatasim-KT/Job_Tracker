from flask import Blueprint, render_template, request, redirect, url_for, flash
from job_tracker.models import Job, Note, Contact
from job_tracker import db
from datetime import datetime
import json

job = Blueprint('job', __name__)

@job.route('/jobs')
def list_jobs():
    """List all jobs."""
    status_filter = request.args.get('status', None)
    
    if status_filter and status_filter != 'All':
        jobs = Job.query.filter_by(status=status_filter).order_by(Job.date_added.desc()).all()
    else:
        jobs = Job.query.order_by(Job.date_added.desc()).all()
    
    return render_template('jobs/list.html', jobs=jobs, current_status=status_filter or 'All')

@job.route('/jobs/add', methods=['GET', 'POST'])
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
            return redirect(url_for('job.add_job'))
        
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
        return redirect(url_for('job.view_job', job_id=job_instance.id))
    
    return render_template('jobs/add.html')

@job.route('/jobs/<int:job_id>')
def view_job(job_id):
    """View a specific job."""
    job_instance = Job.query.get_or_404(job_id)
    notes = Note.query.filter_by(job_id=job_id).order_by(Note.date_added.desc()).all()
    contacts = Contact.query.filter_by(job_id=job_id).all()
    
    # Convert parsed_data JSON string to Python dictionary
    if job_instance.parsed_data:
        try:
            job_instance.parsed_data = json.loads(job_instance.parsed_data)
            
            # Clean up text formatting issues
            if job_instance.parsed_data and 'sections' in job_instance.parsed_data:
                for section in job_instance.parsed_data['sections']:
                    if section['type'] == 'paragraph' and isinstance(section['content'], str):
                        # Clean excessive whitespace and newlines
                        content = section['content'].strip()
                        content = content.replace('\n\n\n', '\n')
                        content = content.replace('\n\n', '\n')
                        
                        # Remove "show more/less" text and similar artifacts
                        content = content.replace('show more', '')
                        content = content.replace('show less', '')
                        content = content.replace('Show more', '')
                        content = content.replace('Show Less', '')
                        content = content.replace('...', '')
                        
                        section['content'] = content
                    
                    elif section['type'] == 'list' and isinstance(section['content'], list):
                        # Clean list items
                        cleaned_items = []
                        for item in section['content']:
                            if isinstance(item, str):
                                # Remove bullets, numbers and excessive whitespace
                                item = item.strip()
                                item = item.replace('show more', '')
                                item = item.replace('show less', '')
                                item = item.replace('Show more', '')
                                item = item.replace('Show Less', '')
                                item = item.replace('...', '')
                                
                                if item:  # Only add non-empty items
                                    cleaned_items.append(item)
                        
                        section['content'] = cleaned_items
        except (json.JSONDecodeError, TypeError):
            job_instance.parsed_data = None
    
    return render_template('jobs/view_with_tabs.html', job=job_instance, notes=notes, contacts=contacts)

@job.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('job.view_job', job_id=job_instance.id))
    
    return render_template('jobs/edit.html', job=job_instance)

@job.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete a job."""
    job_instance = Job.query.get_or_404(job_id)
    
    db.session.delete(job_instance)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@job.route('/jobs/<int:job_id>/add_note', methods=['POST'])
def add_note(job_id):
    """Add a note to a job."""
    job_instance = Job.query.get_or_404(job_id)
    note_content = request.form.get('note_content')
    
    if note_content:
        note = Note(content=note_content, job_id=job_instance.id)
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    
    return redirect(url_for('job.view_job', job_id=job_instance.id))

@job.route('/jobs/<int:job_id>/add_contact', methods=['POST'])
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
    
    return redirect(url_for('job.view_job', job_id=job_instance.id))

@job.route('/jobs/<int:job_id>/update_status', methods=['POST'])
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
