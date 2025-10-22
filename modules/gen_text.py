import os
import requests
import json

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
API_URL = "https://api.thucchien.ai/chat/completions"

def generate_text(user_prompt, system_prompt="You are a helpful assistant.", model="gemini-2.5-flash"):
    """
    Generates text using the AI Thuc Chien Chat Completions API.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Extract the content from the response
        json_response = response.json()
        if json_response and json_response.get("choices"):
            return json_response["choices"][0]["message"]["content"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error generating text: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    prompt_text = "Hãy viết một câu giới thiệu về Việt Nam."
    generated_text = generate_text(prompt_text, system_prompt="Bạn là một trợ lý ảo")
    if generated_text:
        print(generated_text)
