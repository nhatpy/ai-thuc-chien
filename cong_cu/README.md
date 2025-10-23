# AI Thuc Chien Content Generation Tool


This project is a command-line tool designed to interact with the AI Thuc Chien API gateway, allowing you to generate various types of content including text, images, videos, and text-to-speech audio.


## Project Structure


```
AI_thuc_chien_repo/
├── .env                # Your secret API key (create this file)
├── .gitignore          # Files and folders to be ignored by Git
├── modules/            # Python modules for each generation type
│   ├── gen_text.py
│   ├── gen_image.py
│   ├── gen_video.py
│   └── gen_tts.py
├── input/              # Place your input files here
│   ├── prompt.txt
│   └── args.json
├── output/             # Generated content will be saved here
│   └── <generated_files>
├── main.py             # The main script to run the tool
├── requirements.txt    # Project dependencies
└── README.md           # This documentation file
```


## Setup Instructions


### 1. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.


```bash
# Create the virtual environment
python3 -m venv .venv


# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate.bat
```
You will need to activate the environment every time you work on this project in a new terminal.


### 2. Install Dependencies
With your virtual environment active, install the necessary Python libraries:
```bash
pip install -r requirements.txt
```


### 3. Set Your API Key
This project loads your secret API key from a `.env` file.


**Step 1: Create the file**
```bash
cp .env.example .env
```


**Step 2: Add your key**
Open the `.env` file and add your API key in the following format:
```
# Replace with your actual AI Thuc Chien API key
AITHUCCHIEN_API_KEY="your_api_key_here"
```
The `.gitignore` file is configured to prevent this file from being accidentally committed to version control.


## Usage


The tool is run from the command line using `main.py`.


### Basic Command Structure
```bash
python main.py <type> <prompt_file> [--args_file <args_file>] [--input_image <image_path>]
```
-   `<type>`: The type of content to generate. Choices: `text`, `image`, `video`, `tts`.
-   `<prompt_file>`: Path to a text file containing the main prompt.
-   `--args_file`: (Optional) Path to a JSON file containing additional parameters for the API call.
-   `--input_image`: (Optional) Path to an image file, used only for video generation (`type` = `video`).


---


### Example Workflows


#### 1. Text Generation
-   **`input/text_prompt.txt`**:
   ```
   Hãy viết một câu giới thiệu về Việt Nam.
   ```
-   **`input/text_args.json`**:
   ```json
   {
     "system_prompt": "Bạn là một trợ lý ảo"
   }
   ```
-   **Command**:
   ```bash
   python3 main.py text input/text/prompt_1.txt --args_file input/text/prompt_1.json
   ```


#### 2. Image Generation
-   **`input/image_prompt.txt`**:
   ```
   a digital render of a massive skyscraper, modern, grand, epic with a beautiful sunset in the background
   ```
-   **`input/image_args.json`**:
   ```json
   {
     "aspect_ratio": "16:9"
   }
   ```
-   **Command**:
   ```bash
   python3 main.py image input/image/prompt_1.txt --args_file input/image/prompt_1.json
   ```


#### 3. Video Generation (from Text)
-   **`input/video_prompt.txt`**:
   ```
   A cinematic shot of a baby raccoon wearing a tiny cowboy hat, riding a miniature pony through a field of daisies at sunset.
   ```
<!-- -   **`input/video_args.json`**:
   ```json
   {
     "negative_prompt": "blurry, low quality"
   }
   ``` -->
-   **Command**:
   ```bash
   python3 main.py video input/video/prompt_1.txt
   ```


#### 4. Video Generation (from Image)
-   **`input/vid_from_img_prompt.txt`**:
   ```
   Make this raccoon wave its hand.
   ```
-   **Command**:
   ```bash
   python3 main.py video input/video/prompt_1.txt --input_image input/video/prompt_1.png
   ```


#### 5. Text-to-Speech (Single Speaker)
-   **`input/tts_prompt.txt`**:
   ```
   Say cheerfully: Have a wonderful day!
   ```
-   **`input/tts_args.json`**:
   ```json
   {
     "voices": "Kore"
   }
   ```
-   **Command**:
   ```bash
   python3 main.py tts input/voice/prompt_1.txt --args_file input/voice/prompt_1.json
   ```


#### 6. Text-to-Speech (Multiple Speakers)
-   **`input/tts_multi_prompt.txt`**:
   ```
   Make Speaker1 sound tired and bored, and Speaker2 sound excited and happy:
   Speaker1: So... what's on the agenda today?
   Speaker2: You're never going to guess!
   ```
-   **`input/tts_multi_args.json`**:
   ```json
   {
     "voices": {
       "Speaker1": "Kore",
       "Speaker2": "Puck"
     }
   }
   ```
-   **Command**:
   ```bash
   python3 main.py tts input/voice/prompt_1.txt --args_file input/voice/prompt_1.json
   ```