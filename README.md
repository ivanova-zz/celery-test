**Getting Started**

Prerequisites
Docker and Docker Compose installed.
```
    git clone git@github.com:ivanova-zz/celery-test.git
    cd celery-test
    cp .env_example .env
    docker-compose up -d
```

**FastAPI + Celery + Redis: Data Automation Service**

This project is a high-performance automation service that fetches user data from an external API, processes it in chunks, and exports the results to a CSV file. It leverages Celery for background task orchestration and Redis as a message broker.

**Architecture**

The system is designed for scalability using the Master-Worker pattern:

FastAPI: Provides a REST interface to trigger the automation.

Redis: Acts as the queue (broker) to manage tasks.

Celery Master Task: Fetches the full dataset from the External API and splits it into smaller chunks.

Celery Worker Tasks: Multiple worker processes consume the chunks in parallel and append data to the CSV file.

**Tech Stack**

Framework: FastAPI

Task Queue: Celery

Broker/Backend: Redis

Containerization: Docker & Docker Compose

Testing: Pytest with Mocks

**Running Tests**

The project includes unit tests for task logic, error handling, and worker configuration.

To run tests inside the container:
```
docker-compose exec api pytest -v
```
**Parallel Processing (Chunking)**

The script automatically splits the workload based on the CHUNK_SIZE parameter in your .env.

Example: If the API returns 100 users and CHUNK_SIZE=5, Celery will create 20 separate sub-tasks.

This allows multiple workers to process the data simultaneously, significantly improving performance for large datasets.

**Example Request**
```curl -X POST http://localhost:8000/run-automation```