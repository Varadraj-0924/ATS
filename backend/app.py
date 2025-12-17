"""
Flask Web Application - ATS Resume Scorer API
"""
from pathlib import Path
import os
import sqlite3
import sys
import uuid
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'
sys.path.insert(0, str(BASE_DIR))

from resume_parser import ResumeParser
from job_parser import JobDescriptionParser
from ats_scorer import ATSScorer

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / 'templates'),
    static_folder=str(FRONTEND_DIR / 'static'),
    static_url_path='/static'
)
CORS(app)

# Configuration
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
DB_PATH = BASE_DIR / 'ats_scorer.db'

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize parsers and scorer
resume_parser = ResumeParser()
job_parser = JobDescriptionParser()
scorer = ATSScorer()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create scores table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id TEXT PRIMARY KEY,
            filename TEXT,
            job_description TEXT,
            overall_score REAL,
            skills_score REAL,
            keywords_score REAL,
            experience_score REAL,
            education_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analysis table
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id TEXT PRIMARY KEY,
            score_id TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            strengths TEXT,
            suggestions TEXT,
            FOREIGN KEY (score_id) REFERENCES scores(id)
        )
    ''')
    
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """API endpoint to analyze resume against job description"""
    try:
        # Check if resume file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_description.strip():
            return jsonify({'error': 'Job description is required'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF or DOCX'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Parse resume
            resume_data = resume_parser.parse(filepath)
            
            # Parse job description
            job_data = job_parser.extract_requirements(job_description)
            
            # Calculate score
            score_results = scorer.calculate_score(resume_data, job_data)
            
            # Save to database
            score_id = str(uuid.uuid4())
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Insert score
            c.execute('''
                INSERT INTO scores (id, filename, job_description, overall_score, 
                                  skills_score, keywords_score, experience_score, education_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                score_id, filename, job_description[:500], score_results['overall_score'],
                score_results['skills_score'], score_results['keywords_score'],
                score_results['experience_score'], score_results['education_score']
            ))
            
            # Insert analysis
            import json
            c.execute('''
                INSERT INTO analysis (id, score_id, matched_skills, missing_skills, strengths, suggestions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), score_id,
                json.dumps(list(score_results['matched_skills'])),
                json.dumps(score_results['missing_skills']),
                json.dumps(score_results['strengths']),
                json.dumps(score_results['suggestions'])
            ))
            
            conn.commit()
            conn.close()
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify({
                'success': True,
                'score_id': score_id,
                'results': score_results
            })
            
        except Exception as e:
            # Clean up on error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint to get analysis history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        limit = request.args.get('limit', 10, type=int)
        
        c.execute('''
            SELECT s.*, a.matched_skills, a.missing_skills, a.strengths, a.suggestions
            FROM scores s
            LEFT JOIN analysis a ON s.id = a.score_id
            ORDER BY s.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        import json
        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'filename': row['filename'],
                'overall_score': row['overall_score'],
                'created_at': row['created_at'],
                'matched_skills': json.loads(row['matched_skills']) if row['matched_skills'] else [],
                'missing_skills': json.loads(row['missing_skills']) if row['missing_skills'] else []
            })
        
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        return jsonify({'error': f'Error fetching history: {str(e)}'}), 500


@app.route('/api/score/<score_id>', methods=['GET'])
def get_score(score_id):
    """API endpoint to get specific score details"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT s.*, a.matched_skills, a.missing_skills, a.strengths, a.suggestions
            FROM scores s
            LEFT JOIN analysis a ON s.id = a.score_id
            WHERE s.id = ?
        ''', (score_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Score not found'}), 404
        
        import json
        result = {
            'id': row['id'],
            'filename': row['filename'],
            'overall_score': row['overall_score'],
            'skills_score': row['skills_score'],
            'keywords_score': row['keywords_score'],
            'experience_score': row['experience_score'],
            'education_score': row['education_score'],
            'created_at': row['created_at'],
            'matched_skills': json.loads(row['matched_skills']) if row['matched_skills'] else [],
            'missing_skills': json.loads(row['missing_skills']) if row['missing_skills'] else [],
            'strengths': json.loads(row['strengths']) if row['strengths'] else [],
            'suggestions': json.loads(row['suggestions']) if row['suggestions'] else []
        }
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'error': f'Error fetching score: {str(e)}'}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)


