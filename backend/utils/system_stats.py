import docker

# Reuse Docker client instance
_docker_client = None

def get_docker_client():
    """Get or create Docker client instance"""
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    return _docker_client

def get_docker_stats(container_name):
    """Get Docker container statistics"""
    try:
        client = get_docker_client()
        container = client.containers.get(container_name)
        stats = container.stats(stream=False)
        
        return {
            "status": container.status,
            "stats": stats
        }
    except docker.errors.NotFound:
        return {"error": f"Container {container_name} not found"}
    except Exception as e:
        return {"error": str(e)}
