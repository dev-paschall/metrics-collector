import psutil
import docker
from docker.errors import DockerException, APIError
from typing import Dict, Any

def get_system_metrics() -> Dict[str, float]:
    '''Extracts the current CPU, memory, and disk usage percentages for the host resources.'''
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
    }

def get_docker_metrics() -> Dict[str, Any]:
    '''Extracts and calculates CPU and memory usage percentages for all running Docker containers.'''
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        containers = docker_client.containers.list()
        stats: Dict[str, Any] = {}

        for container in containers:
            # fetche one immediate, non-stop snapshot of all current resource usage data for the container and stores it as a dictionary
            c_stats = container.stats(stream=False)

            cpu_usage_percent = 0.0

            # The difference in the container's total CPU usage between the current scrape (c_stats) and the previous scrape (precpu_stats). This tells you how many nanoseconds the container used in that short interval.
            cpu_delta = c_stats["cpu_stats"]["cpu_usage"]["total_usage"] - c_stats["precpu_stats"]["cpu_usage"]["total_usage"]
        
            # The difference in the host system's total CPU usage between the current and previous scrape. This is the total time the host system's CPUs were available in that interval.
            system_delta = c_stats["cpu_stats"]["system_cpu_usage"] - c_stats["precpu_stats"]["system_cpu_usage"]
        
            # Gets the number of CPU cores the container sees. We need to multiply the ratio by this number because Docker CPU limits are based on one core. If a container uses 100% of two cores, it has an effective 200% usage relative to a single core.
            online_cpus = c_stats["cpu_stats"].get("online_cpus", len(c_stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) if c_stats["cpu_stats"].get("percpu_usage") else 1)
            
            # Ensures it don't divide by zero and that it only calculate if it have valid usage change.
            if system_delta > 0 and cpu_delta > 0:
                # This is the final percentage calculation. It converts the usage ratio into a percentage based on all available cores.
                cpu_usage_percent = (cpu_delta / system_delta) * online_cpus * 100.0
            
            memory_usage_bytes = c_stats["memory_stats"]["usage"]
            memory_limit_bytes = c_stats["memory_stats"]["limit"]
            memory_usage_percent = (memory_usage_bytes / memory_limit_bytes) * 100.0

            stats[container.name] = {
                "cpu_usage": cpu_usage_percent, # Updated to be percentage (0-100)
                "memory_usage": memory_usage_percent, # Updated to be percentage (0-100)
            }

        if not containers:
            stats = {"info": "No running container available"}

        print(stats)
        return stats

    except (DockerException, APIError) as e:
        print(f"Docker error: {e}")
        return {"error": "Docker not available or failed to fetch stats"}

    
           