"""
Company information parser utilities.
This module handles fetching and structuring company information from various sources.
"""


import contextlib
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
DEFAULT_MODEL = os.environ.get('GROQ_MODEL', "compound-beta")

class CompanyInfoParser:
    """Parser for extracting and structuring company information from websites."""
    
    @staticmethod
    def fetch_company_data(company_name: str, website_url: Optional[str] = None, 
                          linkedin_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch and structure company information from available sources using an LLM agentic approach.
        """
        company_data = {
            "name": company_name,
            "website_url": website_url,
            "linkedin_url": linkedin_url,
            "metadata": {"sources": []}
        }
        # Compose a prompt for the LLM agent to autonomously gather and structure company info
        prompt = f"""
        You are an autonomous agent with access to web browsing and information extraction tools.
        Your task is to gather and structure information about the following company:
        Company Name: {company_name}
        Website URL: {website_url or 'N/A'}
        LinkedIn URL: {linkedin_url or 'N/A'}
        
        Steps:
        1. If a website URL is provided, visit the homepage and About/Company page to extract:
           - Company description/overview
           - Key products/services
           - Contact info (email, phone, address)
        2. If a LinkedIn URL is provided, extract:
           - Industry
           - Company size
           - Headquarters
           - Founded year
        3. Consolidate all findings into a structured JSON with these fields:
           - company_description
           - industry
           - company_size
           - founded
           - headquarters
           - products_services
           - contact_info
           - mission_values (if available)
        4. If any information is missing, leave the field as null or an empty list.
        Output only the JSON object.
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": "You are a company information agent with web browsing and extraction tools."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    company_data["consolidated_info"] = json.loads(content)
                except json.JSONDecodeError:
                    if json_match := re.search(r'```(?:json)?\\s*(.*?)\\s*```', content, re.DOTALL):
                        with contextlib.suppress(json.JSONDecodeError):
                            company_data["consolidated_info"] = json.loads(json_match[1])
            else:
                company_data["consolidated_info"] = CompanyInfoParser._create_fallback_profile(company_data)
        except Exception as e:
            print(f"Error in LLM agentic company info: {str(e)}")
            company_data["consolidated_info"] = CompanyInfoParser._create_fallback_profile(company_data)
        return company_data

    @staticmethod
    def fetch_company_reviews(company_name: str, glassdoor_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch and structure company reviews using an LLM agentic approach.
        """
        reviews_data = {
            "company_name": company_name,
            "glassdoor_url": glassdoor_url,
            "metadata": {"sources": []}
        }
        prompt = f"""
        You are an autonomous agent with web browsing and review analysis tools.
        Your task is to gather and summarize reviews for the following company:
        Company Name: {company_name}
        Glassdoor URL: {glassdoor_url or 'N/A'}
        
        Steps:
        1. If a Glassdoor URL is provided, visit the page and extract:
           - Overall rating
           - Number of reviews
           - Top 5 pros and cons
           - Culture ratings (work-life balance, compensation, management, etc.)
        2. Summarize the company culture and work environment in a structured JSON with:
           - overall_assessment
           - key_strengths
           - areas_for_improvement
           - culture_highlights
           - bottom_line (recommendation)
        Output only the JSON object.
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": "You are a company review agent with web browsing and summarization tools."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    reviews_data["structured_reviews"] = json.loads(content)
                except json.JSONDecodeError:
                    if json_match := re.search(r'```(?:json)?\\s*(.*?)\\s*```', content, re.DOTALL):
                        with contextlib.suppress(json.JSONDecodeError):
                            reviews_data["structured_reviews"] = json.loads(json_match[1])
            else:
                reviews_data["structured_reviews"] = CompanyInfoParser._create_fallback_review_summary(reviews_data)
        except Exception as e:
            print(f"Error in LLM agentic company reviews: {str(e)}")
            reviews_data["structured_reviews"] = CompanyInfoParser._create_fallback_review_summary(reviews_data)
        return reviews_data

    @staticmethod
    def _fetch_website_info(url: str) -> Dict[str, Any]:
        """
        Use an LLM agentic approach to extract detailed information from a company website.
        """
        prompt = f"""
        You are an autonomous agent with web browsing and extraction tools.
        Your task is to visit the following company website and extract:
        - Title
        - Description (meta or main)
        - About/company section text
        - Structured data (JSON-LD, OpenGraph, microdata)
        - Contact info (email, phone, address)
        Output a JSON object with these fields: title, description, about_text, structured_data, contact_info, url, errors (if any).
        Website URL: {url}
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": "You are a web extraction agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if json_match := re.search(r'```(?:json)?\\s*(.*?)\\s*```', content, re.DOTALL):
                        with contextlib.suppress(json.JSONDecodeError):
                            return json.loads(json_match[1])
            return {"url": url, "errors": ["Failed to extract website info"]}
        except Exception as e:
            return {"url": url, "errors": [f"Error in LLM agentic website info: {str(e)}"]}

    @staticmethod
    def _fetch_linkedin_info(url: str) -> Dict[str, Any]:
        """
        Use an LLM agentic approach to extract company information from LinkedIn.
        """
        prompt = f"""
        You are an autonomous agent with web browsing and extraction tools.
        Your task is to visit the following LinkedIn company page and extract:
        - Company type
        - Number of employees
        - Headquarters
        - Founded year
        - Industry
        Output a JSON object with these fields: company_type, employees, headquarters, founded, industry, url, errors (if any).
        LinkedIn URL: {url}
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": "You are a LinkedIn extraction agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 800
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if json_match := re.search(r'```(?:json)?\\s*(.*?)\\s*```', content, re.DOTALL):
                        with contextlib.suppress(json.JSONDecodeError):
                            return json.loads(json_match[1])
            return {"url": url, "errors": ["Failed to extract LinkedIn info"]}
        except Exception as e:
            return {"url": url, "errors": [f"Error in LLM agentic LinkedIn info: {str(e)}"]}

    @staticmethod
    def _fetch_glassdoor_reviews(url: str) -> Dict[str, Any]:
        """
        Use an LLM agentic approach to extract company reviews from Glassdoor.
        """
        prompt = f"""
        You are an autonomous agent with web browsing and review extraction tools.
        Your task is to visit the following Glassdoor company page and extract:
        - Overall rating
        - Number of reviews
        - Top 5 pros and cons
        - Culture ratings (work-life balance, compensation, management, etc.)
        Output a JSON object with these fields: overall_rating, review_count, pros, cons, culture_ratings, url, errors (if any).
        Glassdoor URL: {url}
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": "You are a Glassdoor review extraction agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if json_match := re.search(r'```(?:json)?\\s*(.*?)\\s*```', content, re.DOTALL):
                        with contextlib.suppress(json.JSONDecodeError):
                            return json.loads(json_match[1])
            return {"url": url, "errors": ["Failed to extract Glassdoor reviews"]}
        except Exception as e:
            return {"url": url, "errors": [f"Error in LLM agentic Glassdoor reviews: {str(e)}"]}
