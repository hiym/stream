import subprocess
import os
import time
from datetime import datetime
from pprint import pprint
import requests
import ssl
from requests.adapters import HTTPAdapter
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


# Кастомный HTTPAdapter для настройки SSL-контекста
class KickAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ssl_context = ssl.create_default_context()
        # Настраиваем контекст при необходимости
        # ssl_context.options |= ssl.OP_NO_TICKET  # Оставьте закомментированным, если не требуется
        kwargs["ssl_context"] = ssl_context
        return super().init_poolmanager(*args, **kwargs)


# Сессия с поддержкой кастомного SSL
session = requests.Session()
session.mount("https://", KickAdapter())


# Функция для проверки доступности трансляции
def is_stream_available(stream_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"}
        response = session.get(stream_url, headers=headers)

        if response.status_code == 200:
            print("Stream page loaded successfully.")

        result = subprocess.run(
            ["streamlink", "--json", stream_url],
            capture_output=True,
            text=True
        )
        pprint(result)
        return result.returncode == 0  # Код 0 означает, что трансляция доступна
    except Exception as e:
        print(f"Error checking stream availability: {e}")
        return False


# Функция для скачивания стрима
def download_stream(stream_url, output_file):
    process = None
    try:
        print(f"Starting download from {stream_url}...")
        command = [
            "streamlink",
            stream_url,
            "-o",
            output_file
        ]
        # Запускаем процесс
        process = subprocess.Popen(command)
        # Ожидание завершения или прерывания
        process.communicate()
        print(f"Stream saved to {output_file}")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Exiting gracefully...")
        if process:
            process.terminate()
            process.wait()  # Ожидание завершения процесса
    except subprocess.CalledProcessError as e:
        print(f"Error downloading stream: {e}")
    finally:
        if process and process.poll() is None:
            process.terminate()


# Функция для загрузки видео на YouTube
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print("Video uploaded successfully.")
    print(f"Video ID: {response['id']}")


if __name__ == "__main__":
    stream_url = "https://kick.com/nem3c"
    check_interval = 30

    print("Waiting for the stream to start...")
    try:
        while True:
            if is_stream_available(stream_url):
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_file = f"stream_{current_time}.mp4"
                video_title = current_time
                video_description = f"Stream recorded on {current_time}."

                print("Stream is available. Starting download...")
                download_stream(stream_url, output_file)

                # После завершения скачивания загружаем видео
                upload_to_youtube(output_file, video_title, video_description)
                break
            else:
                print("Stream not available yet. Retrying in 30 seconds...")
                time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Preparing for upload...")
        # Завершаем скачивание и загружаем на YouTube
        if 'output_file' in locals() and os.path.exists(output_file):
            upload_to_youtube(output_file, video_title, video_description)
        else:
            print("No video file found to upload.")
    finally:
        print("Done!")
