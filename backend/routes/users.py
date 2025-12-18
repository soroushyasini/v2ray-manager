from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

from utils.v2ray_config import read_config, write_config, add_user, remove_user
from utils.qrcode_gen import generate_qrcode

router = APIRouter()

class User(BaseModel):
    id: str
    name: str
    alter_id: int = 64
    created_at: str

class UserCreate(BaseModel):
    name: str
    alter_id: int = 64

@router.get("/users", response_model=List[User])
async def get_users():
    """Get all V2Ray users"""
    try:
        config = read_config()
        users = []
        
        if "inbounds" in config:
            for inbound in config["inbounds"]:
                if inbound.get("protocol") == "vmess":
                    clients = inbound.get("settings", {}).get("clients", [])
                    for client in clients:
                        users.append({
                            "id": client.get("id"),
                            "name": client.get("email", "Unknown"),
                            "alter_id": client.get("alterId", 64),
                            "created_at": datetime.now().isoformat()
                        })
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new V2Ray user"""
    try:
        new_uuid = str(uuid.uuid4())
        config = read_config()
        
        add_user(config, new_uuid, user.name, user.alter_id)
        write_config(config)
        
        return {
            "id": new_uuid,
            "name": user.name,
            "alter_id": user.alter_id,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a V2Ray user"""
    try:
        config = read_config()
        remove_user(config, user_id)
        write_config(config)
        
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
