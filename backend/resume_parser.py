"""
Resume Parser - Extracts information from resume files
Supports PDF and DOCX formats
"""
import re
import pdfplumber
from docx import Document
from typing import Dict, List, Set

# Try to import spacy, but make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except (ImportError, TypeError, Exception):
    SPACY_AVAILABLE = False
    spacy = None


class ResumeParser:
    def __init__(self):
        """Initialize the resume parser"""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except (OSError, Exception):
                pass  # spacy not available or model not found, will use fallback
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file (PDF or DOCX)"""
        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.lower().endswith('.docx') or file_path.lower().endswith('.doc'):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Please use PDF or DOCX.")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def extract_skills(self, text: str, common_skills: List[str] = None) -> Set[str]:
        """Extract skills from resume text"""
        if common_skills is None:
            common_skills = self._get_common_skills()
        
        text_lower = text.lower()
        found_skills = set()
        
        # Match common skills
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.add(skill)
        
        # Extract skills section if present
        skills_pattern = r'(?:skills?|technical skills?|competencies?)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)'
        skills_match = re.search(skills_pattern, text, re.IGNORECASE | re.MULTILINE)
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            for delimiter in [',', ';', '|', '\n', '/']:
                if delimiter in skills_text:
                    for item in skills_text.split(delimiter):
                        skill = item.strip()
                        if len(skill) > 2 and len(skill) < 50:
                            found_skills.add(skill)
        
        return found_skills
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from resume"""
        experience = []
        
        # Pattern to match date ranges (e.g., "2020 - 2024", "Jan 2020 - Present")
        date_pattern = r'(\d{4}|\w{3}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3}\s+\d{4}|Present|Current)'
        
        # Split text into lines
        lines = text.split('\n')
        
        # Look for experience section
        in_experience_section = False
        current_entry = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Detect experience section
            if re.search(r'(experience|employment|work history|professional experience)', line_stripped, re.IGNORECASE):
                in_experience_section = True
                continue
            
            if in_experience_section and line_stripped:
                # Check if line contains date pattern (likely a job entry)
                date_match = re.search(date_pattern, line_stripped, re.IGNORECASE)
                if date_match:
                    if current_entry:
                        experience.append(current_entry)
                    current_entry = {
                        'dates': date_match.group(0),
                        'description': line_stripped
                    }
                elif current_entry:
                    current_entry['description'] += ' ' + line_stripped
        
        if current_entry:
            experience.append(current_entry)
        
        return experience
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        # Pattern for degrees
        degree_pattern = r'\b(?:Bachelor|Master|PhD|Doctorate|B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.)\s+(?:of|in)?\s*\w+'
        
        education_matches = re.findall(degree_pattern, text, re.IGNORECASE)
        education.extend(education_matches)
        
        # Look for education section
        education_section_pattern = r'(?:education|academic background)[\s:]*([^•\n]+(?:\n(?!•)[^•\n]+)*)'
        education_match = re.search(education_section_pattern, text, re.IGNORECASE | re.MULTILINE)
        if education_match:
            education_text = education_match.group(1)
            education.append(education_text.strip())
        
        return education
    
    def extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords from resume"""
        if not self.nlp:
            # Fallback: simple keyword extraction
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            return set(words[:50])  # Return first 50 capitalized words
        
        doc = self.nlp(text)
        keywords = set()
        
        # Extract noun phrases and important terms
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                keywords.add(chunk.text)
        
        # Extract entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY']:
                keywords.add(ent.text)
        
        return keywords
    
    def parse(self, file_path: str) -> Dict:
        """Parse resume and return structured data"""
        text = self.extract_text(file_path)
        
        return {
            'text': text,
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'keywords': self.extract_keywords(text)
        }
    
    def _get_common_skills(self) -> List[str]:
        """Return list of common technical and professional skills"""
        return [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Swift', 'Kotlin',
            'TypeScript', 'PHP', 'R', 'MATLAB', 'Scala', 'Perl', 'Rust',
            
            # Web Technologies
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django',
            'Flask', 'Spring', 'ASP.NET', 'jQuery', 'Bootstrap', 'SASS', 'LESS',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQLite', 'Redis',
            'Cassandra', 'Elasticsearch', 'DynamoDB',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD',
            'Git', 'GitHub', 'GitLab', 'Terraform', 'Ansible', 'Chef', 'Puppet',
            
            # Data Science & ML
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'Pandas', 'NumPy', 'Scikit-learn', 'Data Analysis', 'Statistics',
            'Natural Language Processing', 'Computer Vision',
            
            # Tools & Others
            'Linux', 'Unix', 'Windows', 'Agile', 'Scrum', 'JIRA', 'Confluence',
            'Project Management', 'Leadership', 'Communication', 'Teamwork',
            'Problem Solving', 'Analytical Thinking'
        ]

