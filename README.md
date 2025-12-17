# ATS Resume Scorer

A comprehensive Applicant Tracking System (ATS) Resume Scorer web application that analyzes resumes against job descriptions and provides detailed scoring, missing skills identification, strengths summary, and improvement suggestions.

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#️-setup--installation)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Database Schema](#️-database-schema)
- [How It Works](#-how-it-works)
- [Usage Tips](#-usage-tips)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)

## 🚀 Features

- ✅ **Web-Based Interface**: Modern, responsive UI with drag-and-drop file upload
- ✅ **Resume Parsing**: Supports PDF and DOCX formats
- ✅ **Intelligent Analysis**: Extracts skills, experience, education, and keywords
- ✅ **Detailed Scoring**: Component-based scoring system (Skills, Keywords, Experience, Education)
- ✅ **Actionable Insights**: Missing skills, strengths, and improvement suggestions
- ✅ **History Tracking**: Database storage of previous analyses
- ✅ **RESTful API**: Complete API for programmatic access

## 📋 Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 3.0.0**: Web framework for API and server
- **Flask-CORS 4.0.0**: Cross-origin resource sharing support
- **SQLite3**: Lightweight database for storing analysis history
- **pdfplumber 0.10.3**: PDF text extraction
- **python-docx 1.1.0**: DOCX file parsing
- **PyPDF2 3.0.1**: Additional PDF processing support
- **scikit-learn 1.3.2**: Machine learning utilities
- **nltk 3.8.1**: Natural language processing

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Client-side interactivity
- **Fetch API**: RESTful API communication

### Architecture
- **MVC Pattern**: Model-View-Controller separation
- **RESTful API**: Standard HTTP methods and status codes
- **SQLite Database**: File-based relational database

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd ATS

# Or download and extract the project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

The database will be automatically created on first run. Alternatively, you can initialize it manually:

```python
python -c "from backend.app import init_db; init_db()"
```

### Step 5: Run the Application

```bash
python backend/app.py
```

The application will start on `http://localhost:5000`

### Step 6: Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
ATS/
├── backend/               # Backend application code
│   ├── app.py             # Flask application and API endpoints
│   ├── resume_parser.py   # Resume parsing logic
│   ├── job_parser.py      # Job description parsing logic
│   ├── ats_scorer.py      # Scoring algorithm and analysis
│   ├── ml_model.py        # Semantic similarity helper
│   ├── main.py            # CLI version (optional)
│   ├── ats_scorer.db      # SQLite database (created automatically)
│   └── uploads/           # Temporary file uploads (created automatically)
├── frontend/              # Frontend assets
│   ├── templates/
│   │   └── index.html     # Main HTML template
│   └── static/
│       ├── style.css      # CSS stylesheet
│       └── script.js      # JavaScript for frontend functionality
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── QUICKSTART.md          # Quick setup guide
└── RUN.md                 # CLI usage guide
```

## 🔌 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Analyze Resume
Analyzes a resume against a job description.

**Endpoint:** `POST /api/analyze`

**Content-Type:** `multipart/form-data`

**Request Parameters:**
- `resume` (file, required): Resume file (PDF or DOCX, max 16MB)
- `job_description` (string, required): Job description text

**Response (Success - 200):**
```json
{
  "success": true,
  "score_id": "uuid-string",
  "results": {
    "overall_score": 78.5,
    "skills_score": 85.0,
    "keywords_score": 72.0,
    "experience_score": 90.0,
    "education_score": 100.0,
    "missing_skills": ["Docker", "Kubernetes", "AWS"],
    "matched_skills": ["Python", "JavaScript", "React"],
    "strengths": [
      "Strong technical skills match (8 skills aligned)",
      "Good keyword alignment (15 keywords match)"
    ],
    "suggestions": [
      "Add missing key skills: Docker, AWS, Kubernetes...",
      "Add more relevant keywords from the job description"
    ]
  }
}
```

**Response (Error - 400/500):**
```json
{
  "error": "Error message description"
}
```

#### 2. Get Analysis History
Retrieves previous analysis results.

**Endpoint:** `GET /api/history`

**Query Parameters:**
- `limit` (integer, optional): Number of records to return (default: 10)

**Response (200):**
```json
{
  "success": true,
  "history": [
    {
      "id": "uuid-string",
      "filename": "resume.pdf",
      "overall_score": 78.5,
      "created_at": "2024-12-16 20:30:45",
      "matched_skills": ["Python", "JavaScript"],
      "missing_skills": ["Docker", "AWS"]
    }
  ]
}
```

#### 3. Get Specific Score
Retrieves detailed information about a specific analysis.

**Endpoint:** `GET /api/score/<score_id>`

**Response (200):**
```json
{
  "success": true,
  "result": {
    "id": "uuid-string",
    "filename": "resume.pdf",
    "overall_score": 78.5,
    "skills_score": 85.0,
    "keywords_score": 72.0,
    "experience_score": 90.0,
    "education_score": 100.0,
    "created_at": "2024-12-16 20:30:45",
    "matched_skills": ["Python", "JavaScript"],
    "missing_skills": ["Docker", "AWS"],
    "strengths": ["..."],
    "suggestions": ["..."]
  }
}
```

**Response (404):**
```json
{
  "error": "Score not found"
}
```

### API Usage Example

#### Using cURL
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Software Engineer position..."
```

#### Using Python
```python
import requests

url = "http://localhost:5000/api/analyze"
files = {'resume': open('resume.pdf', 'rb')}
data = {'job_description': 'Software Engineer position...'}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result)
```

#### Using JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('resume', fileInput.files[0]);
formData.append('job_description', jobDescriptionText);

fetch('/api/analyze', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🗄️ Database Schema

The application uses an SQLite database (`backend/ats_scorer.db`) for persistent storage of analysis results. The database is automatically initialized on first run.

### Database Overview

The database consists of two main tables that store analysis results and detailed insights:
- `scores`: Stores basic score information for each analysis
- `analysis`: Stores detailed analysis results linked to scores

### Schema Details

### Table: `scores`
Stores basic score information for each analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique identifier (UUID) |
| filename | TEXT | NOT NULL | Original resume filename |
| job_description | TEXT | | Job description text (truncated to 500 chars) |
| overall_score | REAL | | Overall ATS score (0-100) |
| skills_score | REAL | | Skills match score (0-100) |
| keywords_score | REAL | | Keywords match score (0-100) |
| experience_score | REAL | | Experience match score (0-100) |
| education_score | REAL | | Education match score (0-100) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Analysis timestamp |

### Table: `analysis`
Stores detailed analysis results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique identifier (UUID) |
| score_id | TEXT | FOREIGN KEY → scores.id | Reference to scores table |
| matched_skills | TEXT | | JSON array of matched skills |
| missing_skills | TEXT | | JSON array of missing skills |
| strengths | TEXT | | JSON array of strength descriptions |
| suggestions | TEXT | | JSON array of improvement suggestions |

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│   scores    │1     1  │   analysis   │
├─────────────┤────────>├──────────────┤
│ id (PK)     │         │ id (PK)      │
│ filename    │         │ score_id(FK) │
│ job_desc    │         │ matched_...  │
│ overall_... │         │ missing_...  │
│ skills_...  │         │ strengths    │
│ keywords_...│         │ suggestions  │
│ experience..│         │              │
│ education.. │         │              │
│ created_at  │         │              │
└─────────────┘         └──────────────┘
```

**Relationship Details:**
- One-to-One relationship: Each score record has exactly one analysis record
- Foreign Key: `analysis.score_id` references `scores.id`
- Cascade behavior: Analysis records are linked but can exist independently

### Database Initialization

The database is automatically created on first run. To manually initialize:

```python
from app import init_db
init_db()
```

Or via command line:
```bash
python -c "from app import init_db; init_db()"
```

### Sample SQL Queries

```sql
-- Get all scores with their analysis (full details)
SELECT s.*, a.matched_skills, a.missing_skills, a.strengths, a.suggestions
FROM scores s
LEFT JOIN analysis a ON s.id = a.score_id
ORDER BY s.created_at DESC;

-- Get average score across all analyses
SELECT AVG(overall_score) as avg_score FROM scores;

-- Get scores by date range
SELECT * FROM scores 
WHERE created_at BETWEEN '2024-12-01' AND '2024-12-31';

-- Get top 10 highest scores
SELECT filename, overall_score, created_at 
FROM scores 
ORDER BY overall_score DESC 
LIMIT 10;

-- Count total analyses
SELECT COUNT(*) as total_analyses FROM scores;

-- Get analysis with most missing skills
SELECT s.filename, s.overall_score, 
       json_array_length(a.missing_skills) as missing_count
FROM scores s
JOIN analysis a ON s.id = a.score_id
ORDER BY missing_count DESC;
```

## 🎯 How It Works

### Scoring Algorithm

The overall score is calculated using weighted components:

1. **Skills Match (35% weight)**
   - Compares required skills from job description with skills found in resume
   - Uses fuzzy matching for similar skill names
   - Calculates percentage of matched skills

2. **Keywords Match (20% weight)**
   - Extracts important keywords from job description
   - Matches keywords found in resume
   - Includes technologies, methodologies, and industry terms

3. **Experience Match (15% weight)**
   - Extracts years of experience requirement from job description
   - Calculates total years from resume work history
   - Scores based on meeting/exceeding requirement

4. **Education Match (10% weight)**
   - Checks educational requirements from job description
   - Matches degrees and qualifications in resume
   - Evaluates alignment with required education level

5. **Semantic Similarity (ML) (20% weight)**
   - TF-IDF (unigram + bigram) vectorization with English stop-word removal
   - Cosine similarity between resume text and job description text
   - Rewards resumes that mirror the language of the job description

### Resume Parsing

The parser extracts:
- **Skills**: Technical and professional skills (from skills section and throughout resume)
- **Experience**: Work history with dates, positions, and descriptions
- **Education**: Degrees, certifications, and educational background
- **Keywords**: Important terms, technologies, and concepts

### Job Description Parsing

The parser identifies:
- **Required Skills**: Technical skills and competencies
- **Experience Requirements**: Years of experience needed
- **Education Requirements**: Degree and qualification requirements
- **Responsibilities**: Key job responsibilities (for context)
- **Keywords**: Important terms and technologies mentioned

## 💡 Usage Tips

1. **Resume Format**: Use ATS-friendly formats (simple layouts, standard fonts)
2. **Keywords**: Include relevant keywords from the job description
3. **Skills Section**: Have a dedicated, clearly formatted skills section
4. **Experience**: Quantify achievements and include measurable results
5. **Tailoring**: Customize your resume for each job application

## 🔧 Configuration

### File Upload Settings
Edit `backend/app.py` to modify:
- `MAX_FILE_SIZE`: Maximum file upload size (default: 16MB)
- `ALLOWED_EXTENSIONS`: Supported file types
- `UPLOAD_FOLDER`: Temporary file storage location

### Database Location
The SQLite database (`ats_scorer.db`) is created inside the `backend/` directory. To change the location, modify `DB_PATH` in `backend/app.py`.

### Server Configuration
Modify the `app.run()` call in `backend/app.py` to change:
- Host address (default: `0.0.0.0`)
- Port number (default: `5000`)
- Debug mode (default: `True` for development)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Errors
```bash
# Delete and recreate database (adjust command for Windows)
rm backend/ats_scorer.db
python -c "from backend.app import init_db; init_db()"
```

### File Upload Issues
- Ensure `backend/uploads/` directory exists and has write permissions
- Check file size is within limits
- Verify file format is PDF or DOCX

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📝 CLI Version

The project also includes a command-line interface. Run:

```bash
python backend/main.py
```

Or with arguments:
```bash
python backend/main.py resume.pdf job_description.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Uses various open-source Python libraries for document processing
- Inspired by the need for better ATS resume optimization tools

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.
