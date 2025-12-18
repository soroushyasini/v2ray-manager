from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from utils.v2ray_config import read_config, write_config

router = APIRouter()

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

@router.get("/config")
async def get_config():
    """Get current V2Ray configuration"""
    try:
        config = read_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_config(config_update: ConfigUpdate):
    """Update V2Ray configuration"""
    try:
        write_config(config_update.config)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
