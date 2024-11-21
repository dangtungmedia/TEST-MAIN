from google_auth_oauthlib.flow import InstalledAppFlow
import subprocess

CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    # Save credentials to a file
    with open('credentials.json', 'w') as token:
        token.write(credentials.to_json())
    print("Authentication successful.")

def download_video(video_url):
    # Use yt-dlp with OAuth2 credentials
    command = [
        "yt-dlp",
        f"--cookies=credentials.json",
        video_url
    ]
    subprocess.run(command)

if __name__ == "__main__":
    authenticate()
    video_url = "https://www.youtube.com/watch?v=knW7-x7Y7RE"
    download_video(video_url)
