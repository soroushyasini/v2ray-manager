from fastapi import APIRouter, HTTPException
import psutil
from utils.system_stats import get_docker_stats

router = APIRouter()

@router.get("/stats/system")
async def get_system_stats():
    """Get system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "percent": disk.percent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/v2ray")
async def get_v2ray_stats():
    """Get V2Ray container statistics"""
    try:
        stats = get_docker_stats("v2ray")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
