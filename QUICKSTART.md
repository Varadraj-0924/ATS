# Quick Start Guide

## Web Application Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python backend/app.py
```

### 3. Open Browser
Navigate to: `http://localhost:5000`

### 4. Use the Application
1. Upload your resume (PDF or DOCX)
2. Paste the job description
3. Click "Analyze Resume"
4. View your ATS score and recommendations

## CLI Version (Alternative)

If you prefer command-line:
```bash
python backend/main.py
```

Or with files:
```bash
python backend/main.py resume.pdf job_description.txt
```

## Troubleshooting

**Port 5000 already in use?**
Edit `backend/app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Database errors?**
The database is created automatically on first run. If you need to reset it:
```bash
# Delete the database file
rm backend/ats_scorer.db  # Linux/Mac
del backend\\ats_scorer.db  # Windows

# Restart the app (it will recreate the database)
python backend/app.py
```


