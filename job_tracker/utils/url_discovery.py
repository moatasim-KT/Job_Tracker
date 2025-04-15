"""
Utility for automatically discovering company URLs.
This module handles searching for company websites, LinkedIn profiles, and Glassdoor review pages.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Optional, List, Tuple
import urllib.parse

class URLDiscovery:
    """Class to discover company-related URLs from search engines."""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    @staticmethod
    def discover_company_urls(company_name: str) -> Dict[str, Optional[str]]:
        """
        Discover company website, LinkedIn, and Glassdoor URLs.
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            Dictionary with discovered URLs
        """
        result = {
            "website_url": None,
            "linkedin_url": None,
            "glassdoor_url": None
        }
        
        # Clean up company name for search
        search_name = company_name.lower().strip()
        
        try:
            # Find company website
            result["website_url"] = URLDiscovery._find_company_website(search_name)
            
            # Find LinkedIn profile
            result["linkedin_url"] = URLDiscovery._find_linkedin_profile(search_name)
            
            # Find Glassdoor page
            result["glassdoor_url"] = URLDiscovery._find_glassdoor_page(search_name)
            
        except Exception as e:
            print(f"Error discovering URLs for {company_name}: {str(e)}")
        
        return result
    
    @staticmethod
    def _find_company_website(company_name: str) -> Optional[str]:
        """Find the official company website."""
        search_query = f"{company_name} official website"
        search_results = URLDiscovery._perform_search(search_query)
        
        if not search_results:
            return None
        
        # Look for likely official company domains
        # We're looking for results that:
        # 1. Don't contain job board or social media domains
        # 2. Likely contain the company name in the domain
        # 3. Are top-level domains (not deep pages)
        
        excluded_domains = ['linkedin.com', 'glassdoor.com', 'indeed.com', 'monster.com', 
                           'ziprecruiter.com', 'facebook.com', 'twitter.com', 'instagram.com',
                           'wikipedia.org', 'bloomberg.com', 'crunchbase.com']
        
        company_terms = company_name.lower().split()
        
        for result in search_results:
            url = result.get('link', '')
            
            # Skip if it's from an excluded domain
            if any(excluded in url for excluded in excluded_domains):
                continue
            
            # Parse the domain
            try:
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc.lower()
                
                # Skip subdomains that aren't www
                domain_parts = domain.split('.')
                if len(domain_parts) > 2 and domain_parts[0] != 'www':
                    continue
                
                # Extract the main domain name without www and extension
                main_domain = domain_parts[-2] if domain_parts[0] == 'www' else domain_parts[0]
                
                # Check if any company term is in the domain
                # This helps filter out unrelated websites
                if any(term in main_domain for term in company_terms):
                    # Normalize to include www and https
                    normalized_url = f"https://{domain}"
                    return normalized_url
            except:
                continue
        
        # If we couldn't find a good match with company name in domain, use the first result
        for result in search_results:
            url = result.get('link', '')
            if not any(excluded in url for excluded in excluded_domains):
                try:
                    parsed_url = urllib.parse.urlparse(url)
                    if parsed_url.netloc:
                        return f"https://{parsed_url.netloc}"
                except:
                    continue
        
        return None
    
    @staticmethod
    def _find_linkedin_profile(company_name: str) -> Optional[str]:
        """Find the company's LinkedIn profile."""
        search_query = f"{company_name} linkedin company"
        search_results = URLDiscovery._perform_search(search_query)
        
        if not search_results:
            return None
        
        # Look for LinkedIn company URLs
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/company/[^/\s"]+'
        
        for result in search_results:
            url = result.get('link', '')
            match = re.search(linkedin_pattern, url)
            if match:
                return match.group(0)
        
        return None
    
    @staticmethod
    def _find_glassdoor_page(company_name: str) -> Optional[str]:
        """Find the company's Glassdoor reviews page."""
        search_query = f"{company_name} glassdoor reviews"
        search_results = URLDiscovery._perform_search(search_query)
        
        if not search_results:
            return None
        
        # Look for Glassdoor reviews URLs
        glassdoor_pattern = r'https?://(?:www\.)?glassdoor\.(?:com|co\.[a-z]{2})/Reviews/[^/\s"]+-Reviews-[^/\s"]+'
        
        for result in search_results:
            url = result.get('link', '')
            match = re.search(glassdoor_pattern, url)
            if match:
                return match.group(0)
        
        return None
    
    @staticmethod
    def _perform_search(query: str, num_results: int = 10) -> List[Dict]:
        """
        Perform a search using a search API.
        
        Note: For production, you would want to use an actual search API like Google's Custom Search API,
        Bing Web Search API, or another search service. This implementation uses a fake response for 
        demonstration purposes.
        
        In a real implementation, replace this with an API call to a search service.
        """
        
        # For a real implementation, uncomment this and replace with your actual search API call
        # try:
        #     api_key = "YOUR_SEARCH_API_KEY"
        #     endpoint = "https://api.search-service.com/search"
        #     params = {
        #         "q": query,
        #         "num": num_results,
        #         "key": api_key
        #     }
        #     response = requests.get(endpoint, params=params, headers=URLDiscovery.HEADERS)
        #     return response.json().get("items", [])
        # except Exception as e:
        #     print(f"Error performing search: {str(e)}")
        #     return []
        
        # For this demonstration, we'll return a simulated response based on the query
        simulated_results = []
        
        if "official website" in query:
            company_name = query.replace("official website", "").strip().lower()
            domain_name = company_name.replace(" ", "").replace(",", "").replace(".", "")
            simulated_results = [
                {"link": f"https://www.{domain_name}.com"},
                {"link": f"https://www.{domain_name}.io"},
                {"link": f"https://www.linkedin.com/company/{domain_name}"},
                {"link": f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"}
            ]
        elif "linkedin company" in query:
            company_name = query.replace("linkedin company", "").strip().lower()
            domain_name = company_name.replace(" ", "").replace(",", "").replace(".", "")
            simulated_results = [
                {"link": f"https://www.linkedin.com/company/{domain_name}"},
                {"link": f"https://www.linkedin.com/company/{domain_name.replace(' ', '-')}"},
                {"link": f"https://www.{domain_name}.com/about"},
                {"link": f"https://www.glassdoor.com/Overview/{domain_name}-Overview-EI_IE12345.11,20.htm"}
            ]
        elif "glassdoor reviews" in query:
            company_name = query.replace("glassdoor reviews", "").strip().lower()
            domain_name = company_name.replace(" ", "").replace(",", "").replace(".", "")
            simulated_results = [
                {"link": f"https://www.glassdoor.com/Reviews/{domain_name.title()}-Reviews-E12345.htm"},
                {"link": f"https://www.glassdoor.com/Reviews/{domain_name.replace(' ', '-')}-Reviews-E12345.htm"},
                {"link": f"https://www.indeed.com/cmp/{domain_name}/reviews"},
                {"link": f"https://www.linkedin.com/company/{domain_name}/reviews"}
            ]
        
        return simulated_results
