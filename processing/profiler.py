from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Set
import os, hashlib, json, time, asyncio

import cohere
co = cohere.Client('wIS7zJGenliZH7ds8jlFoilLIFpFNvwd5t5EDeIR') # This is your trial API key

# response = co.embed(
#   model='embed-v4.0',
#   texts=[""],
#   input_type='classification',
#   truncate='NONE'
# )
# print('Embeddings: {}'.format(response.embeddings))

try:
    from sentence_transformers import SentenceTransformer
    st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    st_model = None

@dataclass
class Profile:
    platform: str
    url : str
    handle : Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    links: List[str] = None
    avatar_url: Optional[str] = None
    page_title: Optional[str] = None
    page_text: Optional[str] = None
    domain: Optional[str] = None
    
def embed_text(text):
    if st_model is None:
        #Simple text embedding with has for now
        h = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in h[:64]] + [0.0] * (384 - 64)
    return st_model.encode([text],normalize_embeddings=True)[0].tolist()

# val1 =embed_text("This is a test!")
# val2 = embed_text("This")
# print("\n")
# print(len(val1))
# print(len(val2)) 
# print(embed_text("This is a test!"))