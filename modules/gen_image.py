import os
import requests
import json

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
API_URL = "https://api.thucchien.ai/images/generations"

def generate_image(prompt, model="imagen-4", n=1, aspect_ratio="1:1"):
    """
    Generates an image using the AI Thuc Chien API.
    """
    if not API_KEY:
        raise ValueError("API key not found. Please set the AITHUCCHIEN_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "model": model,
        "n": n,
        "aspect_ratio": aspect_ratio
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        json_response = response.json()
        if json_response and json_response.get("data"):
            return json_response["data"][0]["b64_json"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    prompt_text = "a digital render of a massive skyscraper, modern, grand, epic with a beautiful sunset in the background "
    image_data = generate_image(prompt_text, model="imagen-4", n=1, aspect_ratio="1:1")
    if image_data:
        print(image_data)
        # You would typically decode the base64 string and save it as an image file
