"""
Company information parser utilities.
This module handles fetching and structuring company information from various sources.
"""

import json
import re
import os
import requests
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup
import html2text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration (same as in llm_parser.py)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.environ.get('GROQ_MODEL', "meta-llama/llama-4-scout-17b-16e-instruct")

class CompanyInfoParser:
    """Parser for extracting and structuring company information from websites."""
    
    @staticmethod
    def fetch_company_data(company_name: str, website_url: Optional[str] = None, 
                          linkedin_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch and structure company information from available sources.
        
        Args:
            company_name: Name of the company
            website_url: URL to the company's website (optional)
            linkedin_url: URL to the company's LinkedIn profile (optional)
            
        Returns:
            Dictionary containing structured company information
        """
        company_data = {
            "name": company_name,
            "website_info": {},
            "linkedin_info": {},
            "metadata": {
                "sources": []
            }
        }
        
        # Get information from company website if available
        if website_url:
            try:
                website_info = CompanyInfoParser._fetch_website_info(website_url)
                company_data["website_info"] = website_info
                company_data["metadata"]["sources"].append("company_website")
            except Exception as e:
                print(f"Error fetching company website info: {str(e)}")
        
        # Get information from LinkedIn if available
        if linkedin_url:
            try:
                linkedin_info = CompanyInfoParser._fetch_linkedin_info(linkedin_url)
                company_data["linkedin_info"] = linkedin_info
                company_data["metadata"]["sources"].append("linkedin")
            except Exception as e:
                print(f"Error fetching LinkedIn info: {str(e)}")
        
        # If we have data from multiple sources, use LLM to create a consolidated profile
        if company_data["metadata"]["sources"]:
            try:
                consolidated_info = CompanyInfoParser._parse_with_llm(company_data)
                company_data["consolidated_info"] = consolidated_info
            except Exception as e:
                print(f"Error consolidating company information: {str(e)}")
                # Create a fallback consolidated profile
                company_data["consolidated_info"] = CompanyInfoParser._create_fallback_profile(company_data)
        
        return company_data
    
    @staticmethod
    def fetch_company_reviews(company_name: str, glassdoor_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch and structure company reviews from available sources.
        
        Args:
            company_name: Name of the company
            glassdoor_url: URL to the company's Glassdoor page (optional)
            
        Returns:
            Dictionary containing structured company reviews
        """
        reviews_data = {
            "company_name": company_name,
            "overall_rating": None,
            "review_count": 0,
            "pros": [],
            "cons": [],
            "culture_ratings": {},
            "review_highlights": [],
            "metadata": {
                "sources": []
            }
        }
        
        # Get reviews from Glassdoor if available
        if glassdoor_url:
            try:
                glassdoor_reviews = CompanyInfoParser._fetch_glassdoor_reviews(glassdoor_url)
                reviews_data.update(glassdoor_reviews)
                reviews_data["metadata"]["sources"].append("glassdoor")
            except Exception as e:
                print(f"Error fetching Glassdoor reviews: {str(e)}")
        
        # Use the LLM to structure and summarize the reviews
        if reviews_data["metadata"]["sources"]:
            try:
                structured_reviews = CompanyInfoParser._structure_reviews_with_llm(reviews_data)
                reviews_data["structured_reviews"] = structured_reviews
            except Exception as e:
                print(f"Error structuring company reviews: {str(e)}")
        
        return reviews_data
    
    @staticmethod
    def _fetch_website_info(url: str) -> Dict[str, Any]:
        """Fetch and extract information from company website."""
        # In a real implementation, this would use more sophisticated scraping
        # For now, we'll implement a simplified version
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                return {"error": f"Failed to fetch website: {response.status_code}"}
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract basic information
            title = soup.title.text.strip() if soup.title else None
            
            # Extract meta descriptions
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc and "content" in meta_desc.attrs else None
            
            # Try to find About Us or similar sections
            about_section = ""
            about_patterns = ["about", "about us", "our company", "who we are", "our story"]
            
            # Look for elements with these patterns in their IDs, classes, or href attributes
            for pattern in about_patterns:
                # Check links
                about_links = soup.find_all("a", href=lambda href: href and pattern in href.lower())
                # Check divs and sections with IDs or classes containing the pattern
                about_divs = soup.find_all(["div", "section"], 
                                          id=lambda x: x and pattern in x.lower())
                about_divs.extend(soup.find_all(["div", "section"], 
                                             class_=lambda x: x and pattern in x.lower()))
                
                if about_links or about_divs:
                    about_section = f"Found potential 'About Us' section with pattern: {pattern}"
                    break
            
            # For demonstration, we're not actually navigating to the About Us page or fully parsing it
            # In a real implementation, you would follow the link and extract the content
            
            return {
                "title": title,
                "description": description,
                "about_section": about_section,
                "url": url
            }
            
        except Exception as e:
            return {"error": f"Error processing website: {str(e)}"}
    
    @staticmethod
    def _fetch_linkedin_info(url: str) -> Dict[str, Any]:
        """
        Fetch and extract information from LinkedIn.
        
        Note: LinkedIn actively blocks scraping, so a real implementation would likely
        use a dedicated LinkedIn API or scraping service with proper authentication.
        
        This is a placeholder implementation for demonstration purposes.
        """
        return {
            "note": "LinkedIn scraping is simulated for demonstration purposes.",
            "company_type": "Software Development",
            "employees": "1,000-5,000 employees",
            "headquarters": "California, USA",
            "founded": "2010",
            "industry": "Technology",
            "url": url
        }
    
    @staticmethod
    def _fetch_glassdoor_reviews(url: str) -> Dict[str, Any]:
        """
        Fetch and extract reviews from Glassdoor.
        
        Note: Glassdoor has anti-scraping measures. A real implementation would use
        their API or a specialized scraping service.
        
        This is a placeholder implementation for demonstration purposes.
        """
        return {
            "note": "Glassdoor scraping is simulated for demonstration purposes.",
            "overall_rating": 4.2,
            "review_count": 156,
            "pros": [
                "Great work-life balance",
                "Competitive pay",
                "Good benefits package",
                "Opportunities for growth",
                "Collaborative environment"
            ],
            "cons": [
                "Can be bureaucratic at times",
                "Limited remote work options",
                "Communication between departments could be improved",
                "Some legacy systems are still in use",
                "Meeting-heavy culture"
            ],
            "culture_ratings": {
                "work_life_balance": 4.5,
                "compensation": 4.0,
                "career_opportunities": 3.8,
                "management": 3.5,
                "company_culture": 4.2
            },
            "url": url
        }
    
    @staticmethod
    def _parse_with_llm(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to create a structured profile from various data sources."""
        try:
            # Prepare the input for the LLM
            input_text = f"""
            Company Name: {company_data['name']}
            
            Information from company website:
            {json.dumps(company_data.get('website_info', {}), indent=2)}
            
            Information from LinkedIn:
            {json.dumps(company_data.get('linkedin_info', {}), indent=2)}
            """
            
            prompt = f"""
            Based on the following information about {company_data['name']}, create a structured company profile.
            Extract key details such as:
            - Company description/overview
            - Industry
            - Company size
            - Founded year
            - Headquarters location
            - Key products or services
            - Company mission or values (if available)
            
            Format the result as a clean, structured JSON with these categories.
            
            Input information:
            {input_text}
            """
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a specialized company information parser that creates structured profiles from various data sources."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to extract JSON from the content
                try:
                    # If it's already valid JSON
                    structured_profile = json.loads(content)
                    return structured_profile
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        try:
                            structured_profile = json.loads(json_match.group(1))
                            return structured_profile
                        except json.JSONDecodeError:
                            pass
            
            # Fallback if the API call fails or returns invalid JSON
            return CompanyInfoParser._create_fallback_profile(company_data)
            
        except Exception as e:
            print(f"Error in LLM parsing for company profile: {str(e)}")
            return CompanyInfoParser._create_fallback_profile(company_data)
    
    @staticmethod
    def _structure_reviews_with_llm(reviews_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to structure and summarize company reviews."""
        try:
            # Prepare the input for the LLM
            input_text = f"""
            Company Name: {reviews_data['company_name']}
            Overall Rating: {reviews_data['overall_rating']}
            Number of Reviews: {reviews_data['review_count']}
            
            Pros:
            {json.dumps(reviews_data.get('pros', []), indent=2)}
            
            Cons:
            {json.dumps(reviews_data.get('cons', []), indent=2)}
            
            Culture Ratings:
            {json.dumps(reviews_data.get('culture_ratings', {}), indent=2)}
            """
            
            prompt = f"""
            Based on the following company review information, create a structured summary of the company culture and work environment.
            
            Include:
            - Overall assessment (short paragraph)
            - Key strengths (summarized from pros)
            - Areas for improvement (summarized from cons)
            - Culture highlights (based on ratings)
            - Bottom line (would you recommend working here?)
            
            Format the result as a clean, structured JSON with these categories.
            
            Input information:
            {input_text}
            """
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a specialized company review analyzer that summarizes employee feedback into useful insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to extract JSON from the content
                try:
                    # If it's already valid JSON
                    structured_reviews = json.loads(content)
                    return structured_reviews
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        try:
                            structured_reviews = json.loads(json_match.group(1))
                            return structured_reviews
                        except json.JSONDecodeError:
                            pass
            
            # Fallback if the API call fails or returns invalid JSON
            return CompanyInfoParser._create_fallback_review_summary(reviews_data)
            
        except Exception as e:
            print(f"Error in LLM parsing for company reviews: {str(e)}")
            return CompanyInfoParser._create_fallback_review_summary(reviews_data)
    
    @staticmethod
    def _create_fallback_profile(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic company profile when LLM parsing fails."""
        profile = {
            "company_description": "Information not available",
            "industry": "Unknown",
            "company_size": "Unknown",
            "founded": "Unknown",
            "headquarters": "Unknown",
            "products_services": [],
            "mission_values": []
        }
        
        # Try to get basic info from the data we have
        if company_data.get('website_info', {}).get('description'):
            profile['company_description'] = company_data['website_info']['description']
        
        linkedin_info = company_data.get('linkedin_info', {})
        if linkedin_info:
            if 'industry' in linkedin_info:
                profile['industry'] = linkedin_info['industry']
            if 'employees' in linkedin_info:
                profile['company_size'] = linkedin_info['employees']
            if 'founded' in linkedin_info:
                profile['founded'] = linkedin_info['founded']
            if 'headquarters' in linkedin_info:
                profile['headquarters'] = linkedin_info['headquarters']
        
        return profile
    
    @staticmethod
    def _create_fallback_review_summary(reviews_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic review summary when LLM parsing fails."""
        summary = {
            "overall_assessment": "Information not available",
            "key_strengths": [],
            "areas_for_improvement": [],
            "culture_highlights": {},
            "bottom_line": "Not enough information to provide a recommendation"
        }
        
        # Try to get basic info from the data we have
        if reviews_data.get('overall_rating'):
            summary['overall_assessment'] = f"The company has an overall rating of {reviews_data['overall_rating']} out of 5 based on {reviews_data.get('review_count', 0)} reviews."
        
        # Add some pros as key strengths
        if reviews_data.get('pros'):
            summary['key_strengths'] = reviews_data['pros'][:3]  # Take the first 3 pros
        
        # Add some cons as areas for improvement
        if reviews_data.get('cons'):
            summary['areas_for_improvement'] = reviews_data['cons'][:3]  # Take the first 3 cons
        
        # Add culture ratings if available
        if reviews_data.get('culture_ratings'):
            summary['culture_highlights'] = reviews_data['culture_ratings']
        
        # Create a simple bottom line
        if reviews_data.get('overall_rating'):
            rating = float(reviews_data['overall_rating'])
            if rating >= 4.0:
                summary['bottom_line'] = "Based on high ratings, this company appears to be a good place to work."
            elif rating >= 3.0:
                summary['bottom_line'] = "This company has average ratings and might be worth considering."
            else:
                summary['bottom_line'] = "The company has below-average ratings, suggesting potential issues."
        
        return summary
