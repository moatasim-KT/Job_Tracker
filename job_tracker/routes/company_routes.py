"""
Routes for company information handling.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
from job_tracker import db
from job_tracker.models import Job, CompanySource
from job_tracker.utils.company_parser import CompanyInfoParser
from job_tracker.utils.url_discovery import URLDiscovery

# Create blueprint
company = Blueprint('company', __name__)

@company.route('/job/<int:job_id>/company', methods=['GET'])
def view_company_info(job_id):
    """Route to view company information for a specific job."""
    job = Job.query.get_or_404(job_id)
    
    # Check if we need to fetch company information automatically
    company_source = CompanySource.query.filter_by(company_name=job.company).first()
    
    # If we don't have company source information yet, try to discover URLs automatically
    if not company_source or not (company_source.website_url or company_source.linkedin_url or company_source.glassdoor_url):
        try:
            # Discover URLs for this company
            discovered_urls = URLDiscovery.discover_company_urls(job.company)
            
            # Create or update the company source record
            if not company_source:
                company_source = CompanySource(company_name=job.company)
                db.session.add(company_source)
            
            # Update with discovered URLs
            if discovered_urls.get('website_url') and not company_source.website_url:
                company_source.website_url = discovered_urls.get('website_url')
            
            if discovered_urls.get('linkedin_url') and not company_source.linkedin_url:
                company_source.linkedin_url = discovered_urls.get('linkedin_url')
            
            if discovered_urls.get('glassdoor_url') and not company_source.glassdoor_url:
                company_source.glassdoor_url = discovered_urls.get('glassdoor_url')
            
            db.session.commit()
            
            # If we discovered URLs, try to fetch company information automatically
            auto_fetch = False
            if (discovered_urls.get('website_url') or discovered_urls.get('linkedin_url')) and not job.company_data:
                try:
                    # Fetch and parse company information
                    company_data = CompanyInfoParser.fetch_company_data(
                        job.company, 
                        website_url=discovered_urls.get('website_url'), 
                        linkedin_url=discovered_urls.get('linkedin_url')
                    )
                    
                    # Update the job record with the company data
                    job.company_data = json.dumps(company_data)
                    db.session.commit()
                    auto_fetch = True
                except Exception as e:
                    print(f"Error auto-fetching company information: {str(e)}")
            
            # If we discovered a Glassdoor URL, try to fetch reviews automatically
            if discovered_urls.get('glassdoor_url') and not job.company_reviews:
                try:
                    # Fetch and parse company reviews
                    company_reviews = CompanyInfoParser.fetch_company_reviews(
                        job.company,
                        glassdoor_url=discovered_urls.get('glassdoor_url')
                    )
                    
                    # Update the job record with the company reviews
                    job.company_reviews = json.dumps(company_reviews)
                    db.session.commit()
                    auto_fetch = True
                except Exception as e:
                    print(f"Error auto-fetching company reviews: {str(e)}")
            
            if auto_fetch:
                flash("Company information and reviews were automatically fetched!", "success")
            else:
                flash("We've automatically found sources for this company!", "info")
                
        except Exception as e:
            flash(f"Error discovering company URLs: {str(e)}", "warning")
    
    # Get company data if it exists, otherwise return empty dict
    company_data = {}
    if job.company_data:
        try:
            company_data = json.loads(job.company_data)
        except json.JSONDecodeError:
            flash("Error loading company data", "danger")
    
    # Get company reviews if they exist, otherwise return empty dict
    company_reviews = {}
    if job.company_reviews:
        try:
            company_reviews = json.loads(job.company_reviews)
        except json.JSONDecodeError:
            flash("Error loading company reviews", "danger")
    
    return render_template('jobs/company_info.html', 
                          job=job,
                          company_data=company_data,
                          company_reviews=company_reviews,
                          company_source=company_source)

@company.route('/job/<int:job_id>/company/update', methods=['POST'])
def update_company_info(job_id):
    """Route to update company information for a specific job."""
    job = Job.query.get_or_404(job_id)
    
    # Check if we should try to auto-discover URLs
    auto_discover = request.form.get('auto_discover') == 'true'
    
    if auto_discover:
        try:
            # Discover URLs for this company
            discovered_urls = URLDiscovery.discover_company_urls(job.company)
            
            # Create or update the company source record
            company_source = CompanySource.query.filter_by(company_name=job.company).first()
            if not company_source:
                company_source = CompanySource(company_name=job.company)
                db.session.add(company_source)
            
            # Update with discovered URLs (only if they don't already exist)
            if discovered_urls.get('website_url') and not company_source.website_url:
                company_source.website_url = discovered_urls.get('website_url')
            
            if discovered_urls.get('linkedin_url') and not company_source.linkedin_url:
                company_source.linkedin_url = discovered_urls.get('linkedin_url')
            
            if discovered_urls.get('glassdoor_url') and not company_source.glassdoor_url:
                company_source.glassdoor_url = discovered_urls.get('glassdoor_url')
                
            db.session.commit()
            
            flash("URLs discovered successfully!", "success")
        except Exception as e:
            flash(f"Error discovering URLs: {str(e)}", "danger")
    else:
        # Manual update - Get form data
        website_url = request.form.get('website_url', '')
        linkedin_url = request.form.get('linkedin_url', '')
        glassdoor_url = request.form.get('glassdoor_url', '')
        
        # Create or update the company source record
        company_source = CompanySource.query.filter_by(company_name=job.company).first()
        if not company_source:
            company_source = CompanySource(company_name=job.company)
            db.session.add(company_source)
        
        # Update URLs
        if website_url:
            company_source.website_url = website_url
        if linkedin_url:
            company_source.linkedin_url = linkedin_url
        if glassdoor_url:
            company_source.glassdoor_url = glassdoor_url
        
        db.session.commit()
    
    # Get the updated company source
    company_source = CompanySource.query.filter_by(company_name=job.company).first()
    
    # Fetch and parse company information if we have sources
    if company_source and (company_source.website_url or company_source.linkedin_url):
        try:
            # Fetch and parse company information
            company_data = CompanyInfoParser.fetch_company_data(
                job.company, 
                website_url=company_source.website_url, 
                linkedin_url=company_source.linkedin_url
            )
            
            # Update the job record with the company data
            job.company_data = json.dumps(company_data)
            db.session.commit()
            
            flash("Company information updated successfully", "success")
        except Exception as e:
            flash(f"Error fetching company information: {str(e)}", "danger")
    
    # Fetch and parse company reviews if we have a Glassdoor URL
    if company_source and company_source.glassdoor_url:
        try:
            # Fetch and parse company reviews
            company_reviews = CompanyInfoParser.fetch_company_reviews(
                job.company,
                glassdoor_url=company_source.glassdoor_url
            )
            
            # Update the job record with the company reviews
            job.company_reviews = json.dumps(company_reviews)
            db.session.commit()
            
            flash("Company reviews updated successfully", "success")
        except Exception as e:
            flash(f"Error fetching company reviews: {str(e)}", "danger")
    
    return redirect(url_for('company.view_company_info', job_id=job_id))

@company.route('/job/<int:job_id>', methods=['GET'])
def api_get_company_info(job_id):
    """API endpoint to get company information for a specific job."""
    job = Job.query.get_or_404(job_id)
    
    # Get company data if it exists
    company_data = {}
    if job.company_data:
        try:
            company_data = json.loads(job.company_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Error parsing company data"}), 500
    
    # Get company reviews if they exist
    company_reviews = {}
    if job.company_reviews:
        try:
            company_reviews = json.loads(job.company_reviews)
        except json.JSONDecodeError:
            return jsonify({"error": "Error parsing company reviews"}), 500
    
    return jsonify({
        "company_name": job.company,
        "company_data": company_data,
        "company_reviews": company_reviews
    })
