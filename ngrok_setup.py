import subprocess
import requests
import time
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")

def read_api_key(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("api_key")
    return None

def read_auth_token(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("auth_token")
    return None

def kill_existing_ngrok():
    url = "http://127.0.0.1:4040/api/tunnels"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for tunnel in data['tunnels']:
                subprocess.run(["ngrok", "http", "stop", tunnel["name"]], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except requests.ConnectionError:
        pass

def start_ngrok(auth_token):
    kill_existing_ngrok()
    subprocess.run(["ngrok", "authtoken", auth_token], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    subprocess.Popen(["ngrok", "tcp", "8080"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def get_ngrok_url():
    time.sleep(5)  # Wait for ngrok to initialize
    url = "http://127.0.0.1:4040/api/tunnels"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'tcp':
                return tunnel['public_url']
    except requests.exceptions.RequestException:
        return None

def save_ngrok_url():
    auth_token = read_auth_token(CREDENTIALS_FILE)
    if auth_token:
        start_ngrok(auth_token)
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            print(f"Your ngrok URL is: {ngrok_url}")
            updated_url = ngrok_url.split("tcp://")[1]
            host, port = updated_url.split(':')
            with open(os.path.join(SCRIPT_DIR, "ngrok_url.txt"), "w") as f:  # Save ngrok host and port to a file
                f.write(f"{host}\n{port}\n")
        else:
            print("Failed to get ngrok URL")
    else:
        print("Auth token not found in credentials.json")

def delete_auth_tokens(api_key):
    url = "https://api.ngrok.com/credentials"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Ngrok-Version": "2",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        credentials = response.json().get('credentials', [])
        for credential in credentials:
            credential_id = credential.get('id')
            delete_url = f"https://api.ngrok.com/credentials/{credential_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code == 204:
                print(f"Deleted auth token {credential_id}")
            else:
                print(f"Failed to delete auth token {credential_id}")
    except requests.exceptions.RequestException as e:
        pass

if __name__ == "__main__":
    try:
        save_ngrok_url()
    except Exception:
        pass

    api_key = read_api_key(CREDENTIALS_FILE)
    if api_key:
        delete_auth_tokens(api_key)
    else:
        print("API key not found in credentials.json")
