from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db, Job, Note
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import html2text
import json
import os

parser_routes = Blueprint('parser_routes', __name__)

@parser_routes.route('/parse/url', methods=['GET', 'POST'])
def parse_url():
    """Parse job details from a LinkedIn URL."""
    if request.method == 'POST':
        url = request.form.get('job_url')
        
        if not url:
            flash('Please provide a URL', 'danger')
            return redirect(url_for('parser_routes.parse_url'))
            
        try:
            job_data = extract_from_linkedin(url)
            
            if job_data:
                # Check if job already exists with this URL
                existing_job = Job.query.filter_by(url=url).first()
                if existing_job:
                    flash('This job is already in your tracker!', 'warning')
                    return redirect(url_for('job_routes.view_job', job_id=existing_job.id))
                
                # Create new job
                return render_template('parser/confirm.html', job_data=job_data, url=url)
            else:
                flash('Could not extract job details from this URL. Try copy-pasting the job description instead.', 'danger')
        except Exception as e:
            flash(f'Error parsing URL: {str(e)}', 'danger')
        
        return redirect(url_for('parser_routes.parse_url'))
    
    return render_template('parser/url_form.html')

@parser_routes.route('/parse/text', methods=['GET', 'POST'])
def parse_text():
    """Parse job details from pasted text or uploaded document."""
    if request.method == 'POST':
        job_text = request.form.get('job_text')
        
        if not job_text:
            flash('Please provide job description text', 'danger')
            return redirect(url_for('parser_routes.parse_text'))
        
        try:
            job_data = extract_from_text(job_text)
            
            if job_data:
                return render_template('parser/confirm.html', job_data=job_data)
            else:
                flash('Could not extract enough job details from text. Please fill in the form manually.', 'warning')
                # Pre-fill what we could extract
                return redirect(url_for('job_routes.add_job'))
        except Exception as e:
            flash(f'Error parsing text: {str(e)}', 'danger')
            return redirect(url_for('parser_routes.parse_text'))
    
    return render_template('parser/text_form.html')

@parser_routes.route('/parse/confirm', methods=['POST'])
def confirm_parsed_job():
    """Save parsed job information after user confirmation."""
    title = request.form.get('title')
    company = request.form.get('company')
    location = request.form.get('location')
    description = request.form.get('description')
    url = request.form.get('url')
    salary = request.form.get('salary')
    job_type = request.form.get('job_type')
    
    if not title or not company:
        flash('Job title and company are required!', 'danger')
        return redirect(url_for('job_routes.add_job'))
    
    # Create job
    job = Job(
        title=title,
        company=company,
        location=location,
        description=description,
        url=url,
        salary=salary,
        job_type=job_type,
        status='Saved',
        date_added=datetime.utcnow()
    )
    
    db.session.add(job)
    db.session.commit()
    
    flash('Job added successfully!', 'success')
    return redirect(url_for('job_routes.view_job', job_id=job.id))

def extract_from_linkedin(url):
    """Extract job details from a LinkedIn job posting URL."""
    # This is a simplified version and may need adjustments based on LinkedIn's structure
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract job details - these selectors may need updating based on LinkedIn's current HTML structure
        title = soup.select_one('h1.job-title') or soup.select_one('h1.topcard__title')
        title = title.text.strip() if title else None
        
        company = soup.select_one('a.company-name') or soup.select_one('a.topcard__org-name-link')
        company = company.text.strip() if company else None
        
        location = soup.select_one('span.job-location') or soup.select_one('span.topcard__flavor--bullet')
        location = location.text.strip() if location else None
        
        description_elem = soup.select_one('div.description__text') or soup.select_one('div.show-more-less-html__markup')
        description = description_elem.get_text(separator='\n').strip() if description_elem else None
        
        # Extract other details if available
        job_type = None
        salary = None
        
        # Look for employment type and salary info
        details = soup.select('li.job-criteria__item')
        for detail in details:
            header = detail.select_one('h3.job-criteria__subheader')
            if header and 'Employment type' in header.text:
                job_type = detail.select_one('span.job-criteria__text').text.strip()
            elif header and 'Salary' in header.text:
                salary = detail.select_one('span.job-criteria__text').text.strip()
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': salary,
            'job_type': job_type
        }
    except Exception as e:
        print(f"LinkedIn extraction error: {str(e)}")
        return None

def extract_from_text(text):
    """Extract job details from pasted text."""
    # Convert HTML to plain text if needed
    if '<' in text and '>' in text:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        text = converter.handle(text)
    
    # Basic extraction - in a real application, this would use NLP or more sophisticated techniques
    lines = text.split('\n')
    
    # Try to extract job title (often one of the first prominent lines)
    title = next((line.strip() for line in lines[:10] if len(line.strip()) > 0 and len(line.strip()) < 100), '')
    
    # Try to extract company
    company_patterns = [
        r'at\s+([A-Za-z0-9][\w\s&.,]+)',  # "Software Engineer at Company Name"
        r'([A-Za-z0-9][\w\s&.,]+?)\s+is\s+looking',  # "Company Name is looking for"
        r'Join\s+([A-Za-z0-9][\w\s&.,]+)',  # "Join Company Name"
        r'([A-Za-z0-9][\w\s&.,]+?)\s+(?:is hiring|has an opening)'  # "Company Name is hiring"
    ]
    
    company = None
    for pattern in company_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            company = matches.group(1).strip()
            break
    
    # Look for location
    location_patterns = [
        r'Location:?\s*([A-Za-z0-9][\w\s,.-]+?)(?:\n|$)',
        r'in\s+([A-Za-z][\w\s,.-]+?,\s*(?:[A-Za-z]{2}|[A-Za-z]+))(?:\s|$|,|\.|;)',
        r'(?:headquartered|based) in\s+([A-Za-z][\w\s,.-]+?)(?:\s|$|,|\.|;)'
    ]
    
    location = None
    for pattern in location_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            location = matches.group(1).strip()
            break
    
    # Look for job type
    job_type_patterns = [
        r'(Full[-\s]Time|Part[-\s]Time|Contract|Freelance|Temporary|Internship)',
        r'Employment Type:?\s*([A-Za-z][\w\s-]+?)(?:\n|$)'
    ]
    
    job_type = None
    for pattern in job_type_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            job_type = matches.group(1).strip()
            break
    
    # Look for salary
    salary_patterns = [
        r'(?:Salary|Compensation):?\s*([^\n]+?)(?:\n|$)',
        r'\$\s*\d+[kK]\s*-\s*\$\s*\d+[kK]',
        r'\$\s*\d{2,3},\d{3}\s*-\s*\$\s*\d{2,3},\d{3}',
        r'\$\d{2,3},\d{3}(?:\+\s*)?(?:annually|per year)?',
        r'\$\d{2,3}[kK](?:\+\s*)?(?:annually|per year)?'
    ]
    
    salary = None
    for pattern in salary_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            try:
                salary = matches.group(0).strip()
            except:
                salary = matches.group(1).strip()
            break
    
    return {
        'title': title,
        'company': company or '',
        'location': location or '',
        'description': text,
        'url': '',
        'salary': salary or '',
        'job_type': job_type or ''
    }
