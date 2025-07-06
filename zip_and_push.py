import os
import zipfile
import subprocess

# CONFIG
EXCEL_FILE = "reports/audio_data_summary.xlsx"
ZIP_FILE = "audio_data_summary.zip"
COMMIT_MSG = "🔁 Auto-update audio summary zip"

def zip_file(source, target_zip):
    with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(source, arcname=os.path.basename(source))
    print("✅ Zipped:", target_zip)

def commit_and_push():
    subprocess.run(["git", "config", "user.email", "action@github.com"], check=True)
    subprocess.run(["git", "config", "user.name", "GitHub Action"], check=True)
    subprocess.run(["git", "add", ZIP_FILE], check=True)
    subprocess.run(["git", "commit", "-m", COMMIT_MSG], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Zip file pushed to remote")

if __name__ == "__main__":
    if not os.path.exists(EXCEL_FILE):
        print("❌ Excel file not found:", EXCEL_FILE)
        exit(1)

    zip_file(EXCEL_FILE, ZIP_FILE)
    commit_and_push()
