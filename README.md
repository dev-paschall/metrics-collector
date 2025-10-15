# System Metrics Collector

A FastAPI-based metrics collection service that gathers **system and container metrics** (CPU, memory, disk usage, etc.) and exposes them via a `/metrics` endpoint for **Prometheus** monitoring.

---

## Features

- Collects **system-level metrics** (CPU, memory, disk)
- Collects **Docker container metrics** when running under Docker
- Exposes metrics in **Prometheus-compatible format**
- Supports **Prometheus integration** via Docker Compose

---



