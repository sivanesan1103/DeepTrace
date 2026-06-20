# DeepTrace OSINT Platform

![DeepTrace OSINT Platform](https://img.shields.io/badge/DeepTrace-OSINT%20Platform-blue)

## Tagline
Open Source Intelligence (OSINT) platform for comprehensive digital investigations.

## Features
| Module | Description | Screenshot |
|--------|-------------|------------|
| Authentication | User management and authentication | ![Auth](https://via.placeholder.com/150) |
| Face Recognition | Facial detection and search | ![Face](https://via.placeholder.com/150) |
| Username Hunter | Social media username tracking | ![Username](https://via.placeholder.com/150) |
| Email Breach Lookup | Email exposure and breach intelligence | ![Email](https://via.placeholder.com/150) |
| Phone Intelligence | Carrier and spam analysis | ![Phone](https://via.placeholder.com/150) |
| Geo Intelligence | EXIF and OCR location analysis | ![Geo](https://via.placeholder.com/150) |
| Social Graph | Entity relationship mapping | ![Graph](https://via.placeholder.com/150) |
| Timeline Reconstruction | Event chronology building | ![Timeline](https://via.placeholder.com/150) |
| AI Assistant | Natural language investigation aid | ![AI](https://via.placeholder.com/150) |
| Report Generation | Automated PDF report export | ![Report](https://via.placeholder.com/150) |
| Alerting & Monitoring | Scheduled checks and notifications | ![Alert](https://via.placeholder.com/150) |
| Admin Panel | System health and user management | ![Admin](https://via.placeholder.com/150) |
| Celery Workers | Background task processing | ![Celery](https://via.placeholder.com/150) |
| API Gateway | Service routing and security | ![Gateway](https://via.placeholder.com/150) |

## Tech Stack
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)
![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss)
![Shadcn/ui](https://img.shields.io/badge/Shadcn/ui-000000?style=for-the-badge&logo=shadcnui)

## Quick Start
```bash
# Clone the repository
git clone https://github.com/sivanesan1103/DeepTrace.git
cd DeepTrace

# Start all services with Docker Compose
docker compose up -d

# Access the platform
Open http://localhost:3000 in your browser
```

## Architecture
```mermaid
graph TD
    A[Web Client] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[Face Service]
    B --> E[Username Service]
    B --> F[Email Service]
    B --> G[Phone Service]
    B --> H[Geo Service]
    B --> I[Graph Service]
    B --> J[Timeline Service]
    B --> K[AI Service]
    B --> L[Report Service]
    B --> M[Monitoring Service]
    B --> N[Admin Service]
    C --> O[(PostgreSQL)]
    D --> O
    E --> O
    F --> O
    G --> O
    H --> O
    I --> O
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O
    D --> P[Faiss Index]
    I --> Q[(Neo4j)]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#bff,stroke:#333,stroke-width:2px
    style E fill:#ffb,stroke:#333,stroke-width:2px
    style F fill:#fb9,stroke:#333,stroke-width:2px
    style G fill:#9ff,stroke:#333,stroke-width:2px
    style H fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#9f9,stroke:#333,stroke-width:2px
    style J fill:#99f,stroke:#333,stroke-width:2px
    style K fill:#f99,stroke:#333,stroke-width:2px
    style L fill:#9ff,stroke:#333,stroke-width:2px
    style M fill:#ff9,stroke:#333,stroke-width:2px
    style N fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#999,stroke:#333,stroke-width:2px
    style P fill:#999,stroke:#333,stroke-width:2px
    style Q fill:#999,stroke:#333,stroke-width:2px
```

## Service Overview
| Service | Description | Port |
|---------|-------------|------|
| auth-service | User authentication and management | 8001 |
| face-service | Facial recognition and search | 8002 |
| username-service | Social media username tracking | 8003 |
| email-service | Email breach and exposure intelligence | 8004 |
| phone-service | Phone number intelligence | 8005 |
| geo-service | Geographic information from images | 8006 |
| graph-service | Social graph and relationship mapping | 8007 |
| timeline-service | Event chronology reconstruction | 8008 |
| ai-service | AI-powered assistance and analysis | 8009 |
| report-service | Automated report generation | 8010 |
| monitoring-service | Alerting and system monitoring | 8011 |
| admin-service | Administrative panel and health checks | 8012 |
| api-gateway | Request routing and security | 8000 |
| celery-worker | Background task processing | - |

## Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://user:password@localhost/deeptrace |
| REDIS_URL | Redis connection string | redis://localhost:6379 |
| NEO4J_URI | Neo4j Bolt URI | bolt://localhost:7687 |
| NEO4J_USER | Neo4j username | neo4j |
| NEO4J_PASSWORD | Neo4j password | password |
| OLLAMA_BASE_URL | Ollama API URL | http://ollama:11434 |
| HIBP_API_KEY | HaveIBeenPwned API key | - |
| HUNTER_API_KEY | Hunter.io API key | - |
| JWT_SECRET_KEY | Secret for JWT signing | your-secret-key |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiration | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiration | 7 |
| FRONTEND_URL | Frontend application URL | http://localhost:3000 |
| BACKEND_URL | Backend API URL | http://localhost:8000 |
| MINIO_ENDPOINT | MinIO storage endpoint | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO access key | minioadmin |
| MINIO_SECRET_KEY | MinIO secret key | minioadmin |
| MINIO_BUCKET_REPORTS | Reports bucket name | reports |

## Default Credentials
- **Username**: admin
- **Password**: admin

> ⚠️ **Security Note**: Change these credentials immediately after first login in production environments.

## Development Setup
1. Install dependencies:
   ```bash
   # Backend
   cd services
   pip install -r requirements.txt
   
   # Frontend
   cd ../apps/web
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start development servers:
   ```bash
   # Backend (from services directory)
   uvicorn main:app --reload --port 8000
   
   # Frontend (from apps/web directory)
   npm run dev
   ```

4. Run tests:
   ```bash
   # Backend
   pytest
   
   # Frontend
   npm test
   ```

## Production Deployment
1. Configure environment variables for production in `.env.production`
2. Build Docker images:
   ```bash
   docker compose build
   ```
3. Deploy with Docker Compose:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
4. Set up reverse proxy (nginx) for SSL termination
5. Configure automated backups for PostgreSQL and Redis

## Troubleshooting
For common issues and solutions, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.