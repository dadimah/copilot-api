# Copilot.api

Provides a simple HTTP API to interface with GitHub Copilot, including native GitHub authentication.

## Installing dependencies

`pip install -r requirements.txt`

## Run
`python3 api.py [port]`

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

The `stop` field is optional and defaults to `["\n"]` when omitted. Use it to control where completions should stop.

In order to build a complete code snippet, iteratively append the generated code to the prompt and send it back to the API until the response is empty.

## Using with Open WebUI

When running [Open WebUI](https://github.com/open-webui/open-webui) you can point it to this API by setting a couple of environment variables:

```bash
OPENAI_API_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=dummy
```

`OPENAI_API_KEY` can be any non-empty string; it simply satisfies the WebUI's requirement for a key.
