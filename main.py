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
