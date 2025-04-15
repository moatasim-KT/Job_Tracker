from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, Job, Note, Contact
from datetime import datetime

job_routes = Blueprint('job_routes', __name__)

@job_routes.route('/jobs')
def list_jobs():
    """List all jobs."""
    status_filter = request.args.get('status', None)
    
    if status_filter and status_filter != 'All':
        jobs = Job.query.filter_by(status=status_filter).order_by(Job.date_added.desc()).all()
    else:
        jobs = Job.query.order_by(Job.date_added.desc()).all()
    
    return render_template('jobs/list.html', jobs=jobs, current_status=status_filter or 'All')

@job_routes.route('/jobs/add', methods=['GET', 'POST'])
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
            return redirect(url_for('job_routes.add_job'))
        
        job = Job(
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
                job.date_applied = datetime.strptime(date_applied, '%Y-%m-%d')
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job added successfully!', 'success')
        return redirect(url_for('job_routes.view_job', job_id=job.id))
    
    return render_template('jobs/add.html')

@job_routes.route('/jobs/<int:job_id>')
def view_job(job_id):
    """View a specific job."""
    job = Job.query.get_or_404(job_id)
    notes = Note.query.filter_by(job_id=job_id).order_by(Note.date_added.desc()).all()
    contacts = Contact.query.filter_by(job_id=job_id).all()
    
    return render_template('jobs/view.html', job=job, notes=notes, contacts=contacts)

@job_routes.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    """Edit a job."""
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.location = request.form.get('location')
        job.description = request.form.get('description')
        job.url = request.form.get('url')
        job.salary = request.form.get('salary')
        job.job_type = request.form.get('job_type')
        new_status = request.form.get('status')
        
        # If status changed to Applied and no date_applied set, set it to now
        if new_status == 'Applied' and job.status != 'Applied' and not job.date_applied:
            job.date_applied = datetime.utcnow()
        
        job.status = new_status
        
        # Update date_applied if provided
        date_applied = request.form.get('date_applied')
        if date_applied:
            job.date_applied = datetime.strptime(date_applied, '%Y-%m-%d')
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('job_routes.view_job', job_id=job.id))
    
    return render_template('jobs/edit.html', job=job)

@job_routes.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete a job."""
    job = Job.query.get_or_404(job_id)
    
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('index'))

@job_routes.route('/jobs/<int:job_id>/add_note', methods=['POST'])
def add_note(job_id):
    """Add a note to a job."""
    job = Job.query.get_or_404(job_id)
    note_content = request.form.get('note_content')
    
    if note_content:
        note = Note(content=note_content, job_id=job.id)
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    
    return redirect(url_for('job_routes.view_job', job_id=job.id))

@job_routes.route('/jobs/<int:job_id>/add_contact', methods=['POST'])
def add_contact(job_id):
    """Add a contact to a job."""
    job = Job.query.get_or_404(job_id)
    
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
            job_id=job.id
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
    
    return redirect(url_for('job_routes.view_job', job_id=job.id))

@job_routes.route('/jobs/<int:job_id>/update_status', methods=['POST'])
def update_status(job_id):
    """Quick update of job status."""
    job = Job.query.get_or_404(job_id)
    new_status = request.form.get('status')
    
    if new_status:
        # If changing to Applied and no date_applied, set it to now
        if new_status == 'Applied' and job.status != 'Applied' and not job.date_applied:
            job.date_applied = datetime.utcnow()
            
        job.status = new_status
        db.session.commit()
        flash(f'Status updated to {new_status}!', 'success')
    
    return redirect(request.referrer or url_for('index'))
