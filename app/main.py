from fastapi import FastAPI
from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from metrics_collector import get_docker_metrics, get_system_metrics # Assuming this is correct

app = FastAPI(title="Devops Metrics Collector")

# Initialize the custom registry and all metrics at startup
custom_registry = CollectorRegistry(auto_describe=True) # auto_describe=True is helpful

REQUEST_COUNT = Counter("request_count", "Number of requests", registry=custom_registry)

# System Metrics Gauges (Initialized ONCE)
SYSTEM_CPU = Gauge("system_cpu_percent", "System CPU usage percentage", registry=custom_registry)
SYSTEM_MEMORY = Gauge("system_memory_percent", "System Memory usage percentage", registry=custom_registry)
SYSTEM_DISK = Gauge("system_disk_usage_percent", "System Disk usage percentage", registry=custom_registry)

# Dictionary to store dynamically created Docker Gauges
# Key: container_name -> Value: (cpu_gauge, memory_gauge)
DOCKER_GAUGES = {}


@app.get("/")
def root():
    return {"message": "Devops metrics collector running..."}


@app.get("/metrics")
def get_metrics():
    # Increment the request counter
    REQUEST_COUNT.inc()
    
    system_metrics = get_system_metrics()
    docker_metrics = get_docker_metrics()

    # Set values for system metrics (DO NOT RE-CREATE)
    SYSTEM_CPU.set(system_metrics["cpu_percent"])
    SYSTEM_MEMORY.set(system_metrics["memory_percent"])
    SYSTEM_DISK.set(system_metrics["disk_usage"])

    # Handle Docker metrics dynamically
    if "error" not in docker_metrics:
        current_containers = set(docker_metrics.keys())
        
        # Prune metrics for stopped/removed containers
        for name in list(DOCKER_GAUGES.keys()):
            if name not in current_containers:
                # You can't unregister a timeseries directly, but this is a simplification.
                # If you use Labels, Prometheus client handles missing labels more gracefully.
                del DOCKER_GAUGES[name] 

        for name, container_stats in docker_metrics.items():
            if isinstance(container_stats, dict):
                # Create/Get Gauges dynamically
                if name not in DOCKER_GAUGES:
                    # Create the Gauge for this container if it doesn't exist (Registration happens here)
                    docker_cpu = Gauge(f"container_cpu_usage_{name}", f"CPU usage for {name}", registry=custom_registry)
                    docker_memory = Gauge(f"container_memory_usage_{name}", f"Memory usage for {name}", registry=custom_registry)
                    DOCKER_GAUGES[name] = (docker_cpu, docker_memory)
                else:
                    # Retrieve existing Gauges
                    docker_cpu, docker_memory = DOCKER_GAUGES[name]

                # Set new values
                docker_cpu.set(container_stats["cpu_usage"])
                docker_memory.set(container_stats["memory_usage"])

    # Return the latest metrics
    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)
