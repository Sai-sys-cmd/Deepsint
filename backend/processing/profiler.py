from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Set
import os, hashlib, json, time, asyncio
import base64
from dotenv import load_dotenv
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
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
    try:    
        response.raise_for_status()
    except:
        return False
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return True
        
            

def calculate_cohere_embeddings(file_path: str):
    load_dotenv(dotenv_path=r"C:\Users\Tristan\Downloads\HTN2025\HTN-2025\processing\.env")
    api_key = os.getenv("COHERE_API_KEY")

    co = cohere.ClientV2(api_key = api_key)
    pfp_embeds = {}
    metadata_embeds = {}
    
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
        for i in range(len(data)):
            if data[i]["scrape_status"] == "ok": #Has to be okay, not auth blocked
                pfp_image_url = data[i]["avatar_url"]
                if pfp_image_url:
                    
                    #Not null
                    # temp_image_path = r"HTN-2025\TMP\image" + pfp_image_url
                    test = download_image(pfp_image_url, r"C:\Users\Tristan\Downloads\HTN2025\TMP\image.png")
                    if not test:
                        continue
                    base64_url = image_to_base64_data_url(r"C:\Users\Tristan\Downloads\HTN2025\TMP\image.png")
                    image_input = {
                        "content": [
                            {"type": "image_url", "image_url": {"url": base64_url}}
                        ]
                        
                    }
                    image_embed = co.embed(
                        model="embed-v4.0",
                        output_dimension=1024,
                        inputs=[image_input],
                        input_type="search_document",
                        embedding_types=["float"],
                    )
                    pfp_embeds[i] = image_embed.embeddings.float[0]
                
                metadata = ""
                for dataType in ["page_title","bio", "page_text"]:
                    if dataType == "links":
                        for link in data[i][dataType]:
                            metadata += link  
                    elif data[i][dataType]:
                        #Not null
                        metadata += data[i][dataType]
                        
                embed_input = [
                    {
                        "content": [
                            {"type": "text", "text": metadata},
                        ]
                    },
                ]
                
                doc_emb = co.embed(
                    inputs=embed_input,
                    model="embed-v4.0",
                    output_dimension=1024,
                    input_type="search_document",
                    embedding_types=["float"],
                )
                metadata_embeds[i] = doc_emb.embeddings.float[0]

                # break
        # print(pfp_embeds.keys())
        
        # for key in pfp_embeds.keys():            
            # print(pfp_embeds[key])

        # for key in metadata_embeds.keys():
            # print(len(metadata_embeds[key]))
            # break
 
    return pfp_embeds, metadata_embeds


import numpy as np
from numpy.linalg import norm

def cosine_similarity_numpy(vec1, vec2):
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    return np.dot(vec1_np, vec2_np) / (norm(vec1_np) * norm(vec2_np))


pfp, meta = calculate_cohere_embeddings("generic_scrape_results.json")
# print(cluster_profiles(pfp,meta))
print(cosine_similarity_numpy(meta[1],meta[2]))
print(pfp.keys())
print(meta.keys())

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