import os
import requests
import json
import time

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
 # The base URL is now different, and we'll construct specific URLs for each step
API_BASE_URL = "https://api.thucchien.ai/gemini/v1beta"

def generate_video(prompt, model="veo-3.0-generate-001", negative_prompt="", aspect_ratio="16:9", resolution="720p", person_generation="allow_all", input_image=None):
    """
    Generates a video using a three-step asynchronous process:
    1. Initiate generation
    2. Poll for status
    3. Download the video
    """
    if not API_KEY:
        raise ValueError("API key not found. Please set the AITHUCCHIEN_API_KEY environment variable.")

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # --- Step 1: Initiate Video Generation ---
    initiate_url = f"{API_BASE_URL}/models/{model}:predictLongRunning"
    initiate_payload = {
        "instances": [{
            "prompt": prompt,
            "image": input_image
        }],
        "parameters": {
            "negativePrompt": negative_prompt,
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
            "personGeneration": person_generation
        }
    }

    try:
        print("Step 1: Initiating video generation...")
        initiate_response = requests.post(initiate_url, headers=headers, json=initiate_payload)
        initiate_response.raise_for_status()
        operation_name = initiate_response.json().get("name")
        if not operation_name:
            print("Error: Could not get operation name from the initial response.")
            return None
        print(f"Successfully initiated. Operation name: {operation_name}")

        # --- Step 2: Poll for Status ---
        status_url = f"{API_BASE_URL}/{operation_name}"
        download_uri = None
        while True:
            print("Step 2: Checking generation status...")
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()

            if status_data.get("done"):
                print("Generation complete!")
                try:
                    download_uri = status_data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                except (KeyError, IndexError):
                    print("Error: Could not find download URI in the final response.")
                    return None
                break
            
            print("Generation in progress, waiting 10 seconds...")
            time.sleep(10)

        # --- Step 3: Download the Video ---
        if download_uri:
            # The API returns a googleapis URI, we need to convert it to the thucchien.ai gateway URI
            # e.g., https://generativelanguage.googleapis.com/v1beta/files/xyz -> https://api.thucchien.ai/gemini/download/v1beta/files/xyz
            download_url = download_uri.replace("https://generativelanguage.googleapis.com/", "https://api.thucchien.ai/gemini/download/")
            
            print(f"Step 3: Downloading video from {download_url}...")
            # Remove Content-Type for the download request
            download_headers = {"x-goog-api-key": API_KEY}
            video_response = requests.get(download_url, headers=download_headers)
            video_response.raise_for_status()
            print("Download successful.")
            return video_response.content

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    return None

if __name__ == '__main__':
    # Example usage:
    prompt_text = "Make this tiny cowboy even smaller."
    
    # This is a dummy 1x1 red pixel png for demonstration
    dummy_base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/epv2AAAAABJRU5ErkJggg=="
    image_input = {
        "bytesBase64Encoded": dummy_base64_image,
        "mimeType": "image/png"
    }

    video_content = generate_video(prompt_text, input_image=image_input)
    
    if video_content:
        output_path = "output/my_generated_video_with_image.mp4"
        with open(output_path, "wb") as f:
            f.write(video_content)
        print(f"Video successfully saved to {output_path}")
