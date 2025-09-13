from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Set
import os, hashlib, json, time, asyncio
import base64
# from scraper import 
import cohere
import requests

def image_to_base64_data_url(image_path: str):
    _, file_extension = os.path.splitext(image_path)
    file_type = file_extension[1:] #Remove the .
    with open(image_path, "rb") as f:
        enc_img = base64.b64encode(f.read()).decode("utf-8")
        enc_img = f"data:image/{file_type};base64,{enc_img}"
    return enc_img


def download_image(image_url: str, save_path: str):
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
        
            

def calculate_cohere_embeddings(file_path: str):
    co = cohere.ClientV2(api_key = 'API_KEY')
    pfp_embeds = {}
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
        for i in range(len(data)):
            pfp_image_url = data[i]["avatar_url"]
            if pfp_image_url:
                #Not null
                # temp_image_path = r"HTN-2025\TMP\image" + pfp_image_url
                download_image(pfp_image_url, r"C:\Users\Tristan\Downloads\HTN2025\TMP\image.png")
                base64_url = image_to_base64_data_url(r"C:\Users\Tristan\Downloads\HTN2025\TMP\image.png")
                image_input = {
                    "content": [
                        {"type": "image_url", "image_url": {"url": base64_url}}
                    ]
                    
                }
                image_embed = co.embed(
                    model="embed-v4.0",
                    inputs=[image_input],
                    input_type="search_document",
                    embedding_types=["float"],
                )
                pfp_embeds[i] = image_embed
                # break
calculate_cohere_embeddings("generic_scrape_results.json")
    


# response = co.embed(
#   model='embed-v4.0',
#   texts=[""],
#   input_type='classification',
#   truncate='NONE'
# )
# print('Embeddings: {}'.format(response.embeddings))

# try:
#     from sentence_transformers import SentenceTransformer
#     st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# except Exception:
#     st_model = None

# @dataclass
# class Profile:
#     platform: str
#     url : str
#     handle : Optional[str] = None
#     display_name: Optional[str] = None
#     bio: Optional[str] = None
#     location: Optional[str] = None
#     links: List[str] = None
#     avatar_url: Optional[str] = None
#     page_title: Optional[str] = None
#     page_text: Optional[str] = None
#     domain: Optional[str] = None
    
# def embed_text(text):
#     if st_model is None:
#         #Simple text embedding with has for now
#         h = hashlib.sha256(text.encode()).digest()
#         return [b / 255.0 for b in h[:64]] + [0.0] * (384 - 64)
#     return st_model.encode([text],normalize_embeddings=True)[0].tolist()

# val1 =embed_text("This is a test!")
# val2 = embed_text("This")
# print("\n")
# print(len(val1))
# print(len(val2)) 
# print(embed_text("This is a test!"))