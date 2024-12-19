import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


def get_m3u8_link(url):
    # Настройка Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск без интерфейса
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service('/usr/bin/chromedriver')  # Путь для Docker
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # Даем странице загрузиться

        logs = driver.get_log("performance")
        for log in logs:
            if ".m3u8" in log["message"]:
                start_index = log["message"].find("https://")
                end_index = log["message"].find(".m3u8") + 5
                if start_index != -1 and end_index != -1:
                    return log["message"][start_index:end_index]
    finally:
        driver.quit()
    return None


def download_stream(stream_url, output_file):
    try:
        print(f"Starting download from {stream_url}...")
        command = ["streamlink", stream_url, "best", "-o", output_file]
        subprocess.run(command, check=True)
        print(f"Stream saved to {output_file}")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading stream: {e}")


def upload_to_youtube(video_file, title, description, category_id="22", privacy_status="private"):
    credentials = None
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    youtube = build("youtube", "v3", credentials=credentials)
    body = {
        "snippet": {"title": title, "description": description, "categoryId": category_id},
        "status": {"privacyStatus": privacy_status},
    }
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")
    print("Video uploaded successfully.")
    print(f"Video ID: {response['id']}")


if __name__ == "__main__":
    stream_url = "https://kick.com/am1rrkhan"
    m3u8_link = get_m3u8_link(stream_url)

    if m3u8_link:
        print(f"Stream link found: {m3u8_link}")
        output_file = f"stream_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        download_stream(m3u8_link, output_file)
        upload_to_youtube(output_file, "Stream Title", "Stream Description")
    else:
        print("No .m3u8 link found.")
