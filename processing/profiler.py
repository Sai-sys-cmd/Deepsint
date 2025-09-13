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
                
                doc_emb =  co.embed(
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
# print("?")
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict

def cluster_profiles_from_modalities(pfp: Dict[int, list],
                                     meta: Dict[int, list],
                                     w_meta: float = 0.7,
                                     w_pfp: float  = 0.3,
                                     dbscan_eps: float = 0.5,
                                     dbscan_min_samples: int = 1):
    #index mapping
    profile_ids = sorted(set(list(meta.keys()) + list(pfp.keys())))
    id_to_idx = {pid: idx for idx, pid in enumerate(profile_ids)}
    n = len(profile_ids)

    #compute pairwise similarities per-modality (symmetric)
    sim_meta = np.zeros((n, n))
    sim_meta_mask = np.zeros((n, n), dtype=float) #1 if available
    sim_pfp = np.zeros((n, n))
    sim_pfp_mask = np.zeros((n, n), dtype=float)

    for i, pid_i in enumerate(profile_ids):
        for j in range(i+1, n):
            pid_j = profile_ids[j]
            #meta
            if pid_i in meta and pid_j in meta:
                s = cosine_similarity_numpy(meta[pid_i], meta[pid_j])
                sim_meta[i, j] = sim_meta[j, i] = s
                sim_meta_mask[i, j] = sim_meta_mask[j, i] = 1.0
            #pfp
            if pid_i in pfp and pid_j in pfp:
                s = cosine_similarity_numpy(pfp[pid_i], pfp[pid_j])
                sim_pfp[i, j] = sim_pfp[j, i] = s
                sim_pfp_mask[i, j] = sim_pfp_mask[j, i] = 1.0

    #Combine similarities with weights, ignoring missing modalities
    combined_sim = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            num = w_meta * sim_meta[i, j] * sim_meta_mask[i, j] + w_pfp * sim_pfp[i, j] * sim_pfp_mask[i, j]
            denom = w_meta * sim_meta_mask[i, j] + w_pfp * sim_pfp_mask[i, j]
            if denom == 0:
                combined_sim[i, j] = 0.0   # no info between these two profiles
            else:
                combined_sim[i, j] = num / denom

    #convert similarity -> distance (DBSCAN with precomputed distances)
    dist = 1.0 - combined_sim
    #Ensure diagonal is zero
    np.fill_diagonal(dist, 0.0)

    #cluster with DBSCAN on the precomputed distance matrix
    clustering = DBSCAN(metric="precomputed", eps=dbscan_eps, min_samples=dbscan_min_samples)
    labels = clustering.fit_predict(dist)

    #return mapping profile_id -> label and grouped clusters
    pid_to_label = {pid: int(labels[idx]) for pid, idx in id_to_idx.items()}
    clusters = defaultdict(list)
    for pid, lbl in pid_to_label.items():
        clusters[lbl].append(pid)

    return pid_to_label, dict(clusters), combined_sim, dist

pid_to_label, clusters, combined_sim, dist = cluster_profiles_from_modalities(pfp, meta)
print("clusters (label -> profile ids):")
for lbl, ids in clusters.items():
    print(lbl, ids)

# print(clusters)

# print(cluster_profiles(pfp,meta))
# print(cosine_similarity_numpy(meta[1],meta[2]))
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