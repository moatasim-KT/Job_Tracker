"""
Test script to verify the job description parsing functionality.
This script creates a test job with a detailed job description to test the LLM parsing.
"""

from job_tracker import create_app, db
from job_tracker.models import Job
from job_tracker.utils.llm_parser import JobDescriptionParser
import json
from datetime import datetime

# Sample job description for a Machine Learning Engineer
TEST_JOB_DESCRIPTION = """
About TCP (TimeClock Plus)
For more than 30 years, TCP has helped organizations engage their people by providing flexible, mobile timekeeping and workforce management solutions. Trusted by tens of thousands of customers and millions of users, TCP delivers best-in-class technology and personalized support to organizations of all sizes in the public and private sector to meet their complex timekeeping, employee scheduling, leave management and other workforce needs.

About The Role
We are seeking a passionate and skilled Machine Learning Engineer to work on developing and improving our AI-powered solutions. This position will involve training production models for a variety of machine learning tasks such as forecasting, anomaly detection, and event prediction, as well as leveraging cutting-edge libraries and technologies to build efficient and scalable systems.

Responsibilities:
• Train and deploy production-level machine learning models focused on forecasting, anomaly detection, and event prediction
• Develop and implement machine learning algorithms, ensuring their scalability, performance, and robustness
• Create agentic language model based user experiences
• Work with large datasets, process and analyze data using tools like Pandas and Numpy
• Use modern deep learning frameworks such as Pytorch to implement and optimize models
• Integrate machine learning models into the company's software applications
• Collaborate with cross-functional teams to solve complex business challenges through AI/ML

Requirements:
• Bachelor's degree in Computer Science, Engineering, Mathematics, or related field
• 2+ years of professional experience in machine learning or data science
• Strong programming skills in Python
• Proficiency with machine learning frameworks and libraries (PyTorch, scikit-learn)
• Experience with statistical analysis and data processing
• Familiarity with SQL and database systems
• Strong problem-solving and analytical skills
• Excellent communication and collaboration abilities

Preferred Qualifications:
• Master's or PhD in Computer Science, Machine Learning, or related field
• Experience with deep learning techniques and transformer models
• Knowledge of NLP and LLM applications in enterprise products
• Experience with time-series forecasting and anomaly detection
• Familiarity with cloud computing platforms (AWS, GCP, Azure)
• Understanding of MLOps and machine learning lifecycle management
• Experience with version control (Git) and CI/CD pipelines

Benefits:
• Competitive salary and comprehensive benefits package
• Flexible work arrangements
• Continuous learning and professional development opportunities
• Collaborative and innovative work environment
• Opportunity to work with cutting-edge AI technologies
• Paid time off and company holidays
• 401(k) matching program
"""

def create_test_job():
    """Create a test job with LLM parsing."""
    app = create_app()
    with app.app_context():
        # Parse the job description
        parser = JobDescriptionParser()
        parsed_data = parser.parse_description(TEST_JOB_DESCRIPTION)
        
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
            title="Machine Learning Engineer",
            company="TCP (TimeClock Plus)",
            location="Remote",
            description=TEST_JOB_DESCRIPTION,
            url="https://example.com/job",
            salary="Competitive",
            job_type="Full-time",
            status="Saved",
            date_added=datetime.utcnow(),
            parsed_data=json.dumps(parsed_data)
        )
        
        # Check if job already exists
        existing_job = Job.query.filter_by(title="Machine Learning Engineer", 
                                         company="TCP (TimeClock Plus)").first()
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
    job_id = create_test_job()
    print(f"Test complete. Job ID: {job_id}")
