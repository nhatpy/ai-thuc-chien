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
