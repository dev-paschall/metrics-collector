# System Metrics Collector

A FastAPI-based metrics collection service that gathers **system and container metrics** (CPU, memory, disk usage, etc.) and exposes them via a `/metrics` endpoint for **Prometheus** monitoring.

---

## Features

- Collects **system-level metrics** (CPU, memory, disk)
- Collects **Docker container metrics** when running under Docker
- Exposes metrics in **Prometheus-compatible format**
- Supports **Prometheus integration** via Docker Compose

---

## Installation

```bash
git clone https://github.com/dev-paschall/metrics-collector.git
cd metrics-collector
pip install -r requirements.txt
```

---

## Usage

### Run locally(Uvicorn)

```bash
uvicorn app.main:app --reload
```
Visit http://localhost:8000/metrics to view collected metrics.


### Run with Docker(standalone)
For metrics collection only (requires Docker socket access to collect container stats):

```bash
docker build -t metrics-collector .
docker run -d -p 8000:8000 \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  metrics-collector
```
This will start:
- App → FastAPI metrics collector (port 8000)
- Prometheus → Metrics monitoring (port 9090)
Then open http://localhost:9090 to access Prometheus UI

### Run with Docker Compose (Recommended)

```bash
docker compose up -d
```
Use this method to start the metrics collector and Prometheus simultaneously.

### Configuration

Prometheus configuration (prometheus.yml):

```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: "fastapi_app"
    static_configs:
      - targets: ["app:8000"]
```
You can adjust the scrape_interval or add new jobs to monitor other services.

---

## License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.

---

## Author

**Paschal Arowolo**  
GitHub: @dev-paschall (https://github.com/dev-paschall)
