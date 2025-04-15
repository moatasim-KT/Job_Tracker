"""
LLM-based job description parsing utilities.
This module handles the extraction of structured information from job descriptions.
"""

import json
import re
import os
import requests
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.environ.get('GROQ_MODEL', "meta-llama/llama-4-scout-17b-16e-instruct")

class JobDescriptionParser:
    """Parser that uses LLM capabilities to extract structured information from job descriptions."""
    
    @staticmethod
    def parse_description(description: str) -> Dict[str, Any]:
        """
        Parse a job description into structured sections using an LLM.
        
        Args:
            description: The raw job description text
            
        Returns:
            A dictionary containing structured job information with sections
        """
        try:
            # Check if API key is available
            if not GROQ_API_KEY:
                print("No Groq API key found. Set the GROQ_API_KEY environment variable to use the LLM parser.")
                return JobDescriptionParser._heuristic_parse(description)
            
            # Use Groq API with the specified model
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Analyze the job description below VERY CAREFULLY and extract structured information into the following distinct sections.

            **CRITICAL RULES - FOLLOW THESE STRICTLY:**
            1.  **NO OVERLAPPING CONTENT:** Each piece of information MUST appear in ONLY ONE section. DO NOT repeat details across sections.
            2.  **PRIORITIZE SPECIFICITY:** If a detail could fit into multiple sections (e.g., a skill mentioned within Responsibilities), place it ONLY in the MOST SPECIFIC section (e.g., 'Skills'). Remove it from the less specific section.
            3.  **OMIT EMPTY SECTIONS:** Only include sections if relevant content exists in the original text. Do NOT create empty sections or sections with placeholder text.
            4.  **COMPLETENESS:** Capture all relevant details from the original description, assigning each detail to its single, most appropriate section.
            5.  **UNIQUENESS:** Ensure the final content for each section is unique and not duplicated elsewhere.
            6.  **FORMATTING:** Identify if the content for each section should be a single paragraph or a list of items.

            **REQUIRED SECTIONS (Extract ONLY if content exists):**
            -   **About the Company:** Company overview, culture, mission. (Do NOT include role details here).
            -   **About the Role:** General description of the position and its purpose within the company. (Do NOT include specific tasks or requirements here).
            -   **Responsibilities:** Specific day-to-day duties, tasks, and core functions of the role. (Do NOT list required skills or qualifications here).
            -   **Requirements:** General qualifications, attributes, or prerequisites needed. (MUST NOT include specific skills, education levels, or years of experience - these belong in their dedicated sections below).
            -   **Skills:** Specific technical skills (e.g., Python, SQL, AWS) and soft skills (e.g., Communication, Teamwork).
            -   **Education:** Explicit degree requirements or educational background needed (e.g., Bachelor's in CS, MBA).
            -   **Experience:** Specific number of years or types of professional experience required (e.g., 5+ years in software development, experience managing teams).
            -   **Benefits:** Compensation details, perks, insurance, time off, etc.
            -   **Additional Information:** Any other relevant details, like location, travel requirements, application instructions, or EOE statements.

            **OUTPUT FORMAT (Strictly adhere to this JSON structure):**
            {{
                "sections": [
                    {{
                        "title": "Section Title",  // MUST be one of the titles listed above
                        "type": "paragraph" or "list", // Choose based on content structure
                        "content": "Formatted text content for paragraphs." or ["Item 1", "Item 2", "Item 3"] // For lists
                    }}
                    // ... more sections if applicable
                ]
            }}

            **Job Description Text:**
            ---
            {description}
            ---
            """
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an expert job description parser. Your primary goal is to extract structured information into STRICTLY DISTINCT, NON-OVERLAPPING sections. Prioritize accuracy and adherence to the non-overlapping rule above all else."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 4000
            }
            
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    parsed_data = json.loads(content)
                    if "sections" not in parsed_data:
                        parsed_data = {"sections": parsed_data}
                    
                    # Additional processing to improve section quality
                    improved_sections = []
                    for section in parsed_data.get("sections", []):
                        # Fix common issues
                        if section.get("type") == "list" and isinstance(section.get("content"), str):
                            # Convert string content into a list if marked as list type
                            items = [item.strip() for item in section["content"].split("\n") if item.strip()]
                            section["content"] = items
                        
                        # Clean up list items
                        if section.get("type") == "list" and isinstance(section.get("content"), list):
                            # Remove bullet points and numbering from list items
                            cleaned_items = []
                            for item in section["content"]:
                                item = re.sub(r'^[\s•\-\*\+\d\.\)]+', '', item).strip()
                                if item:
                                    cleaned_items.append(item)
                            section["content"] = cleaned_items
                        
                        # Add processed section
                        if section.get("title") and (
                            (section.get("type") == "paragraph" and section.get("content")) or
                            (section.get("type") == "list" and section.get("content") and len(section["content"]) > 0)
                        ):
                            improved_sections.append(section)
                    
                    # If we lost all sections in the cleaning, use the original
                    if improved_sections:
                        parsed_data["sections"] = improved_sections
                    
                    # Add metadata about successful API parse
                    parsed_data["metadata"] = {
                        "parsing_method": "llm",
                        "model": "llama-3.3-70b-versatile"
                    }
                    
                    return parsed_data
                    
                except json.JSONDecodeError:
                    # Try to extract JSON from text response
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        try:
                            parsed_data = json.loads(json_match.group(1))
                            if "sections" not in parsed_data:
                                parsed_data = {"sections": parsed_data}
                            # Add metadata about successful API parse
                            parsed_data["metadata"] = {
                                "parsing_method": "llm",
                                "model": "llama-3.3-70b-versatile"
                            }
                            return parsed_data
                        except json.JSONDecodeError:
                            pass
            
            # Handle API error cases
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error") if response.headers.get("content-type") == "application/json" else f"Status code: {response.status_code}"
                print(f"Groq API error: {error_detail}")
                
                # Check for authentication errors specifically
                if response.status_code == 401 or response.status_code == 403:
                    print("Authentication error with Groq API. Please check your API key.")
                elif response.status_code == 429:
                    print("Rate limit exceeded for Groq API.")
                
            # Fall back to heuristic parsing
            print("Error calling Groq API or parsing response, falling back to heuristic parsing")
            return JobDescriptionParser._heuristic_parse(description)
            
        except Exception as e:
            print(f"Error in LLM parsing: {str(e)}")
            # Simplified heuristic-based parsing as fallback
            return JobDescriptionParser._heuristic_parse(description)
    
    @staticmethod
    def _heuristic_parse(description: str) -> Dict[str, Any]:
        """Fallback method that uses regex patterns and heuristics to identify common sections in job descriptions"""
        print("--- Starting _heuristic_parse fallback ---")
        sections = []
        
        # Helper function to check if a section already exists
        def section_exists(title):
            normalized_title = title.lower().strip()
            for section in sections:
                if section["title"].lower().strip() == normalized_title:
                    return True
            return False
        
        # Helper function to extract a section based on patterns
        def extract_section(patterns, title, content_filter=None):
            print(f"  Trying to extract section: {title}")
            for i, pattern in enumerate(patterns):
                print(f"    Using pattern {i+1}: {pattern[:50]}...")
                matches = re.finditer(pattern, description, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    content = match.group(1).strip()
                    print(f"      Potential match found (length: {len(content)}): {content[:100]}...")
                    if len(content) > 30:  # Ensure content is substantial
                        if content_filter:
                            print("      Applying content filter...")
                            if not content_filter(content):
                                print("      Content failed filter.")
                                continue
                            else:
                                print("      Content passed filter.")
                            
                        # Check if content is a list
                        is_list = bool(re.search(r'(?:^|\n)[ \t]*(?:•|\*|-|\d+[\.\)]|\([a-z0-9]\))[ \t]+', content))
                        if is_list:
                            print("      Detected list format.")
                            list_pattern = r'(?:^|\n)[ \t]*(?:•|\*|-|\d+[\.\)]|\([a-z0-9]\))[ \t]+'
                            items = re.split(list_pattern, content)
                            items = [item.strip() for item in items if item.strip()]
                            if not section_exists(title):
                                print(f"      Adding section '{title}' (list) with {len(items)} items.")
                                sections.append({
                                    "title": title,
                                    "type": "list",
                                    "content": items
                                })
                                return True
                            else:
                                print(f"      Section '{title}' already exists, skipping.")
                        else:
                            print("      Detected paragraph format.")
                            if not section_exists(title):
                                print(f"      Adding section '{title}' (paragraph).")
                                sections.append({
                                    "title": title,
                                    "type": "paragraph",
                                    "content": content
                                })
                                return True
                            else:
                                print(f"      Section '{title}' already exists, skipping.")
                    else:
                        print("      Content too short, skipping.")
                print(f"  Finished trying to extract section: {title}")
            return False
        
        # About the Company section patterns
        company_patterns = [
            r'(?:^|\n)(?:about (?:us|the company|our company|.{1,20} company))(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:company description|who we are|we are .{1,20})(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:our story|our mission|our values)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(company_patterns, "About the Company", 
                       lambda content: not any(kw in content.lower() for kw in ['responsibility', 'requirement', 'qualification']))
        
        # About the Role section patterns
        role_patterns = [
            r'(?:^|\n)(?:about the (?:role|position|job|opportunity))(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:role overview|job overview|position overview|position summary|job summary)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:we are looking for|we are seeking|we need)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(role_patterns, "About the Role", 
                      lambda content: not any(kw in content.lower() for kw in ['responsibility', 'requirement', 'qualification']))
        
        # Responsibilities section patterns
        responsibility_patterns = [
            r'(?:^|\n)(?:responsibilities|duties|what you\'ll do|what you will do|job duties|day to day|day-to-day|in this role you will|your role|you will be responsible for)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:your responsibilities include|as a .{1,30}, you will|as the .{1,30}, you will)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(responsibility_patterns, "Responsibilities")
        
        # Requirements (general) section patterns
        requirement_patterns = [
            r'(?:^|\n)(?:requirements|qualifications|what you\'ll need|what you need|what we are looking for|job requirements|you should have)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:what you\'ll bring|what you will bring|what you need to have|who you are)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        # Only extract if it doesn't mention skills or education prominently
        extract_section(requirement_patterns, "Requirements", 
                       lambda content: not (re.search(r'(?:degree|education|bachelor|master|phd|diploma)', content.lower()) and len(content) < 300))
        
        # Skills (specific technical skills) section patterns
        skills_patterns = [
            r'(?:^|\n)(?:skills|technical skills|technical requirements|technical qualifications|you should know|you must know|must have skills|required skills)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:professional skills|soft skills|technical proficiency|tech stack|programming languages|tools & technologies|tools and technologies)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(skills_patterns, "Skills")
        
        # Education section patterns
        education_patterns = [
            r'(?:^|\n)(?:education|academic|educational requirements|academic requirements|degree requirements|academic qualifications)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:bachelor\'s|master\'s|degree|diploma)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
        ]
        # Try to extract education-specific content
        education_section = extract_section(education_patterns, "Education")
        
        # If no specific education section, check if it's mentioned in requirements
        if not education_section:
            for section in sections:
                if section["title"] == "Requirements":
                    content = section["content"]
                    if isinstance(content, list):
                        edu_items = [item for item in content if re.search(r'(?:degree|education|bachelor|master|phd|diploma)', item.lower())]
                        if edu_items and len(edu_items) < len(content) / 2:  # Don't extract if most items are about education
                            sections.append({
                                "title": "Education",
                                "type": "list",
                                "content": edu_items
                            })
                            # Remove education items from requirements
                            section["content"] = [item for item in content if item not in edu_items]
                    elif isinstance(content, str):
                        edu_matches = re.findall(r'(?:^|\n)(?:.*?(?:degree|education|bachelor|master|phd|diploma).*?)(?:\n|$)', 
                                               content, re.IGNORECASE)
                        if edu_matches and len(''.join(edu_matches)) < len(content) / 2:
                            edu_content = '\n'.join(edu_matches)
                            sections.append({
                                "title": "Education",
                                "type": "paragraph",
                                "content": edu_content
                            })
                            # Remove education sentences from requirements
                            for match in edu_matches:
                                content = content.replace(match, '')
                            section["content"] = content.strip()
        
        # Experience section patterns
        experience_patterns = [
            r'(?:^|\n)(?:experience|professional experience|work experience|years of experience|minimum experience)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:\d+ years|at least \d+ years|minimum of \d+ years)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        experience_section = extract_section(experience_patterns, "Experience")
        
        # If no specific experience section, check if it's prominently mentioned in requirements
        if not experience_section:
            for section in sections:
                if section["title"] == "Requirements":
                    content = section["content"]
                    if isinstance(content, list):
                        exp_items = [item for item in content if re.search(r'(?:\d+ years|experience in|experience with)', item.lower())]
                        if exp_items and len(exp_items) < len(content) / 2:
                            sections.append({
                                "title": "Experience",
                                "type": "list",
                                "content": exp_items
                            })
                            # Remove experience items from requirements
                            section["content"] = [item for item in content if item not in exp_items]
                    elif isinstance(content, str):
                        exp_matches = re.findall(r'(?:^|\n)(?:.*?(?:\d+ years|experience in|experience with).*?)(?:\n|$)', 
                                              content, re.IGNORECASE)
                        if exp_matches and len(''.join(exp_matches)) < len(content) / 2:
                            exp_content = '\n'.join(exp_matches)
                            sections.append({
                                "title": "Experience",
                                "type": "paragraph",
                                "content": exp_content
                            })
                            # Remove experience sentences from requirements
                            for match in exp_matches:
                                content = content.replace(match, '')
                            section["content"] = content.strip()
        
        # Benefits section patterns
        benefits_patterns = [
            r'(?:^|\n)(?:benefits|perks|what we offer|what\'s in it for you|you\'ll receive|we provide|our offering|compensation|what to expect)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:our benefits|compensation and benefits|in return we offer|package includes|we offer|why work (?:for|with) us)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(benefits_patterns, "Benefits")
        
        # Additional Information section patterns
        additional_patterns = [
            r'(?:^|\n)(?:additional information|more information|to apply|application process|other information|notes)(.*?)(?:\n\n|\n(?:[A-Z])|$)',
            r'(?:^|\n)(?:about the process|how to apply|equal opportunity|diversity|inclusion|accessibility)(.*?)(?:\n\n|\n(?:[A-Z])|$)'
        ]
        extract_section(additional_patterns, "Additional Information")
        
        # If no sections were found, create a generic one with the full text
        if not sections:
            print("  No sections extracted by heuristics, adding full description as 'Job Description'.")
            sections.append({
                "title": "Job Description",
                "type": "paragraph",
                "content": description.strip()
            })

        print(f"--- Finished _heuristic_parse. Found {len(sections)} sections. ---")
        return {
            "sections": sections,
            "metadata": {
                "parsing_method": "heuristic"
            }
        }

    @staticmethod 
    def extract_company_info(company_name: str) -> Dict[str, Any]:
        """
        Placeholder for extracting company information from external sources.
        In a real implementation, this would query company databases or web APIs.
        
        Args:
            company_name: The name of the company
            
        Returns:
            Dictionary with company information
        """
        return {
            "name": company_name,
            "description": "Company information would be fetched from external sources in a production implementation.",
            "rating": None,
            "review_count": 0,
            "website": None,
            "size": None,
            "founded": None,
            "headquarters": None,
            "industry": None
        }
