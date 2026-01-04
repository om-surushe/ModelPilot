# ModelPilot 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Config Validation](https://github.com/om-surushe/ModelPilot/actions/workflows/ci.yml/badge.svg)](https://github.com/om-surushe/ModelPilot/actions/workflows/ci.yml)


Smart LLM Routing & Proxy Server (Powered by LiteLLM).

## Features

* **Unified Interface**: One API key for 100+ LLMs (OpenAI, Azure, Anthropic, etc.).
* **Smart Routing**: Load balance across multiple keys/deployments.
* **User Management**: Built-in Admin UI to create Users, Teams, and Budgets.
* **Reliability**: Automatic retries and fallbacks (e.g., switch to Azure if OpenAI is down).

## Setup

### Prerequisites

* Docker & Docker Compose
* Linux VM with ports 4001, 5432, 6379 available (or configure custom ports)

### Quick Start

1. **Configure Secrets**:

    ```bash
    cp .env.example .env
    nano .env
    ```

    **Update these critical values:**
    * `LITELLM_MASTER_KEY` - Generate a strong random key
    * `POSTGRES_PASSWORD` - Use a secure password
    * Provider API keys (`GROQ_API_KEY`, `MISTRAL_API_KEY`, `GEMINI_API_KEY`)

2. **Start Services**:

    ```bash
    docker compose up -d
    ```

3. **Access Admin UI**:
    * URL: `http://localhost:4001/ui` (or `http://your-vm-ip:4001/ui`)
    * Admin Key: The value of `LITELLM_MASTER_KEY` from your `.env` file.

## Configuration

### Environment Variables (`.env`)

All deployment parameters are configurable:
* `LITELLM_PORT` - External port for LiteLLM (default: 4001)
* `CONFIG_PATH` - Path to config.yaml (default: ./config.yaml)
* `POSTGRES_PORT` - Database port (default: 5432)
* `REDIS_PORT` - Redis cache port (default: 6379)

### Models (`config.yaml`)

Add models or change routing logic:

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
```

## VM Deployment

### Firewall Configuration

```bash
# Allow LiteLLM port
sudo ufw allow 4001/tcp

# Optional: If accessing DB externally
sudo ufw allow 5432/tcp
```

### Production Checklist

- [ ] Change `LITELLM_MASTER_KEY` to a strong random value
* [ ] Use a complex `POSTGRES_PASSWORD`
* [ ] Configure firewall rules
* [ ] Set up SSL/TLS reverse proxy (nginx/caddy) for HTTPS
* [ ] Enable Docker restart policies (already configured)
* [ ] Regular backups of `pg_data` volume

### Custom Config Path

For centralized config management:

```bash
# In .env
CONFIG_PATH=/etc/modelpilot/config.yaml
```

## API Usage

```bash
curl -X POST 'http://localhost:4001/chat/completions' \
-H 'Authorization: Bearer sk-1234567890abcdef' \
-H 'Content-Type: application/json' \
-d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [ { "content": "Hello, world!", "role": "user" } ]
}'
```

## Troubleshooting

### Check Logs

```bash
docker compose logs -f litellm
```

### Restart Services

```bash
docker compose restart
```

### Port Conflicts

If default ports are in use:

```bash
# Edit .env
LITELLM_PORT=8080
POSTGRES_PORT=5433
REDIS_PORT=6380
```

### Database Connection Issues

```bash
docker compose exec db psql -U postgres -d litellm
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
