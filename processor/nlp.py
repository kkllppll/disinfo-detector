from sentence_transformers import SentenceTransformer
import numpy as np


_model = None

def get_model():
    global _model
    if _model is None:
        print("Завантаження NLP моделі...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("Модель готова!")
    return _model

def vectorize_text(text):
    #повертає вектор для тексту
    model = get_model()
    if not text or len(text.strip()) < 10:
        return None
    embedding = model.encode(text[:512], convert_to_numpy=True)
    return embedding.tolist()

def cosine_similarity(vec1, vec2):
    #схожість між двома векторами
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))