# Deployment Guide

Deploy your LayerCode agent to production environments.

## Deployment Options

### 1. Traditional Server (VPS/EC2)

Deploy to a virtual private server or cloud instance.

#### Requirements

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.12+
- Reverse proxy (Nginx/Caddy)
- Process manager (systemd/supervisor)

#### Setup Steps

**1. Install dependencies:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-venv

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Clone and setup:**

```bash
# Clone repository
git clone https://github.com/yourusername/layercode-create-app.git
cd layercode-create-app

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
nano .env  # Edit with your credentials
```

**3. Create systemd service:**

Create `/etc/systemd/system/layercode-agent.service`:

```ini
[Unit]
Description=LayerCode Agent Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/layercode-create-app
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/.local/bin/uv run layercode-create-app run --agent starter --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable layercode-agent
sudo systemctl start layercode-agent
sudo systemctl status layercode-agent
```

**5. Configure Nginx:**

Create `/etc/nginx/sites-available/layercode`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/layercode /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. Docker Deployment

Deploy using Docker containers.

#### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "layercode-create-app", "run", "--agent", "starter", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  layercode-agent:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 3. Cloud Platforms

#### Railway

1. Push your code to GitHub
2. Create new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy automatically on push

#### Render

1. Push your code to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `uv sync`
   - **Start Command**: `uv run layercode-create-app run --agent starter --port 8000`
5. Add environment variables
6. Deploy

#### Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Create `fly.toml`:

```toml
app = "layercode-agent"
primary_region = "sjc"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
```

4. Deploy: `flyctl deploy`
5. Set secrets: `flyctl secrets set LAYERCODE_API_KEY=...`

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```env
# LayerCode
LAYERCODE_API_KEY=lk_live_...
LAYERCODE_WEBHOOK_SECRET=whsec_...

# AI Provider
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=openai:gpt-5-nano

# Observability
LOGFIRE_TOKEN=lf_...

# Server
HOST=0.0.0.0
PORT=8000
```

### Security Best Practices

1. **Use secrets management**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Cloud provider secret stores

2. **Rotate credentials regularly**:
   ```bash
   # Update secrets without downtime
   flyctl secrets set OPENAI_API_KEY=new_key
   ```

3. **Limit API access**:
   - Use IP allowlists where possible
   - Implement rate limiting
   - Monitor for unusual activity

## Monitoring

### Health Checks

Implement health check endpoints:

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/ready")
async def ready():
    # Check dependencies
    try:
        # Test database connection, etc.
        return {"ready": True}
    except Exception:
        return {"ready": False}, 503
```

### Logging

Configure structured logging:

```python
import loguru

logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time} {level} {message}",
)
```

### Metrics with Logfire

Enable Logfire for production monitoring:

```env
LOGFIRE_TOKEN=lf_live_...
```

Monitor:
- Request latency
- Error rates
- Agent response times
- Resource usage

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```yaml
# docker-compose.yml
version: '3.8'

services:
  layercode-agent:
    build: .
    deploy:
      replicas: 3
    env_file:
      - .env

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - layercode-agent
```

### Vertical Scaling

Increase resources for compute-intensive agents:

```yaml
# docker-compose.yml
services:
  layercode-agent:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Troubleshooting

### Check Logs

```bash
# Systemd
sudo journalctl -u layercode-agent -f

# Docker
docker-compose logs -f layercode-agent

# Fly.io
flyctl logs
```

### Test Webhook Endpoint

```bash
curl -X POST https://your-domain.com/api/agent \
  -H "Content-Type: application/json" \
  -H "layercode-signature: test" \
  -d '{"type":"call_started","call_id":"test"}'
```

### Debug Mode

Enable verbose logging in production:

```bash
uv run layercode-create-app run --agent starter --verbose
```

## Next Steps

- [Observability Guide](observability.md) - Set up monitoring
- [Troubleshooting](troubleshooting.md) - Common issues
