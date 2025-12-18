import qrcode
import json
import base64
from io import BytesIO
import os

DOMAIN = os.getenv("DOMAIN", "management.hamnaghsheh.ir")
PORT = os.getenv("PORT", "8443")

def generate_vmess_url(user_id, email, alter_id=64):
    """Generate VMess URL for client configuration"""
    config = {
        "v": "2",
        "ps": email,
        "add": DOMAIN,
        "port": PORT,
        "id": user_id,
        "aid": str(alter_id),
        "net": "tcp",
        "type": "none",
        "host": "",
        "path": "",
        "tls": "tls"
    }
    
    json_str = json.dumps(config)
    base64_str = base64.b64encode(json_str.encode()).decode()
    return f"vmess://{base64_str}"

def generate_qrcode(config, user_id):
    """Generate QR code for a user's configuration"""
    user_email = "Unknown"
    alter_id = 64
    
    if "inbounds" in config:
        for inbound in config["inbounds"]:
            if inbound.get("protocol") == "vmess":
                clients = inbound.get("settings", {}).get("clients", [])
                for client in clients:
                    if client.get("id") == user_id:
                        user_email = client.get("email", "Unknown")
                        alter_id = client.get("alterId", 64)
                        break
    
    vmess_url = generate_vmess_url(user_id, user_email, alter_id)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vmess_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return img_base64
