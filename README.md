# DeepTrace OSINT Platform

[![DeepTrace OSINT Platform](https://img.shields.io/badge/DeepTrace-OSINT%20Platform-blue?style=for-the-badge&logo=search)](https://deeptrace.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

Advanced OSINT investigation platform combining facial recognition, username hunting, email intelligence, and social graph analysis.

## Features

| Module | Description | Status |
|--------|-------------|--------|
| ![](https://img.shields.io/badge/🔍-Face%20Recognition-blue) | AI-powered facial recognition with FAISS vector search | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🕵️-Username%20Hunter-blue) | Maigret integration for 2000+ site searches | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📧-Email%20Intelligence-blue) | Breach lookup via HIBP, Gravatar, GitHub searches | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📱-Phone%20Intel-blue) | Carrier lookup, WhatsApp/Telegram detection | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🌍-Geo%20Analytics-blue) | EXIF extraction, OCR, reverse geocoding | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📊-Social%20Graph-blue) | Neo4j-powered relationship mapping | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🤖-AI%20Assistant-blue) | Ollama streaming chat for investigation summaries | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📅-Timeline%20Recon-blue) | Wayback Machine integration, event reconstruction | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📈-Reports-blue) | PDF/CSV/JSON export with templated layouts | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🚨-Monitoring-blue) | Scheduled breach scans, webhook alerts | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🔐-Auth%20Service-blue) | Keycloak integration with RBAC | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🌐-Gateway-blue) | API gateway with rate limiting | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/🔗-Search%20Engine-blue) | Multi-source investigation aggregation | ![](https://img.shields.io/badge/-Available-green) |
| ![](https://img.shields.io/badge/📊-Dashboard-blue) | Next.js frontend with real-time updates | ![](https://img.shields.io/badge/-Available-green) |

## Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-005571?style=for-the-badge&logo=neo4j)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)

## Quick Start

```bash
docker compose up -d
```

The platform will be available at `http://localhost:3000`

## Architecture

```mermaid
graph TB
    subgraph "Frontend"
        WEB[Next.js Dashboard]
    end

    subgraph "Gateway Layer"
        GW[API Gateway]
    end

    subgraph "Auth Layer"
        AUTH[Auth Service]
        KEYCLOAK[Keycloak]
    end

    subgraph "OSINT Services"
        FACE[Face Service]
        USER[Username Service]
        EMAIL[Email Service]
        PHONE[Phone Service]
        GEO[Geo Service]
        GRAPH[Graph Service]
        AI[AI Assistant]
        TIMELINE[Timeline Service]
        REPORT[Report Service]
        MONITOR[Monitoring Service]
        SEARCH[Search Service]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL)]
        REDIS[(Redis)]
        NEO4J[(Neo4j)]
        MINIO[(MinIO)]
        FAISS[FAISS Index]
    end

    WEB --> GW
    GW --> AUTH
    AUTH --> KEYCLOAK
    GW --> FACE & USER & EMAIL & PHONE & GEO & GRAPH & AI & TIMELINE & REPORT & MONITOR & SEARCH
    FACE --> FAISS
    GRAPH --> NEO4J
    REPORT --> MINIO
    FACE & USER & EMAIL & PHONE & GEO & GRAPH & TIMELINE & REPORT & MONITOR --> PG
    AUTH & USER & EMAIL & PHONE & GEO & GRAPH & AI & TIMELINE & REPORT & MONITOR & SEARCH --> REDIS
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| gateway | 8080 | API Gateway with rate limiting and routing |
| auth | 8001 | Authentication service with Keycloak integration |
| face | 8002 | Facial recognition with FAISS vector search |
| username | 8003 | Username hunting across 2000+ platforms |
| email | 8004 | Email breach lookup and exposure intelligence |
| phone | 8005 | Phone number carrier and social detection |
| geo | 8006 | Geo intelligence with EXIF and OCR analysis |
| graph | 8007 | Social graph engine with Neo4j traversal |
| timeline | 8008 | Timeline reconstruction with Wayback integration |
| ai | 8009 | AI assistant with Ollama streaming chat |
| report | 8010 | Report generation with PDF export |
| monitoring | 8011 | Alert service with scheduled checks |
| search | 8012 | Investigation aggregation and search |
| frontend | 3000 | Next.js dashboard |

## Environment Variables

### Core Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `COMPOSE_PROJECT_NAME` | Docker project name | `deeptrace` |
| `DOMAIN` | Application domain | `localhost` |
| `ENVIRONMENT` | Deployment environment | `development` |

### Database & Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | PostgreSQL database | `deeptrace` |
| `POSTGRES_USER` | PostgreSQL user | `deeptrace` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `deeptrace` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `NEO4J_URI` | Neo4j Bolt URI | `bolt://neo4j:7688` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `deeptrace` |
| `MINIO_ENDPOINT` | MinIO endpoint | `minio:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |

### External APIs

| Variable | Description | Required |
|----------|-------------|----------|
| `HIBP_API_KEY` | HaveIBeenPwned API key | Yes |
| `KEYCLOAK_ADMIN` | Keycloak admin username | Yes |
| `KEYCLOAK_PASSWORD` | Keycloak admin password | Yes |
| `OLLAMA_BASE_URL` | Ollama service URL | Optional |

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| Keycloak Admin | `admin` | `admin` |
| PostgreSQL | `deeptrace` | `deeptrace` |
| MinIO | `minioadmin` | `minioadmin` |
| Neo4j | `neo4j` | `deeptrace` |

> **⚠️ Security Warning:** Change all default passwords before production deployment.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/deeptrace/deeptrace.git
cd deeptrace

# Start development environment
docker compose up -d

# View logs
docker compose logs -f

# Run tests
docker compose exec gateway pytest
docker compose exec frontend npm test
```

### Service Development

Each service can be developed independently:

```bash
# Backend service (example: auth)
cd services/auth
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev
```

## Production Deployment

```bash
# Create production environment file
cp .env.example .env.prod

# Edit with production values
nano .env.prod

# Deploy with production configuration
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

See [Deployment Guide](docs/deployment.md) for detailed production setup.

## Troubleshooting

- **Services not starting**: Check `docker compose logs <service>`
- **Database connection errors**: Verify PostgreSQL and Redis are running
- **Authentication issues**: Ensure Keycloak realm is configured
- **FAISS errors**: Check `/data/faiss.index` permissions
- **Full troubleshooting guide**: [docs/troubleshooting.md](docs/troubleshooting.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.