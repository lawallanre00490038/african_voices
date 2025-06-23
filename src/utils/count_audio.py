import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

REPO_OWNER = "lawallanre00490038"
REPO_NAME = "dsn-voice"
BASE_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/annotators"
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg"}

headers = {
    "Authorization": f"token {TOKEN}"
}

def is_audio_file(filename):
    return any(filename.lower().endswith(ext) for ext in AUDIO_EXTENSIONS)

def count_files_in_folder(folder_url):
    audio_count = 0
    subfolder_breakdown = {}

    response = requests.get(folder_url, headers=headers)
    if response.status_code != 200:
        return 0, {}

    items = response.json()

    for item in items:
        if item["type"] == "file" and is_audio_file(item["name"]):
            audio_count += 1
        elif item["type"] == "dir":
            subfolder_name = item["name"]
            sub_url = item["url"]
            sub_count, _ = count_files_in_folder(sub_url)
            subfolder_breakdown[subfolder_name] = sub_count
            audio_count += sub_count

    return audio_count, subfolder_breakdown

def count_audio_files_deep():
    result = {}
    response = requests.get(BASE_API, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch annotator folders", "details": response.text}

    annotator_folders = response.json()

    for folder in annotator_folders:
        if folder["type"] == "dir":
            folder_name = folder["name"]
            print(f"Counting audio files in {folder_name}...")
            total, subfolders = count_files_in_folder(folder["url"])
            result[folder_name] = {
                "total_audio": total,
                "subfolders": subfolders
            }

    return result
