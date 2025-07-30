# Copilot.api

Provides a simple HTTP API to interface with GitHub Copilot, including native GitHub authentication.

## Installing dependencies

`pip install -r requirements.txt`

## Run
`python3 api.py [port]`

By default the application listens on port `8080`. After starting the server you
can open `http://localhost:8080/` in your browser to use a simple chat page that
talks to the API.

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

### Web UI

There is a minimal browser-based interface in the `static/` folder. Once the server is running, visit [http://localhost:8080/](http://localhost:8080/) to send prompts and view completions.
