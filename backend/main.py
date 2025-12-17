"""
Main Application - ATS Resume Scorer
Run this script to analyze a resume against a job description
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from resume_parser import ResumeParser
from job_parser import JobDescriptionParser
from ats_scorer import ATSScorer


def print_report(score_results: dict):
    """Print a formatted report of the ATS score analysis"""
    print("\n" + "="*70)
    print(" " * 20 + "ATS RESUME SCORE REPORT")
    print("="*70 + "\n")
    
    # Overall Score
    overall = score_results['overall_score']
    score_bar = "█" * int(overall / 2) + "░" * (50 - int(overall / 2))
    print(f"OVERALL SCORE: {overall}/100")
    print(f"[{score_bar}]")
    print()
    
    # Component Scores
    print("Component Scores:")
    print(f"  • Skills Match:        {score_results['skills_score']:.1f}/100")
    print(f"  • Keywords Match:      {score_results['keywords_score']:.1f}/100")
    print(f"  • Experience Match:    {score_results['experience_score']:.1f}/100")
    print(f"  • Education Match:     {score_results['education_score']:.1f}/100")
    print()
    
    # Matched Skills
    if score_results['matched_skills']:
        print("✓ MATCHED SKILLS:")
        matched_list = list(score_results['matched_skills'])[:10]
        for skill in matched_list:
            print(f"  • {skill}")
        if len(score_results['matched_skills']) > 10:
            print(f"  ... and {len(score_results['matched_skills']) - 10} more")
        print()
    
    # Missing Skills
    if score_results['missing_skills']:
        print("✗ MISSING SKILLS:")
        missing_list = list(score_results['missing_skills'])[:10]
        for skill in missing_list:
            print(f"  • {skill}")
        if len(score_results['missing_skills']) > 10:
            print(f"  ... and {len(score_results['missing_skills']) - 10} more")
        print()
    
    # Strengths
    print("STRENGTHS:")
    for strength in score_results['strengths']:
        print(f"  ✓ {strength}")
    print()
    
    # Suggestions
    print("IMPROVEMENT SUGGESTIONS:")
    for i, suggestion in enumerate(score_results['suggestions'], 1):
        print(f"  {i}. {suggestion}")
    print()
    
    print("="*70 + "\n")


def main():
    """Main function to run the ATS Resume Scorer"""
    print("\n" + "="*70)
    print(" " * 25 + "ATS RESUME SCORER")
    print("="*70 + "\n")
    
    # Get resume file path
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        resume_path = input("Enter path to resume file (PDF or DOCX): ").strip().strip('"')
    
    if not os.path.exists(resume_path):
        print(f"Error: Resume file not found at {resume_path}")
        return
    
    # Get job description
    if len(sys.argv) > 2:
        job_desc_path = sys.argv[2]
        if os.path.exists(job_desc_path):
            with open(job_desc_path, 'r', encoding='utf-8') as f:
                job_description = f.read()
        else:
            print(f"Error: Job description file not found at {job_desc_path}")
            return
    else:
        print("\nEnter job description (paste and press Enter twice when done):")
        lines = []
        empty_line_count = 0
        while empty_line_count < 2:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
            else:
                empty_line_count = 0
                lines.append(line)
        job_description = "\n".join(lines)
    
    if not job_description.strip():
        print("Error: Job description cannot be empty")
        return
    
    # Parse resume
    print("\n📄 Parsing resume...")
    try:
        resume_parser = ResumeParser()
        resume_data = resume_parser.parse(resume_path)
        print(f"✓ Resume parsed successfully!")
        print(f"  Found {len(resume_data['skills'])} skills")
        print(f"  Found {len(resume_data['experience'])} experience entries")
        print(f"  Found {len(resume_data['education'])} education entries")
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        return
    
    # Parse job description
    print("\n📋 Parsing job description...")
    try:
        job_parser = JobDescriptionParser()
        job_data = job_parser.extract_requirements(job_description)
        print(f"✓ Job description parsed successfully!")
        print(f"  Found {len(job_data['skills'])} required skills")
        print(f"  Found {len(job_data['keywords'])} keywords")
        if job_data['experience_years'] > 0:
            print(f"  Requires {job_data['experience_years']} years of experience")
    except Exception as e:
        print(f"Error parsing job description: {str(e)}")
        return
    
    # Calculate score
    print("\n🔍 Calculating ATS score...")
    try:
        scorer = ATSScorer()
        score_results = scorer.calculate_score(resume_data, job_data)
        print("✓ Score calculated successfully!")
    except Exception as e:
        print(f"Error calculating score: {str(e)}")
        return
    
    # Print report
    print_report(score_results)
    
    # Optionally save report to file
    save_report = input("Save report to file? (y/n): ").strip().lower()
    if save_report == 'y':
        output_file = input("Enter output file name (default: ats_report.txt): ").strip()
        if not output_file:
            output_file = "ats_report.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ATS RESUME SCORE REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"OVERALL SCORE: {score_results['overall_score']}/100\n\n")
            f.write("Component Scores:\n")
            f.write(f"  Skills Match:     {score_results['skills_score']:.1f}/100\n")
            f.write(f"  Keywords Match:   {score_results['keywords_score']:.1f}/100\n")
            f.write(f"  Experience Match: {score_results['experience_score']:.1f}/100\n")
            f.write(f"  Education Match:  {score_results['education_score']:.1f}/100\n\n")
            
            if score_results['matched_skills']:
                f.write("MATCHED SKILLS:\n")
                for skill in score_results['matched_skills']:
                    f.write(f"  • {skill}\n")
                f.write("\n")
            
            if score_results['missing_skills']:
                f.write("MISSING SKILLS:\n")
                for skill in score_results['missing_skills']:
                    f.write(f"  • {skill}\n")
                f.write("\n")
            
            f.write("STRENGTHS:\n")
            for strength in score_results['strengths']:
                f.write(f"  • {strength}\n")
            f.write("\n")
            
            f.write("IMPROVEMENT SUGGESTIONS:\n")
            for i, suggestion in enumerate(score_results['suggestions'], 1):
                f.write(f"  {i}. {suggestion}\n")
        
        print(f"\n✓ Report saved to {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


