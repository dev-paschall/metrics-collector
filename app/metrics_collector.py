import psutil
import docker
from docker.errors import DockerException, APIError
from typing import Dict, Any

def get_system_metrics() -> Dict[str, float]:
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
    }

def get_docker_metrics() -> Dict[str, Any]:
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        containers = docker_client.containers.list()
        stats: Dict[str, Any] = {}

        for container in containers:
            c_stats = container.stats(stream=False)
            stats[container.name] = {
                "cpu_usage": c_stats["cpu_stats"]["cpu_usage"]["total_usage"],
                "memory_usage": c_stats["memory_stats"]["usage"],
            }

        if not containers:
            stats = {"info": "No running container available"}

        print(stats)
        return stats

    except (DockerException, APIError) as e:
        print(f"Docker error: {e}")
        return {"error": "Docker not available or failed to fetch stats"}
