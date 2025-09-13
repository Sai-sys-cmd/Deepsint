import cohere
import os
from dotenv import load_dotenv
import json
def summarize_cluster_full(links, file_path, username):
    #Takes the index values of the json's as input to summarize
    #Summarizes the profile as a whole. 
    system_message = f"You are an assistant specializing in extracting key personal details from public online profiles. You will be given various data from websites. Your task is to extract important facts about the user’s activities, interests, affiliations, and any other relevant information. Avoid mentioning the websites or platforms unless necessary to understand the context."


    chunked_documents = []
    
    for index in links:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = ""
            data = json.load(f)
            
            if data[index]["page_title"]:
                text += f"{data[index]['page_title']}."
            if data[index]["domain"]:
                text += f"The user, {username} has an account for {data[index]['domain']}."
            if data[index]["page_text"]:
                text += f"Here is some user information: {data[index]['page_text']}"
            
            chunked_documents.append({"data": {"text": text}})

    load_dotenv()
    api_key = os.getenv("COHERE_API_KEY")
    co = cohere.ClientV2(api_key=api_key)
    
    message = f"Summarize the key details about the user based on the provided data, highlighting their activities, interests, potential age (based on account creation), affiliations, or any other relevant FACTUAL personal information. Keep it concise—2-3 sentences, and avoid including website names unless essential."

    response = co.chat(
        model="command-a-03-2025",
        documents=chunked_documents,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ],
    )
    return response.message.content[0].text



# print(summarize_cluster_full([0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12],r"C:\Users\Tristan\Downloads\HTN2025\generic_scrape_results.json","LordFurno" ))

