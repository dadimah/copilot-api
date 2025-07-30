# Copilot.api

Provides a simple HTTP API to interface with GitHub Copilot, including native GitHub authentication.  It exposes OpenAI compatible endpoints so that tools such as [Open WebUI](https://github.com/open-webui/open-webui) can talk to Copilot.

## Installing dependencies

`pip install -r requirements.txt`

## Run
Run the server on the desired port (defaults to `8080`):
`python3 api.py [port]`

The server exposes OpenAI‑compatible endpoints under `/v1` so that tools like
[Open WebUI](https://github.com/open-webui/open-webui) can connect.  When
starting Open WebUI use the following environment variables:

```
OPENAI_API_BASE_URLS=http://host.docker.internal:8080/v1
OPENAI_API_KEYS=dummy
```

Point your browser to `http://localhost:8080/` for a small fallback UI that works
in any modern browser.  It can be useful when you do not have Open WebUI running.

## Usage
Send a POST request to `http://localhost:8080/api` with the following JSON body:

### Request payload
```json
{
    "prompt": "# hello world function\n\n",
    "language": "python"
}
```

### Response

The response will be a plain text string containing the generated code.

```text
def hello_world():
```



In order to build a complete code snippet, iteratively append the generated code to the prompt and send it back to the API until the response is empty.
