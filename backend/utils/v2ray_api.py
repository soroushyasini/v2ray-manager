import subprocess
import json

def add_user_via_api(user_id, email, alter_id=64, inbound_tag="proxy"):
    """Add user via V2Ray API without restart"""
    try:
        cmd = [
            "docker", "exec", "v2ray",
            "/usr/bin/v2ray", "api", "adi", "inbound.user",
            "--server=127.0.0.1:10085",
            f"--tag={inbound_tag}",
            f"--email={email}",
            f"--uuid={user_id}",
            f"--alterid={alter_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error adding user via API: {e}")
        return False

def remove_user_via_api(email, inbound_tag="proxy"):
    """Remove user via V2Ray API without restart"""
    try:
        cmd = [
            "docker", "exec", "v2ray",
            "/usr/bin/v2ray", "api", "rmi", "inbound.user",
            "--server=127.0.0.1:10085",
            f"--tag={inbound_tag}",
            f"--email={email}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error removing user via API: {e}")
        return False

def get_user_stats(email):
    """Get traffic stats for a user"""
    try:
        # Get uplink
        cmd_up = [
            "docker", "exec", "v2ray",
            "/usr/bin/v2ray", "api", "statsquery",
            "--server=127.0.0.1:10085",
            f"--pattern=user>>>{email}>>>traffic>>>uplink"
        ]
        result_up = subprocess.run(cmd_up, capture_output=True, text=True)
        
        # Get downlink
        cmd_down = [
            "docker", "exec", "v2ray",
            "/usr/bin/v2ray", "api", "statsquery",
            "--server=127.0.0.1:10085",
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
        print(f"Error getting stats: {e}")
        return {"uplink": 0, "downlink": 0, "total": 0}

def parse_stats(output):
    """Parse V2Ray stats output"""
    try:
        for line in output.split('\n'):
            if 'value:' in line:
                return int(line.split('value:')[1].strip())
    except:
        pass
    return 0

def reset_user_stats(email):
    """Reset traffic stats for a user"""
    try:
        cmd = [
            "docker", "exec", "v2ray",
            "/usr/bin/v2ray", "api", "stats",
            "--server=127.0.0.1:10085",
            "--reset",
            f"user>>>{email}>>>traffic>>>uplink",
            f"user>>>{email}>>>traffic>>>downlink"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error resetting stats: {e}")
        return False
