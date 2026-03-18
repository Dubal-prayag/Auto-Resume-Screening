# utils/scorer.py
# SEMANTIC AI SCORING — BATCH OPTIMIZED VERSION
# Encodes all resumes in a single batch for speed (instead of one-by-one),
# and uses RAW text (not preprocessed) for maximum embedding accuracy.

from sentence_transformers import SentenceTransformer, util
import math

# Load model globally so it only loads ONCE per session startup
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load sentence-transformers ({e})")
    model = None


def compute_similarity(jd_text: str, resume_text: str) -> float:
    """
    Compute semantic cosine similarity between JD and one resume.
    Always call with RAW (unprocessed) text for best results.
    Returns a score from 0.0 to 100.0.
    """
    if not jd_text.strip() or not resume_text.strip() or model is None:
        return 0.0
    try:
        jd_emb     = model.encode(jd_text,     convert_to_tensor=True)
        resume_emb = model.encode(resume_text,  convert_to_tensor=True)
        raw_score  = util.cos_sim(jd_emb, resume_emb)[0][0].item()
        return round(math.sqrt(max(0.0, raw_score)) * 100, 2)
    except Exception:
        return 0.0


def rank_resumes(jd_text: str, resumes_dict: dict) -> list:
    """
    Rank multiple resumes against a job description.
    Uses BATCH encoding for speed — all resumes encoded in one call.

    Args:
        jd_text      : RAW (unprocessed) job description text
        resumes_dict : {filename: raw_resume_text}

    Returns:
        List of dicts sorted by score descending:
        [{'resume': filename, 'score': float}, ...]
    """
    if model is None or not resumes_dict:
        return [{'resume': f, 'score': 0.0} for f in resumes_dict]

    filenames   = list(resumes_dict.keys())
    raw_texts   = list(resumes_dict.values())
    all_texts   = [jd_text] + raw_texts

    # Encode everything in ONE batch — significantly faster than encoding one at a time
    embeddings  = model.encode(all_texts, convert_to_tensor=True, batch_size=32, show_progress_bar=False)
    jd_emb      = embeddings[0]
    resume_embs = embeddings[1:]

    scores = []
    for i, filename in enumerate(filenames):
        raw_score     = util.cos_sim(jd_emb, resume_embs[i])[0][0].item()
        boosted_score = round(math.sqrt(max(0.0, raw_score)) * 100, 2)
        scores.append({'resume': filename, 'score': boosted_score})

    return sorted(scores, key=lambda x: x['score'], reverse=True)