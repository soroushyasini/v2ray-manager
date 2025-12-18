import json
import os

CONFIG_PATH = os.getenv("V2RAY_CONFIG_PATH", "/etc/v2ray/config.json")

def read_config():
    """Read V2Ray configuration file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"Config file not found at {CONFIG_PATH}")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON in config file")

def write_config(config):
    """Write V2Ray configuration file"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to write config: {str(e)}")

def add_user(config, user_id, email, alter_id=64):
    """Add a user to V2Ray config"""
    if "inbounds" not in config:
        config["inbounds"] = []
    
    vmess_inbound = None
    for inbound in config["inbounds"]:
        if inbound.get("protocol") == "vmess":
            vmess_inbound = inbound
            break
    
    if not vmess_inbound:
        raise Exception("No VMess inbound found in config")
    
    if "settings" not in vmess_inbound:
        vmess_inbound["settings"] = {}
    if "clients" not in vmess_inbound["settings"]:
        vmess_inbound["settings"]["clients"] = []
    
    vmess_inbound["settings"]["clients"].append({
        "id": user_id,
        "alterId": alter_id,
        "email": email
    })
    
    return config

def remove_user(config, user_id):
    """Remove a user from V2Ray config"""
    if "inbounds" not in config:
        raise Exception("No inbounds in config")
    
    for inbound in config["inbounds"]:
        if inbound.get("protocol") == "vmess":
            clients = inbound.get("settings", {}).get("clients", [])
            inbound["settings"]["clients"] = [
                client for client in clients if client.get("id") != user_id
            ]
    
    return config
