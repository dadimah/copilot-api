import http.server
import threading
import requests
import json
import time
import sys
import os

token = None

# Dummy model list for OpenAI compatibility
MODELS = [
    {
        "id": "copilot",
        "object": "model",
        "owned_by": "copilot-api",
    }
]

def build_prompt(messages):
    """Concatenate message contents for OpenAI-style payloads."""
    parts = []
    for msg in messages:
        content = msg.get("content")
        if content:
            parts.append(content)
    return "\n".join(parts)

def setup():
    resp = requests.post('https://github.com/login/device/code', headers={
            'accept': 'application/json',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'content-type': 'application/json',
            'user-agent': 'GithubCopilot/1.155.0',
            'accept-encoding': 'gzip,deflate,br'
        }, data='{"client_id":"Iv1.b507a08c87ecfe98","scope":"read:user"}')


    # Parse the response json, isolating the device_code, user_code, and verification_uri
    resp_json = resp.json()
    device_code = resp_json.get('device_code')
    user_code = resp_json.get('user_code')
    verification_uri = resp_json.get('verification_uri')

    # Print the user code and verification uri
    print(f'Please visit {verification_uri} and enter code {user_code} to authenticate.')


    while True:
        time.sleep(5)
        resp = requests.post('https://github.com/login/oauth/access_token', headers={
            'accept': 'application/json',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'content-type': 'application/json',
            'user-agent': 'GithubCopilot/1.155.0',
            'accept-encoding': 'gzip,deflate,br'
            }, data=f'{{"client_id":"Iv1.b507a08c87ecfe98","device_code":"{device_code}","grant_type":"urn:ietf:params:oauth:grant-type:device_code"}}')

        # Parse the response json, isolating the access_token
        resp_json = resp.json()
        access_token = resp_json.get('access_token')

        if access_token:
            break

    # Save the access token to a file
    with open('.copilot_token', 'w') as f:
        f.write(access_token)

    print('Authentication success!')


def get_token():
    global token
        # Check if the .copilot_token file exists
    while True:
        try:
            with open('.copilot_token', 'r') as f:
                access_token = f.read()
                break
        except FileNotFoundError:
            setup()
    # Get a session with the access token
    try:
        resp = requests.get('https://api.github.com/copilot_internal/v2/token', headers={
            'authorization': f'token {access_token}',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'user-agent': 'GithubCopilot/1.155.0'
        })
        resp.raise_for_status()
        resp_json = resp.json()
        token = resp_json.get('token')
    except Exception as e:
        print(f'Failed to refresh Copilot token: {e}')
        token = None


def token_thread():
    global token
    while True:
        get_token()
        time.sleep(25 * 60)
    
def copilot(prompt, language='python'):
    """Request a completion from GitHub Copilot."""
    global token
    # If the token is None, get a new one
    if token is None or is_token_invalid(token):
        get_token()

    try:
        resp = requests.post('https://copilot-proxy.githubusercontent.com/v1/engines/copilot-codex/completions', headers={'authorization': f'Bearer {token}'}, json={
            'prompt': prompt,
            'suffix': '',
            'max_tokens': 1000,
            'temperature': 0,
            'top_p': 1,
            'n': 1,
            'nwo': 'github/copilot.vim',
            'stream': True,
            'extra': {
                'language': language
            }
        })
    except requests.exceptions.ConnectionError:
        return ''

    result = ''

    # Parse the response text, splitting it by newlines
    resp_text = resp.text.split('\n')
    for line in resp_text:
        # If the line contains a completion, print it
        if line.startswith('data: {'):
            # Parse the completion from the line as json
            json_completion = json.loads(line[6:])
            completion = json_completion.get('choices')[0].get('text')
            if completion:
                result += completion
            else:
                result += '\n'
    
    return result

# Check if the token is invalid through the exp field
def is_token_invalid(token):
    if token is None or 'exp' not in token or extract_exp_value(token) <= time.time():
        return True
    return False

def extract_exp_value(token):
    pairs = token.split(';')
    for pair in pairs:
        key, value = pair.split('=')
        if key.strip() == 'exp':
            return int(value.strip())
    return None

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/v1/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"object": "list", "data": MODELS}).encode())
            return

        path = self.path.lstrip("/") or "index.html"
        file_path = os.path.join("static", path)
        if os.path.exists(file_path):
            self.send_response(200)
            if file_path.endswith(".html"):
                ctype = "text/html"
            elif file_path.endswith(".js"):
                ctype = "application/javascript"
            else:
                ctype = "text/plain"
            self.send_header("Content-Type", ctype)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            body_json = {}

        if self.path == "/v1/chat/completions":
            messages = body_json.get("messages", [])
            language = body_json.get("language", "python")
            prompt = build_prompt(messages)
            completion = copilot(prompt, language)
            response = {
                "choices": [
                    {
                        "message": {"role": "assistant", "content": completion}
                    }
                ]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

        # default /api compatibility
        prompt = body_json.get("prompt")
        language = body_json.get("language", "python")
        completion = copilot(prompt, language)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(completion.encode())


def main():
    # Every 25 minutes, get a new token
    threading.Thread(target=token_thread, daemon=True).start()
    # Get the port to listen on from the command line
    if len(sys.argv) < 2:
        port = 8080
    else:
        port = int(sys.argv[1])
    # Start the http server
    httpd = http.server.HTTPServer(('0.0.0.0', port), HTTPRequestHandler)
    print(f'Listening on port 0.0.0.0:{port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()
