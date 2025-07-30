# Copilot.api

Provides a simple HTTP API to interface with GitHub Copilot, including native GitHub authentication.

## Installing dependencies

`pip install -r requirements.txt`

## Run
`python3 api.py [port]`

The server also exposes OpenAI-compatible endpoints under `/v1` so that tools
like [Open WebUI](https://github.com/open-webui/open-webui) can connect. Use the
following environment variables when starting Open WebUI:

```
OPENAI_API_BASE_URLS=http://host.docker.internal:8080/v1
OPENAI_API_KEYS=dummy
```

Point your browser to `http://localhost:8080/` for a minimal chat UI.

## Usage
Send a POST request to `http://localhost:8080/api` with the following JSON body:

### Request payload
```json
{
    "prompt": "# hello world function\n\n",
    "language": "python",
    "stop": ["\n"]
}
```

### Response

The response will be a plain text string containing the generated code.

```text
def hello_world():
```

The `stop` field is optional and defaults to `["\n"]` when omitted. Use it to control where completions should stop. Omit the field entirely to allow multiline responses.

In order to build a complete code snippet, iteratively append the generated code to the prompt and send it back to the API until the response is empty.
