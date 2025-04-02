# GDAI - Generative Document AI

GDAI is a containerized, AI-powered application that leverages a set of specialized services to provide semantic search, secure user authentication, and a scalable API. The application uses Docker Compose for local development and production deployment, ensuring all services work together seamlessly.



## 1. Getting Started

### Running the Application

To start all services defined in the project, simply run:

```bash
docker-compose up
```


For running the services in detached mode, use:

```bash
docker-compose up -d
```

### SSL Certificate Generation

Before deploying into production, generate SSL certificates for your domains:

```bash
certbot certonly --standalone -d gdai.site -d www.gdai.site --email firminodefaria@gmail.com --agree-tos --non-interactive --config-dir ./certbot/config --work-dir ./certbot/work --logs-dir ./certbot/logs
```

Make sure ports 80 and 443 are available when running Certbot.

---

## 2. Project Structure


```bash
gdai/
├── docker-compose.yml     # Docker Compose configuration
├── .github/               # Github Actions configuration
│── infra/                 # Infrastructure configuration files
│── src/                   # Application
│── Dockerfile.yml         # Dockerfile for project application
│── pyproject.yml          # python project configuration
│── uv.lock                # uv.lock file for project
└── README.md              # Project documentation
```

*Note: Additional configuration files (e.g., for Nginx or Certbot) may be provided in external folders or through mounted volumes.*

---

## 3. Services Infrastructure

The services defined in the `docker-compose.yml` file combine to provide a full-featured environment for GDAI. Below is an explanation of each service:

### Weaviate
- **Image:** `semitechnologies/weaviate:latest`  
- **Purpose:** Provides a vector search engine for semantic similarity searches.  
- **Configuration:**  
  - Environment variables set options such as query defaults and anonymous access.
  - Persists data with a named volume (`weaviate_data`).
  - Exposes port 8080 internally and maps it for inter-service communication.

### Supertokens
- **Image:** `supertokens/supertokens-postgresql:latest`  
- **Purpose:** Manages secure user authentication and session management.  
- **Configuration:**  
  - Environment variables configure database connection details.
  - It depends on the `postgres` service to operate.
  - Exposes port 3567 for authentication API calls.

### Postgres
- **Image:** `postgres:13-alpine`  
- **Purpose:** Acts as the primary database service supporting both Supertokens and potentially other application data.  
- **Configuration:**  
  - Environment variables define the database, user, and password.
  - Persists data with a named volume (`postgres_data`).

### FastAPI Application (fastapi-app)
- **Container Name:** `fastapi-app`  
- **Purpose:** Runs the main API application built with FastAPI.  
- **Configuration:**  
  - Built from the local Dockerfile.
  - Exposes the application on port 8000.
  - Sets environment variables to connect to the Weaviate and Supertokens services.
  - Depends on both `weaviate` and `supertokens` to ensure proper startup order.

### Nginx
- **Image:** `nginx:alpine`  
- **Purpose:** Acts as a reverse proxy and TLS terminator in a production environment.  
- **Configuration:**  
  - Maps host ports 80 and 443 to the container.
  - Mounts configuration files (from `infra/nginx/gdai.conf`) and SSL certificates.
  - Depends on the FastAPI application to start before routing traffic.

---

## 4. Summary

GDAI leverages a modern set of technologies orchestrated via Docker Compose:

- **Weaviate** handles semantic search.
- **Supertokens** provides authentication services.
- **Postgres** maintains the backend database.
- **FastAPI app** serves as the core API.
- **Nginx** secures and routes external web traffic in production.

This setup allows developers to quickly start the environment with minimal configuration while ensuring a scalable infrastructure appropriate for production deployments.

Happy coding!