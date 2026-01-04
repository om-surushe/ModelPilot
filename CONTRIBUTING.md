# Contributing to ModelPilot

Thank you for your interest in contributing to ModelPilot! This repository contains the configuration for the ModelPilot LiteLLM proxy server.

## How to Contribute

### 1. Prerequisites
- Docker and Docker Compose installed
- Git installed

### 2. Making Changes
Since this is a configuration repository, most changes will involve:
- Updating `docker-compose.yml` for service orchestration.
- Modifying example configurations.
- Improving documentation.

### 3. Testing Locally
Before submitting a Pull Request, please verify your changes locally:

```bash
# validate docker-compose config
docker compose config

# test running the services
docker compose up -d
```

### 4. Submitting a Pull Request
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-update`.
3. Commit your changes: `git commit -m "feat: add new service config"`.
4. Push to the branch: `git push origin feature/my-update`.
5. Open a Pull Request.

## Code of Conduct
Please be respectful and considerate of others when contributing.
