from fastapi import FastAPI
from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from metrics_collector import get_docker_metrics, get_system_metrics

app = FastAPI(title="Devops Metrics Collector")

custom_registry = CollectorRegistry()
REQUEST_COUNT = Counter("request_count", "Number of requests", registry=custom_registry)

@app.get("/")
def root():
    return {"message": "Devops metrics collector running..."}

@app.get("/metrics")
def get_metrics():
    system_metrics = get_system_metrics()
    docker_metrics = get_docker_metrics()

    # Register system metrics gauge to prometheus
    system_cpu = Gauge("system_cpu_percent", "System CPU usage percentage", registry=custom_registry)
    system_memory = Gauge("system_memory_percent", "System Memory usage percentage", registry=custom_registry)
    system_disk = Gauge("system_disk_usage_percent", "System Disk usage percentage", registry=custom_registry)

    # Set registerd system metrics gauge
    system_cpu.set(system_metrics["cpu_percent"])
    system_memory.set(system_metrics["memory_percent"])
    system_disk.set(system_metrics["disk_usage"])

    for name, container_stats in docker_metrics.items():
        if isinstance(container_stats, dict):
            docker_cpu = Gauge(f"container_cpu_usage_{name}", f"CPU usage for {name}", registry=custom_registry)
            docker_memory = Gauge(f"container_memory_usage_{name}", f"Memory usage for {name}", registry=custom_registry)

            docker_cpu.set(container_stats["cpu_usage"])
            docker_memory.set(container_stats["memory_usage"])

    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

