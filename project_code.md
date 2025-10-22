# AI Thuc Chien Project Code

## `main.py`
```python
import argparse
import datetime
import json
import base64
import mimetypes
from modules.gen_text import generate_text
from modules.gen_image import generate_image
from modules.gen_video import generate_video
from modules.gen_tts import generate_tts

def log_prompt(prompt, response, response_is_binary=False):
    """Logs the prompt and its response to the prompt.log file."""
    with open("prompt.log", "a") as f:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": prompt,
            "response": "binary data" if response_is_binary else response
        }
        f.write(json.dumps(log_entry) + "\n")

def main():
    parser = argparse.ArgumentParser(description="AI Thuc Chien Content Generator")
    parser.add_argument("type", choices=["text", "image", "video", "tts"], help="Type of content to generate")
    parser.add_argument("prompt_file", help="Path to the file containing the prompt text")
    parser.add_argument("--args_file", help="Path to a JSON file with additional arguments for the API")
    parser.add_argument("--input_image", help="Path to an input image file (for video generation)")

    args = parser.parse_args()

    with open(args.prompt_file, "r") as f:
        prompt = f.read()

    api_args = {}
    if args.args_file:
        with open(args.args_file, "r") as f:
            api_args = json.load(f)

    if args.input_image:
        if args.type != "video":
            print("Warning: --input_image is only used for video generation.")
        else:
            try:
                with open(args.input_image, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                mime_type, _ = mimetypes.guess_type(args.input_image)
                if not mime_type:
                    mime_type = 'application/octet-stream' # Default if type can't be guessed

                api_args['input_image'] = {
                    "bytesBase64Encoded": encoded_string,
                    "mimeType": mime_type
                }
            except FileNotFoundError:
                print(f"Error: Input image file not found at {args.input_image}")
                return

    response = None
    if args.type == "text":
        response = generate_text(prompt, **api_args)
    elif args.type == "image":
        response = generate_image(prompt, **api_args)
    elif args.type == "video":
        # Filter api_args to only include valid arguments for generate_video
        valid_args = ["input_image"]
        video_args = {k: v for k, v in api_args.items() if k in valid_args}
        response = generate_video(prompt, **video_args)
    elif args.type == "tts":
        response = generate_tts(prompt, **api_args)

    if response:
        print("Generation successful!")
        is_binary_response = args.type == "tts" or args.type == "image" or args.type == "video"
        if not is_binary_response:
            if args.type == "text": # Handle text response as plain string
                print(response)
            else:
                print(json.dumps(response, indent=2))
        else:
            # For image/tts, response is binary or base64 string, so we don't print it directly to console
            print(f"Output for {args.type} generated.")

        log_prompt(prompt, response, response_is_binary=is_binary_response)

        # Save the output
        output_filename = f"output/{args.type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        if args.type == "tts":
            decoded_audio = base64.b64decode(response)
            with open(f"{output_filename}.wav", "wb") as f:
                f.write(decoded_audio)
            print(f"Saved audio to {output_filename}.wav")
        elif args.type == "image":
            decoded_image = base64.b64decode(response)
            with open(f"{output_filename}.png", "wb") as f:
                f.write(decoded_image)
            print(f"Saved image to {output_filename}.png")
        elif args.type == "video":
            with open(f"{output_filename}.mp4", "wb") as f:
                f.write(response)
            print(f"Saved video to {output_filename}.mp4")
        else:
            if args.type == "text":
                with open(f"{output_filename}.txt", "w") as f:
                    f.write(response)
                print(f"Saved response to {output_filename}.txt")
            else:
                with open(f"{output_filename}.json", "w") as f:
                    json.dump(response, f, indent=2)
                print(f"Saved response to {output_filename}.json")
    else:
        print("Generation failed.")

if __name__ == "__main__":
    main()
```

## `modules/gen_text.py`
```python
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

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
```

## `modules/gen_image.py`
```python
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
API_URL = "https://api.thucchien.ai/images/generations"

def generate_image(prompt, aspect_ratio="1:1", model="imagen-4", n=1):
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
```

## `modules/gen_video.py`
```python
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
 # The base URL is now different, and we'll construct specific URLs for each step
API_BASE_URL = "https://api.thucchien.ai/gemini/v1beta"

def generate_video(prompt, model="veo-3.0-generate-001", input_image=None):
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
        # "parameters": {
        #     "negativePrompt": "blurry, low quality"
        # }
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
```

## `modules/gen_tts.py`
```python
import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("AITHUCCHIEN_API_KEY")
API_BASE_URL = "https://api.thucchien.ai/gemini/v1beta/models"

def generate_tts(text, model="gemini-2.5-flash-preview-tts", voices="Kore"):
    """
    Generates audio from text using the Gemini TTS API via AI Thuc Chien gateway.
    
    Args:
        text (str): The text to synthesize.
        model (str): The model to use for generation.
        voices (str or dict): 
            - For a single speaker, a string with the voice name (e.g., "Kore").
            - For multiple speakers, a dict mapping speaker name to voice name 
              (e.g., {"Speaker1": "Kore", "Speaker2": "Puck"}).
    """
    if not API_KEY:
        raise ValueError("API key not found. Please set the AITHUCCHIEN_API_KEY environment variable.")

    api_url = f"{API_BASE_URL}/{model}:generateContent"
    
    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # --- Build Generation Config based on single or multi-speaker ---
    speech_config = {}
    if isinstance(voices, str):
        # Single speaker
        speech_config["voiceConfig"] = {
            "prebuiltVoiceConfig": {"voiceName": voices}
        }
    elif isinstance(voices, dict):
        # Multiple speakers
        speaker_configs = []
        for speaker, voice_name in voices.items():
            speaker_configs.append({
                "speaker": speaker,
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
            })
        speech_config["multiSpeakerVoiceConfig"] = {
            "speakerVoiceConfigs": speaker_configs
        }

    data = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": speech_config
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        
        # Extract the base64 encoded audio data
        if json_response.get("candidates"):
            return json_response["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print(f"Response body: {e.response.text if e.response else 'No response'}")
        return None

if __name__ == '__main__':
    # --- Example 1: Single Speaker ---
    print("--- Testing Single Speaker ---")
    text_to_speak_single = "Say cheerfully: Have a wonderful day!"
    audio_data_single = generate_tts(text_to_speak_single, voices="Kore")
    if audio_data_single:
        decoded_audio = base64.b64decode(audio_data_single)
        with open("output/speech_single.wav", "wb") as f:
            f.write(decoded_audio)
        print("Single speaker speech saved to output/speech_single.wav")

    print("\n" + "="*20 + "\n")

    # --- Example 2: Multiple Speakers ---
    print("--- Testing Multiple Speakers ---")
    text_to_speak_multi = """Make Speaker1 sound tired and bored, and Speaker2 sound excited and happy:
Speaker1: So... what's on the agenda today?
Speaker2: You're never going to guess!"""
    voices_multi = {"Speaker1": "Kore", "Speaker2": "Puck"}
    audio_data_multi = generate_tts(text_to_speak_multi, voices=voices_multi)
    if audio_data_multi:
        decoded_audio = base64.b64decode(audio_data_multi)
        with open("output/speech_multi.wav", "wb") as f:
            f.write(decoded_audio)
        print("Multi-speaker speech saved to output/speech_multi.wav")
```

## `requirements.txt`
```
requests
python-dotenv
```

## `.gitignore`
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
.venv/

# Environment variables
.env

# Output files
# output/

# IDE / Editor specific
.vscode/
.idea/
```
