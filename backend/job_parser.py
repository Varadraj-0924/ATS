"""
Job Description Parser - Extracts requirements and skills from job descriptions
"""
import re
from typing import Dict, List, Set


class JobDescriptionParser:
    def __init__(self):
        """Initialize the job description parser"""
        pass
    
    def extract_requirements(self, job_description: str) -> Dict:
        """Extract requirements from job description"""
        text_lower = job_description.lower()
        
        # Extract required skills
        skills = self._extract_skills(job_description)
        
        # Extract years of experience
        experience_years = self._extract_experience_years(job_description)
        
        # Extract education requirements
        education = self._extract_education_requirements(job_description)
        
        # Extract key responsibilities
        responsibilities = self._extract_responsibilities(job_description)
        
        # Extract qualifications
        qualifications = self._extract_qualifications(job_description)
        
        return {
            'skills': skills,
            'experience_years': experience_years,
            'education': education,
            'responsibilities': responsibilities,
            'qualifications': qualifications,
            'keywords': self._extract_keywords(job_description),
            'full_text': job_description
        }
    
    def _extract_skills(self, text: str) -> Set[str]:
        """Extract required skills from job description"""
        skills = set()
        text_lower = text.lower()
        
        # Common skills database
        common_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'swift', 'kotlin',
            'typescript', 'php', 'r', 'matlab', 'scala', 'perl', 'rust',
            'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express', 'django',
            'flask', 'spring', 'asp.net', 'jquery', 'bootstrap', 'sass', 'less',
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
            'git', 'github', 'gitlab', 'terraform', 'ansible', 'chef', 'puppet',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
            'pandas', 'numpy', 'scikit-learn', 'data analysis', 'statistics',
            'linux', 'unix', 'windows', 'agile', 'scrum', 'jira', 'confluence'
        ]
        
        # Check for each skill in the text
        for skill in common_skills:
            if skill in text_lower:
                skills.add(skill.title())
        
        # Look for skills section
        skills_patterns = [
            r'(?:required skills?|technical skills?|skills required|qualifications?)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)',
            r'(?:must have|required)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)',
        ]
        
        for pattern in skills_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                skills_text = match.group(1)
                # Extract capitalized terms (likely technologies)
                capitalized_terms = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', skills_text)
                skills.update([term for term in capitalized_terms if len(term) > 2])
                
                # Also check for common skill patterns
                for delimiter in [',', ';', '|', '\n', '/', '•', '-']:
                    for item in skills_text.split(delimiter):
                        item = item.strip()
                        if len(item) > 2 and len(item) < 50:
                            skills.add(item)
        
        return skills
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements"""
        education = []
        
        degree_pattern = r'\b(Bachelor|Master|PhD|Doctorate|B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.|BS|BA|MS|MA)\s+(?:degree|of|in)?\s*\w*'
        
        matches = re.finditer(degree_pattern, text, re.IGNORECASE)
        for match in matches:
            education.append(match.group(0))
        
        return education
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities"""
        responsibilities = []
        
        # Look for responsibilities section
        responsibility_patterns = [
            r'(?:responsibilities|key responsibilities|duties?|what you\'ll do)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)',
        ]
        
        for pattern in responsibility_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                responsibilities_text = match.group(1)
                # Split by bullet points or new lines
                for line in responsibilities_text.split('\n'):
                    line = line.strip()
                    if line and len(line) > 10:
                        responsibilities.append(line)
        
        return responsibilities[:10]  # Limit to 10
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications"""
        qualifications = []
        
        qualification_patterns = [
            r'(?:qualifications?|requirements?|must have)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)',
        ]
        
        for pattern in qualification_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                qualifications_text = match.group(1)
                for line in qualifications_text.split('\n'):
                    line = line.strip()
                    if line and len(line) > 10:
                        qualifications.append(line)
        
        return qualifications[:10]  # Limit to 10
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords"""
        # Extract capitalized terms (likely technologies, companies, etc.)
        keywords = set(re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text))
        
        # Filter out common words
        common_words = {'The', 'A', 'An', 'This', 'That', 'We', 'You', 'Your', 'Our'}
        keywords = keywords - common_words
        
        return keywords


