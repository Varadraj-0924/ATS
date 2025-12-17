# How to Run ATS Resume Scorer

## Setup (First Time Only)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install spaCy Language Model (Optional but Recommended)
```bash
python -m spacy download en_core_web_sm
```
**Note:** If this fails, the application will still work but with limited keyword extraction.

---

## Running the Application

### Method 1: Interactive Mode (Recommended for first-time users)
```bash
python backend/main.py
```
Then follow the prompts:
1. Enter path to your resume file (PDF or DOCX)
2. Paste the job description (or press Enter twice to finish)

### Method 2: Command Line Arguments
```bash
python backend/main.py "path/to/resume.pdf" "path/to/job_description.txt"
```

### Method 3: Resume Only (paste job description)
```bash
python backend/main.py "path/to/resume.pdf"
```
Then paste the job description when prompted.

---

## Example Usage

```bash
# Example 1: Interactive mode
python backend/main.py

# Example 2: With resume and job description files
python backend/main.py resume.pdf job_description.txt

# Example 3: With resume file only
python backend/main.py "C:\Users\YourName\Documents\resume.pdf"
```

---

## Output

The application will:
1. Parse your resume
2. Analyze the job description
3. Calculate scores
4. Display a detailed report
5. Optionally save the report to a file

---

## Troubleshooting

**If you get import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`

**If resume parsing fails:**
- Ensure your resume is in PDF or DOCX format
- Check that the file path is correct

**If spaCy model installation fails:**
- The application will still work, just with basic keyword extraction
- You can ignore this error and proceed


