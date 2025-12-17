"""
Machine Learning utilities for semantic similarity between resume and job description.
Uses TF-IDF vectorization and cosine similarity.
"""
from typing import Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_semantic_similarity(resume_text: str, job_text: str) -> float:
    """
    Compute semantic similarity (0-100) between resume and job description text.

    Uses TF-IDF (unigrams + bigrams) with English stop words removed.
    Returns a score in the range [0, 100]. In case of any error, returns 0.
    """
    resume_text = (resume_text or "").strip()
    job_text = (job_text or "").strip()

    if not resume_text or not job_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )
        tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])

        # Compute cosine similarity between job description (row 0) and resume (row 1)
        similarity_matrix: np.ndarray = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        similarity = float(similarity_matrix[0][0])

        return round(similarity * 100, 2)
    except Exception:
        return 0.0


