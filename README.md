# ModelPilot 🚀

Smart LLM Routing & Proxy Server (Powered by LiteLLM).

## Features
*   **Unified Interface**: One API key for 100+ LLMs (OpenAI, Azure, Anthropic, etc.).
*   **Smart Routing**: Load balance across multiple keys/deployments.
*   **User Management**: Built-in Admin UI to create Users, Teams, and Budgets.
*   **Reliability**: Automatic retries and fallbacks (e.g., switch to Azure if OpenAI is down).

## Setup

### Prerequisites
*   Docker & Docker Compose

### Quick Start

1.  **Configure Secrets**:
    Edit `.env` and add your Master Key and Provider Keys:
    ```bash
    cp .env.example .env  # If you haven't already
    nano .env
    ```

2.  **Start Services**:
    ```bash
    docker compose up -d
    ```

3.  **Access Admin UI**:
    *   URL: `http://localhost:4000/ui`
    *   Admin Key: The value of `LITELLM_MASTER_KEY` from your `.env` file.

## Configuration
Edit `config.yaml` to add models or change routing logic.

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
```

## API Usage

```bash
curl -X POST 'http://localhost:4000/chat/completions' \
-H 'Authorization: Bearer sk-1234567890abcdef' \
-H 'Content-Type: application/json' \
-d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [ { "content": "Hello, world!", "role": "user" } ]
}'
```
