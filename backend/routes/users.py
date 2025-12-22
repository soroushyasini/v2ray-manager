from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from utils.v2ray_config import read_config, write_config, add_user, remove_user
from utils.qrcode_gen import generate_qrcode
from utils.v2ray_api import get_user_stats, add_user_via_api, remove_user_via_api, reset_user_stats

router = APIRouter()

class User(BaseModel):
    id: str
    name: str
    alter_id: int = 64
    created_at: str
    traffic_used: int = 0  # in bytes
    traffic_limit: int = 0  # in bytes, 0 = unlimited
    uplink: int = 0
    downlink: int = 0
    enabled: bool = True

class UserCreate(BaseModel):
    name: str
    alter_id: int = 64
    traffic_limit: int = 0  # in GB

@router.get("/users", response_model=List[User])
async def get_users():
    """Get all V2Ray users with traffic stats"""
    try:
        config = read_config()
        users = []
        
        if "inbounds" in config:
            for inbound in config["inbounds"]:
                if inbound.get("protocol") == "vmess":
                    clients = inbound.get("settings", {}).get("clients", [])
                    for client in clients:
                        email = client.get("email", "Unknown")
                        user_id = client.get("id")
                        
                        # Get real-time traffic stats from V2Ray API
                        stats = get_user_stats(email)
                        
                        users.append({
                            "id": user_id,
                            "name": email,
                            "alter_id": client.get("alterId", 64),
                            "created_at": datetime.now().isoformat(),
                            "traffic_used": stats["total"],
                            "traffic_limit": 0,  # Can be loaded from database
                            "uplink": stats["uplink"],
                            "downlink": stats["downlink"],
                            "enabled": True
                        })
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new V2Ray user without service interruption"""
    try:
        new_uuid = str(uuid.uuid4())
        config = read_config()
        
        # Add to config file (for persistence)
        add_user(config, new_uuid, user.name, user.alter_id)
        write_config(config)
        
        # Add via API for immediate effect (no restart needed!)
        api_success = add_user_via_api(new_uuid, user.name, user.alter_id)
        
        if not api_success:
            print("Warning: API add failed, user added to config only. Restart V2Ray to activate.")
        
        return {
            "id": new_uuid,
            "name": user.name,
            "alter_id": user.alter_id,
            "created_at": datetime.now().isoformat(),
            "traffic_used": 0,
            "traffic_limit": user.traffic_limit * 1024 * 1024 * 1024,  # GB to bytes
            "uplink": 0,
            "downlink": 0,
            "enabled": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a V2Ray user without service interruption"""
    try:
        config = read_config()
        
        # Find user email before removing
        user_email = None
        if "inbounds" in config:
            for inbound in config["inbounds"]:
                if inbound.get("protocol") == "vmess":
                    clients = inbound.get("settings", {}).get("clients", [])
                    for client in clients:
                        if client.get("id") == user_id:
                            user_email = client.get("email")
                            break
        
        # Remove from config
        remove_user(config, user_id)
        write_config(config)
        
        # Remove via API (no restart needed!)
        if user_email:
            api_success = remove_user_via_api(user_email)
            if not api_success:
                print("Warning: API remove failed, user removed from config only.")
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/qrcode")
async def get_user_qrcode(user_id: str):
    """Generate QR code for a user"""
    try:
        config = read_config()
        qr_code_base64 = generate_qrcode(config, user_id)
        
        return {"qrcode": qr_code_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/reset-stats")
async def reset_user_traffic(user_id: str):
    """Reset traffic statistics for a user"""
    try:
        config = read_config()
        
        # Find user email
        user_email = None
        if "inbounds" in config:
            for inbound in config["inbounds"]:
                if inbound.get("protocol") == "vmess":
                    clients = inbound.get("settings", {}).get("clients", [])
                    for client in clients:
                        if client.get("id") == user_id:
                            user_email = client.get("email")
                            break
        
        if not user_email:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = reset_user_stats(user_email)
        
        if success:
            return {"message": "Traffic stats reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset stats")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
