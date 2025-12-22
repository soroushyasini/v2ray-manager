import subprocess
import json
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configuration from environment variables
V2RAY_CONTAINER = os.getenv("V2RAY_CONTAINER", "v2ray")
V2RAY_API_HOST = os.getenv("V2RAY_API_HOST", "127.0.0.1")
V2RAY_API_PORT = os.getenv("V2RAY_API_PORT", "10085")

def add_user_via_api(user_id, email, alter_id=64, inbound_tag="proxy"):
    """Add user via V2Ray API without restart"""
    try:
        cmd = [
            "docker", "exec", V2RAY_CONTAINER,
            "/usr/bin/v2ray", "api", "adi", "inbound.user",
            f"--server={V2RAY_API_HOST}:{V2RAY_API_PORT}",
            f"--tag={inbound_tag}",
            f"--email={email}",
            f"--uuid={user_id}",
            f"--alterid={alter_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error adding user via API: {e}")
        return False

def remove_user_via_api(email, inbound_tag="proxy"):
    """Remove user via V2Ray API without restart"""
    try:
        cmd = [
            "docker", "exec", V2RAY_CONTAINER,
            "/usr/bin/v2ray", "api", "rmi", "inbound.user",
            f"--server={V2RAY_API_HOST}:{V2RAY_API_PORT}",
            f"--tag={inbound_tag}",
            f"--email={email}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error removing user via API: {e}")
        return False

def get_user_stats(email):
    """Get traffic stats for a user"""
    try:
        # Get uplink
        cmd_up = [
            "docker", "exec", V2RAY_CONTAINER,
            "/usr/bin/v2ray", "api", "statsquery",
            f"--server={V2RAY_API_HOST}:{V2RAY_API_PORT}",
            f"--pattern=user>>>{email}>>>traffic>>>uplink"
        ]
        result_up = subprocess.run(cmd_up, capture_output=True, text=True)
        
        # Get downlink
        cmd_down = [
            "docker", "exec", V2RAY_CONTAINER,
            "/usr/bin/v2ray", "api", "statsquery",
            f"--server={V2RAY_API_HOST}:{V2RAY_API_PORT}",
            f"--pattern=user>>>{email}>>>traffic>>>downlink"
        ]
        result_down = subprocess.run(cmd_down, capture_output=True, text=True)
        
        uplink = parse_stats(result_up.stdout)
        downlink = parse_stats(result_down.stdout)
        
        return {
            "uplink": uplink,
            "downlink": downlink,
            "total": uplink + downlink
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"uplink": 0, "downlink": 0, "total": 0}

def parse_stats(output):
    """Parse V2Ray stats output"""
    try:
        for line in output.split('\n'):
            if 'value:' in line:
                return int(line.split('value:')[1].strip())
    except Exception:
        pass
    return 0

def reset_user_stats(email):
    """Reset traffic stats for a user"""
    try:
        cmd = [
            "docker", "exec", V2RAY_CONTAINER,
            "/usr/bin/v2ray", "api", "stats",
            f"--server={V2RAY_API_HOST}:{V2RAY_API_PORT}",
            "--reset",
            f"user>>>{email}>>>traffic>>>uplink",
            f"user>>>{email}>>>traffic>>>downlink"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error resetting stats: {e}")
        return False
