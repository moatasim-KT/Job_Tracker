"""
Test script to verify the job description parsing functionality with messy, real-world job descriptions.
"""

from job_tracker import create_app, db
from job_tracker.models import Job
from job_tracker.utils.llm_parser import JobDescriptionParser
import json
from datetime import datetime

# Sample messy job description that doesn't have clear section headers or consistent formatting
MESSY_JOB_DESCRIPTION = """
Senior Software Engineer
Location: Remote (US)
Salary: $120K - $170K DOE

ACME Tech Solutions is looking for talented engineers to join our growing team!

We're a fast-paced startup disrupting the widget industry with innovative cloud solutions.

- Founded in 2018
- Series B funding of $25M
- Growing 150% YoY

Join us!

The ideal candidate will help build out our scalable backend services and contribute to our core platform.

What you'll be working on:
Building RESTful APIs using Node.js and Express
Designing database schemas in MongoDB
Implementing real-time communication features using WebSockets
Optimizing application performance and scalability
Creating automated testing frameworks
Contributing to architecture decisions
Mentoring junior developers
Participating in code reviews

We need someone who has:
5+ years experience with JavaScript/TypeScript
3+ years working with Node.js in production environments
Strong understanding of asynchronous programming
Experience with MongoDB or similar NoSQL databases
Knowledge of microservice architecture patterns
Familiarity with containerization (Docker, Kubernetes)
Excellent problem-solving skills
Good communication and collaboration abilities

Bonus points if you have:
Experience with GraphQL
Knowledge of AWS services
Familiarity with CI/CD pipelines
Open source contributions
Experience with React or Vue.js

What we offer:
Competitive salary & equity package
Remote-first work environment
Flexible working hours
Health, dental, and vision insurance
401k matching
Annual learning budget of $2,500
Latest equipment of your choice
Regular team retreats to exciting locations
"""

def create_test_messy_job():
    """Create a test job with a messy job description to test the enhanced LLM parsing."""
    app = create_app()
    with app.app_context():
        # Parse the job description
        parser = JobDescriptionParser()
        parsed_data = parser.parse_description(MESSY_JOB_DESCRIPTION)
        
        # Print parsed sections
        print("Parsed Job Description Sections:")
        for section in parsed_data.get('sections', []):
            print(f"\n--- {section['title']} ---")
            if section['type'] == 'list':
                for item in section['content']:
                    print(f"• {item}")
            else:
                print(section['content'])
        
        # Create a new job with the parsed data
        job = Job(
            title="Senior Software Engineer",
            company="ACME Tech Solutions",
            location="Remote (US)",
            description=MESSY_JOB_DESCRIPTION,
            url="https://example.com/job",
            salary="$120K - $170K DOE",
            job_type="Full-time",
            status="Saved",
            date_added=datetime.utcnow(),
            parsed_data=json.dumps(parsed_data)
        )
        
        # Check if job already exists
        existing_job = Job.query.filter_by(title="Senior Software Engineer", 
                                         company="ACME Tech Solutions").first()
        if existing_job:
            print(f"Test job already exists with ID: {existing_job.id}")
            return existing_job.id
        
        # Add to database
        db.session.add(job)
        db.session.commit()
        
        print(f"Created test job with ID: {job.id}")
        print(f"View at: http://127.0.0.1:5000/jobs/{job.id}")
        return job.id

if __name__ == "__main__":
    job_id = create_test_messy_job()
    print(f"Test complete. Job ID: {job_id}")
