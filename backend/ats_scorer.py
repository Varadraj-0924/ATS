"""
ATS Scorer - Compares resume with job description and generates scores
"""
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher
import re

from ml_model import compute_semantic_similarity


class ATSScorer:
    def __init__(self):
        """Initialize the ATS scorer"""
        pass
    
    def calculate_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Calculate overall ATS score and generate analysis"""
        
        # Calculate individual component scores
        skills_score, skills_match, missing_skills = self._score_skills(
            resume_data.get('skills', set()),
            job_data.get('skills', set())
        )
        
        keywords_score, matched_keywords = self._score_keywords(
            resume_data.get('keywords', set()),
            job_data.get('keywords', set())
        )
        
        experience_score = self._score_experience(
            resume_data.get('experience', []),
            job_data.get('experience_years', 0)
        )
        
        education_score = self._score_education(
            resume_data.get('education', []),
            job_data.get('education', [])
        )

        semantic_score = self._score_semantic(
            resume_data.get('text', ''),
            job_data.get('full_text', '')
        )
        
        # Calculate weighted overall score (now includes ML semantic similarity)
        overall_score = (
            skills_score * 0.35 +   # Skills are most important (35%)
            keywords_score * 0.20 +  # Keywords (20%)
            experience_score * 0.15 +  # Experience (15%)
            education_score * 0.10 +   # Education (10%)
            semantic_score * 0.20    # ML semantic similarity (20%)
        )
        
        # Generate strengths
        strengths = self._generate_strengths(
            resume_data, job_data, skills_match, matched_keywords, semantic_score
        )
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(
            missing_skills, job_data, resume_data, overall_score, semantic_score
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'skills_score': round(skills_score, 1),
            'keywords_score': round(keywords_score, 1),
            'experience_score': round(experience_score, 1),
            'education_score': round(education_score, 1),
            'semantic_score': round(semantic_score, 1),
            'missing_skills': list(missing_skills),
            'matched_skills': list(skills_match),
            'strengths': strengths,
            'suggestions': suggestions
        }
    
    def _score_skills(self, resume_skills: Set[str], job_skills: Set[str]) -> Tuple[float, Set[str], Set[str]]:
        """Score skills match (0-100)"""
        if not job_skills:
            return 100.0, set(), set()
        
        # Normalize skills to lowercase for comparison
        resume_skills_lower = {s.lower().strip() for s in resume_skills}
        job_skills_lower = {s.lower().strip() for s in job_skills}
        
        # Find exact matches
        exact_matches = resume_skills_lower & job_skills_lower
        
        # Find fuzzy matches (similar skills)
        fuzzy_matches = set()
        remaining_job_skills = job_skills_lower - exact_matches
        
        for job_skill in remaining_job_skills:
            for resume_skill in resume_skills_lower:
                similarity = SequenceMatcher(None, job_skill, resume_skill).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    fuzzy_matches.add(job_skill)
                    break
        
        # Find original case matched skills for display
        matched_skills = set()
        for job_skill_orig in job_skills:
            if job_skill_orig.lower().strip() in (exact_matches | fuzzy_matches):
                matched_skills.add(job_skill_orig)
        
        total_matches = len(exact_matches) + len(fuzzy_matches)
        score = (total_matches / len(job_skills_lower)) * 100 if job_skills_lower else 100.0
        score = min(score, 100.0)
        
        # Missing skills (original case)
        missing_skills = job_skills - matched_skills
        
        return score, matched_skills, missing_skills
    
    def _score_keywords(self, resume_keywords: Set[str], job_keywords: Set[str]) -> Tuple[float, Set[str]]:
        """Score keyword match (0-100)"""
        if not job_keywords:
            return 100.0, set()
        
        # Normalize keywords
        resume_keywords_lower = {k.lower().strip() for k in resume_keywords}
        job_keywords_lower = {k.lower().strip() for k in job_keywords}
        
        # Find matches
        matches = resume_keywords_lower & job_keywords_lower
        
        # Find original case matched keywords
        matched_keywords = set()
        for job_kw_orig in job_keywords:
            if job_kw_orig.lower().strip() in matches:
                matched_keywords.add(job_kw_orig)
        
        score = (len(matches) / len(job_keywords_lower)) * 100 if job_keywords_lower else 100.0
        score = min(score, 100.0)
        
        return score, matched_keywords
    
    def _score_experience(self, resume_experience: List[Dict], required_years: int) -> float:
        """Score experience match (0-100)"""
        if required_years == 0:
            return 100.0
        
        # Extract years from experience entries
        total_years = 0
        date_pattern = r'(\d{4})'
        
        for exp in resume_experience:
            dates = exp.get('dates', '')
            years = re.findall(date_pattern, dates)
            if len(years) >= 2:
                try:
                    start_year = int(years[0])
                    end_year = int(years[1]) if years[1] else 2024
                    total_years += (end_year - start_year)
                except ValueError:
                    pass
        
        # If we can't extract years, assume they have some experience
        if total_years == 0 and resume_experience:
            total_years = len(resume_experience) * 2  # Estimate 2 years per role
        
        # Score based on meeting/exceeding requirement
        if total_years >= required_years:
            return 100.0
        else:
            return (total_years / required_years) * 100
    
    def _score_education(self, resume_education: List[str], job_education: List[str]) -> float:
        """Score education match (0-100)"""
        if not job_education:
            return 100.0
        
        resume_edu_text = ' '.join(resume_education).lower()
        
        matches = 0
        for job_edu in job_education:
            job_edu_lower = job_edu.lower()
            if any(term in resume_edu_text for term in job_edu_lower.split()[:2]):  # Check first 2 words
                matches += 1
        
        score = (matches / len(job_education)) * 100 if job_education else 100.0
        return min(score, 100.0)
    
    def _score_semantic(self, resume_text: str, job_text: str) -> float:
        """Score semantic similarity (0-100) using ML (TF-IDF + cosine similarity)"""
        return compute_semantic_similarity(resume_text, job_text)

    def _generate_strengths(self, resume_data: Dict, job_data: Dict, 
                           matched_skills: Set[str], matched_keywords: Set[str], semantic_score: float) -> List[str]:
        """Generate list of strengths"""
        strengths = []
        
        # Skills strengths
        if len(matched_skills) > 0:
            if len(matched_skills) >= 5:
                strengths.append(f"Strong technical skills match ({len(matched_skills)} skills aligned with job requirements)")
            else:
                strengths.append(f"Some relevant technical skills ({len(matched_skills)} matched)")
        
        # Keywords strengths
        if len(matched_keywords) > 0:
            strengths.append(f"Good keyword alignment ({len(matched_keywords)} keywords match)")

        # Semantic similarity strength
        if semantic_score >= 70:
            strengths.append("Strong overall alignment to the job description (semantic similarity)")
        
        # Experience strengths
        if resume_data.get('experience'):
            strengths.append(f"Demonstrated work experience ({len(resume_data['experience'])} positions)")
        
        # Education strengths
        if resume_data.get('education'):
            strengths.append(f"Relevant educational background")
        
        if not strengths:
            strengths.append("Resume shows potential, but needs more alignment with job requirements")
        
        return strengths
    
    def _generate_suggestions(self, missing_skills: Set[str], job_data: Dict, 
                            resume_data: Dict, overall_score: float, semantic_score: float) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Missing skills suggestions
        if missing_skills:
            top_missing = list(missing_skills)[:5]  # Top 5 missing skills
            if top_missing:
                suggestions.append(
                    f"Add missing key skills: {', '.join(top_missing)}. "
                    "If you have experience with these, make sure they're mentioned in your resume."
                )
        
        # Low score suggestions
        if overall_score < 60:
            suggestions.append(
                "Overall score is below average. Consider revising your resume to better align "
                "with the job description. Use keywords from the job posting."
            )
        elif overall_score < 80:
            suggestions.append(
                "Score is good but can be improved. Focus on adding missing skills and "
                "emphasizing relevant experience more prominently."
            )

        # Semantic similarity suggestions
        if semantic_score < 60:
            suggestions.append(
                "Improve semantic alignment: mirror phrasing from the job description, add role-specific "
                "keywords in context, and ensure your summary and bullet points reflect the responsibilities."
            )
        
        # Experience suggestions
        required_years = job_data.get('experience_years', 0)
        if required_years > 0:
            resume_exp = resume_data.get('experience', [])
            if len(resume_exp) == 0:
                suggestions.append(
                    f"The job requires {required_years} years of experience. "
                    "Make sure your experience section is clearly formatted and visible."
                )
        
        # Keyword optimization
        if len(resume_data.get('keywords', set())) < 20:
            suggestions.append(
                "Add more relevant keywords and industry-specific terms from the job description "
                "to improve ATS parsing."
            )
        
        # General formatting
        suggestions.append(
            "Ensure your resume uses standard formatting with clear sections: "
            "Skills, Experience, Education. Avoid graphics and complex layouts that ATS systems can't parse."
        )
        
        return suggestions

