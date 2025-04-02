# GDAI - Generative Document AI

## 0. Project Structure

```
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

## 1. Commands

**Including application running on port 8000** 
```sh
docker-compose up 
```


**Generate SSL certificate for gdai.site and www.gdai.site -- only on server** 
```sh
certbot certonly --standalone -d gdai.site -d www.gdai.site  --email firminodefaria@gmail.com --agree-tos --non-interactive  --config-dir ./certbot/config   --work-dir ./certbot/work   --logs-dir ./certbot/logs
```

**Running fastapi application**
```sh
task runserver
```

## 2. Project Infrastructure

+ Weaviate: is an open-source vector search engine designed for scalable semantic similarity searches.
+ supertokens: is an open-source authentication server that provides secure and scalable user session management.
+ postgres: is an advanced open-source SQL database management system renowned for its reliability, extensibility, and strong standards compliance. 
+ fastapi-app: the api application 
+ nginx: used only in production to serve the application with ssl certificate