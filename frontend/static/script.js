// File upload handling
const fileInput = document.getElementById('resume');
const fileName = document.getElementById('fileName');

fileInput.addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        fileName.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        fileName.classList.add('show');
    } else {
        fileName.classList.remove('show');
    }
});

// Drag and drop
const fileUploadLabel = document.querySelector('.file-upload-label');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    fileUploadLabel.style.borderColor = '#6366f1';
    fileUploadLabel.style.background = '#f0f4ff';
}

function unhighlight(e) {
    fileUploadLabel.style.borderColor = '#e2e8f0';
    fileUploadLabel.style.background = '#f8fafc';
}

fileUploadLabel.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    
    if (files.length > 0) {
        const file = files[0];
        fileName.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        fileName.classList.add('show');
    }
}

// Form submission
document.getElementById('analyzeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    
    // Reset UI
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
    analyzeBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'An error occurred');
        }
        
        // Display results
        displayResults(data.results);
        
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    } finally {
        analyzeBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
});

function displayResults(results) {
    // Overall score
    const overallScore = Math.round(results.overall_score);
    document.getElementById('overallScore').textContent = overallScore;
    document.getElementById('scoreFill').style.width = overallScore + '%';
    
    // Component scores
    document.getElementById('skillsScore').textContent = Math.round(results.skills_score) + '/100';
    document.getElementById('keywordsScore').textContent = Math.round(results.keywords_score) + '/100';
    document.getElementById('experienceScore').textContent = Math.round(results.experience_score) + '/100';
    document.getElementById('educationScore').textContent = Math.round(results.education_score) + '/100';
    
    // Matched skills
    const matchedSkillsDiv = document.getElementById('matchedSkills');
    matchedSkillsDiv.innerHTML = '';
    if (results.matched_skills && results.matched_skills.length > 0) {
        results.matched_skills.slice(0, 20).forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge';
            badge.textContent = skill;
            matchedSkillsDiv.appendChild(badge);
        });
        if (results.matched_skills.length > 20) {
            const more = document.createElement('span');
            more.className = 'skill-badge';
            more.textContent = `+${results.matched_skills.length - 20} more`;
            matchedSkillsDiv.appendChild(more);
        }
    } else {
        matchedSkillsDiv.innerHTML = '<p style="color: var(--text-secondary);">No matched skills found.</p>';
    }
    
    // Missing skills
    const missingSkillsDiv = document.getElementById('missingSkills');
    missingSkillsDiv.innerHTML = '';
    if (results.missing_skills && results.missing_skills.length > 0) {
        results.missing_skills.slice(0, 20).forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge';
            badge.textContent = skill;
            missingSkillsDiv.appendChild(badge);
        });
        if (results.missing_skills.length > 20) {
            const more = document.createElement('span');
            more.className = 'skill-badge';
            more.textContent = `+${results.missing_skills.length - 20} more`;
            missingSkillsDiv.appendChild(more);
        }
    } else {
        missingSkillsDiv.innerHTML = '<p style="color: var(--text-secondary);">Great! No missing skills.</p>';
    }
    
    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    results.strengths.forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        strengthsList.appendChild(li);
    });
    
    // Suggestions
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    results.suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });
    
    // Show results
    document.getElementById('results').style.display = 'block';
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetForm() {
    document.getElementById('analyzeForm').reset();
    document.getElementById('fileName').classList.remove('show');
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('jobDescription').focus();
}


