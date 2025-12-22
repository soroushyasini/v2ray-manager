# V2Ray Manager Dashboard

A lightweight, resource-efficient web dashboard for managing V2Ray server users and monitoring system performance.

## Features

- 📊 **Real-time System Monitoring**: CPU, RAM, and disk usage
- 👥 **User Management**: Add, delete, and manage V2Ray users
- 📱 **QR Code Generation**: Generate client configuration QR codes
- 🐳 **Docker Support**: Easy deployment with Docker
- ⚡ **Lightweight**: Optimized for low-resource VPS environments

## Requirements

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- V2Ray server running with VMess protocol

## Installation

### Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/soroushyasini/v2ray-manager.git
cd v2ray-manager
```

2. Set environment variables:
```bash
export V2RAY_CONFIG_PATH=/path/to/v2ray/config.json
export DOMAIN=your-domain.com
export PORT=8443
```

3. Build and run with Docker Compose:
```bash
cd docker
docker-compose up -d
```

4. Access the dashboard at `http://your-server-ip:8000`

### Manual Deployment

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export V2RAY_CONFIG_PATH=/etc/v2ray/config.json
export DOMAIN=management.hamnaghsheh.ir
export PORT=8443
```

3. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

- `V2RAY_CONFIG_PATH`: Path to V2Ray configuration file (default: `/etc/v2ray/config.json`)
- `DOMAIN`: Your V2Ray server domain (default: `management.hamnaghsheh.ir`)
- `PORT`: Your V2Ray server port (default: `8443`)

## V2Ray API Configuration

For zero-downtime user management and traffic monitoring, you need to enable V2Ray API.

### Add to your V2Ray config.json:

```json
{
  "api": {
    "tag": "api",
    "services": [
      "HandlerService",
      "StatsService"
    ]
  },
  "stats": {},
  "policy": {
    "levels": {
      "0": {
        "statsUserUplink": true,
        "statsUserDownlink": true
      }
    },
    "system": {
      "statsInboundUplink": true,
      "statsInboundDownlink": true
    }
  },
  "inbounds": [
    {
      "listen": "127.0.0.1",
      "port": 10085,
      "protocol": "dokodemo-door",
      "settings": {
        "address": "127.0.0.1"
      },
      "tag": "api"
    },
    ... your existing inbounds ...
  ],
  "routing": {
    "rules": [
      {
        "inboundTag": ["api"],
        "outboundTag": "api",
        "type": "field"
      },
      ... your existing rules ...
    ]
  }
}
```

After updating the config, restart V2Ray once:
```bash
docker restart v2ray
```

After this initial setup, all future user additions/removals will happen without restart!

## API Endpoints

### Users
- `GET /api/users` - List all users
- `POST /api/users` - Create a new user
- `DELETE /api/users/{user_id}` - Delete a user
- `GET /api/users/{user_id}/qrcode` - Generate QR code

### Stats
- `GET /api/stats/system` - Get system statistics
- `GET /api/stats/v2ray` - Get V2Ray container stats

### Config
- `GET /api/config` - Get V2Ray configuration
- `PUT /api/config` - Update V2Ray configuration

## Security Considerations

- Always run the dashboard behind a reverse proxy (Nginx/Caddy) with HTTPS
- Implement authentication before exposing to the internet
- Restrict access by IP if possible
- Keep the application updated
- Use strong passwords/UUIDs

## Resource Usage

Optimized for low-resource environments:
- Memory: ~150-200MB
- CPU: Minimal overhead with async operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Author

Created for efficient V2Ray server management on resource-constrained VPS environments.
