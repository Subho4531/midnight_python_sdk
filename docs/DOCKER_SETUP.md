# 🐳 midnight-py Docker Setup

## Overview

You now have **two options** for running Midnight services:

1. **Local Mock Services** (Recommended for development)
   - Fast startup
   - No external dependencies
   - Simulates real behavior
   - Perfect for testing

2. **Real Midnight Images** (For production-like testing)
   - Official Midnight Docker images
   - Real blockchain behavior
   - Requires more resources

## 🚀 Quick Start

### Option 1: Local Mock Services (Recommended)

**Windows:**
```bash
start_docker.bat
```

**Linux/Mac:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

### Option 2: Real Midnight Images

**Windows:**
```bash
start_docker.bat --real
```

**Linux/Mac:**
```bash
./start_docker.sh --real
```

## 📋 What Gets Started

### Local Mock Services
- **midnight-node-local** (port 9944)
  - Mock blockchain node
  - JSON-RPC interface
  - Transaction handling
  
- **midnight-indexer-local** (port 8088)
  - GraphQL API
  - WebSocket subscriptions
  - State queries
  
- **midnight-proof-local** (port 6300)
  - ZK proof generation (simulated, 2s delay)
  - Proof verification

### Real Services (if using --real)
- **midnight-node** - Real Midnight blockchain node
- **midnight-indexer** - Real GraphQL indexer
- **midnight-proof-server** - Real ZK proof generation
- **postgres** - Database for indexer

## ✅ Verify Services

After starting, check status:

```bash
# Check with midnight-py CLI
midnight-py status

# Or check Docker containers
docker ps

# View logs
docker-compose -f docker-compose.local.yml logs -f
```

Expected output:
```
Service    Status      URL
Node       ✓ ONLINE    http://127.0.0.1:9944
Indexer    ✓ ONLINE    http://127.0.0.1:8088/api/v3/graphql
Prover     ✓ ONLINE    http://127.0.0.1:6300
```

## 🎯 Run the Demo

Once services are running:

```bash
# Update the demo to use your wallet
python examples/bulletin_board.py

# Or run the real network demo
python examples/real_demo.py
```

## 🛠️ Management Commands

### Start Services
```bash
# Windows
start_docker.bat

# Linux/Mac
./start_docker.sh
```

### Stop Services
```bash
# Windows
stop_docker.bat

# Linux/Mac
./stop_docker.sh
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.local.yml logs -f

# Specific service
docker-compose -f docker-compose.local.yml logs -f midnight-node-mock
```

### Restart Services
```bash
# Stop and start again
docker-compose -f docker-compose.local.yml restart
```

### Clean Up Everything
```bash
# Stop and remove containers, networks, volumes
docker-compose -f docker-compose.local.yml down -v
```

## 📊 Service Details

### Node (Port 9944)
**Endpoints:**
- `POST /` - JSON-RPC 2.0
- `GET /health` - Health check
- `GET /balance/{address}` - Get balance
- `POST /wallet/sign` - Sign transaction
- `POST /transactions` - Submit transaction
- `POST /contracts/deploy` - Deploy contract

**Example:**
```bash
curl http://localhost:9944/health
```

### Indexer (Port 8088)
**Endpoints:**
- `POST /api/v3/graphql` - GraphQL queries
- `WS /api/v3/graphql/ws` - WebSocket subscriptions
- `GET /health` - Health check

**Example:**
```bash
curl -X POST http://localhost:8088/api/v3/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### Proof Server (Port 6300)
**Endpoints:**
- `POST /prove` - Generate ZK proof
- `POST /verify` - Verify proof
- `GET /health` - Health check

**Example:**
```bash
curl http://localhost:6300/health
```

## 🐛 Troubleshooting

### Services won't start

**Problem:** Docker containers fail to start

**Solutions:**
1. Check Docker is running:
   ```bash
   docker info
   ```

2. Check port conflicts:
   ```bash
   # Windows
   netstat -ano | findstr "9944"
   netstat -ano | findstr "8088"
   netstat -ano | findstr "6300"
   
   # Linux/Mac
   lsof -i :9944
   lsof -i :8088
   lsof -i :6300
   ```

3. Stop conflicting services:
   ```bash
   # Stop dev_server.py if running
   pkill -f dev_server.py
   ```

### Services show as unhealthy

**Problem:** `docker ps` shows unhealthy status

**Solutions:**
1. Check logs:
   ```bash
   docker-compose -f docker-compose.local.yml logs
   ```

2. Restart services:
   ```bash
   docker-compose -f docker-compose.local.yml restart
   ```

3. Rebuild containers:
   ```bash
   docker-compose -f docker-compose.local.yml up -d --build --force-recreate
   ```

### midnight-py can't connect

**Problem:** `midnight-py status` shows all offline

**Solutions:**
1. Verify containers are running:
   ```bash
   docker ps
   ```

2. Check if ports are accessible:
   ```bash
   curl http://localhost:9944/health
   curl http://localhost:8088/health
   curl http://localhost:6300/health
   ```

3. Check firewall settings (Windows):
   - Allow Docker through Windows Firewall
   - Allow Python through Windows Firewall

### Out of disk space

**Problem:** Docker runs out of space

**Solutions:**
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything
docker system prune -a --volumes
```

## 🔄 Switching Between Mock and Real

### From Mock to Real
```bash
# Stop mock services
docker-compose -f docker-compose.local.yml down

# Start real services
./start_docker.sh --real
```

### From Real to Mock
```bash
# Stop real services
docker-compose -f docker-compose.real.yml down

# Start mock services
./start_docker.sh
```

## 📁 Docker Files Structure

```
midnightsdk/
├── docker-compose.local.yml    # Local mock services
├── docker-compose.real.yml     # Real Midnight images
├── start_docker.sh             # Start script (Linux/Mac)
├── start_docker.bat            # Start script (Windows)
├── stop_docker.sh              # Stop script (Linux/Mac)
├── stop_docker.bat             # Stop script (Windows)
└── docker/
    ├── node/
    │   ├── Dockerfile
    │   └── server.py
    ├── indexer/
    │   ├── Dockerfile
    │   └── server.py
    └── proof/
        ├── Dockerfile
        └── server.py
```

## 🎯 For the Hackathon

### Demo Flow with Docker

1. **Start services:**
   ```bash
   start_docker.bat  # or ./start_docker.sh
   ```

2. **Verify:**
   ```bash
   midnight-py status
   ```

3. **Run demo:**
   ```bash
   python examples/bulletin_board.py
   ```

4. **Show judges:**
   - Docker containers running: `docker ps`
   - Services healthy: `midnight-py status`
   - Real transactions: Show TX hash from demo

### Advantages for Demo

✅ **No manual setup** - One command starts everything
✅ **Consistent environment** - Works on any machine with Docker
✅ **Easy reset** - `docker-compose down` and start fresh
✅ **Professional** - Shows you know Docker/containers
✅ **Portable** - Can demo on any laptop

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Midnight Documentation](https://docs.midnight.network/)

## 🎉 You're Ready!

Your Midnight services are now running in Docker containers. You can:

- ✅ Start/stop services with one command
- ✅ Run demos without manual setup
- ✅ Reset environment easily
- ✅ Show professional deployment

**Run your first demo:**
```bash
midnight-py status
python examples/bulletin_board.py
```

🌙 Happy hacking!
