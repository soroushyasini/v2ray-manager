import docker

def get_docker_stats(container_name):
    """Get Docker container statistics"""
    try:
        client = docker.from_env()
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
