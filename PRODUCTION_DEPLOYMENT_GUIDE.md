# Production Deployment Guide

**Date:** January 2025
**Version:** 2.0 - LangChain-Free System

## Overview

This guide provides comprehensive instructions for deploying the LangChain-free Tilores_X credit analysis platform to production environments.

## Pre-Deployment Checklist

### ✅ System Requirements

- Python 3.11+
- FastAPI 0.115.3+
- Uvicorn 0.25.0+
- All dependencies from `requirements.txt`

### ✅ Environment Variables

Ensure all required environment variables are configured:

```bash
# Tilores API Configuration
TILORES_GRAPHQL_API_URL=https://api.tilores.com/graphql
TILORES_OAUTH_TOKEN_URL=https://api.tilores.com/oauth/token
TILORES_CLIENT_ID=your_client_id
TILORES_CLIENT_SECRET=your_client_secret

# AI Provider API Keys
OPENAI_API_KEY=sk-your_openai_key
GROQ_API_KEY=gsk_your_groq_key
GOOGLE_API_KEY=your_google_api_key

# Application Configuration
PORT=8080
ENVIRONMENT=production
```

### ✅ File Structure Verification

Ensure the following files are present and updated:

- `main_direct.py` (Primary application)
- `direct_credit_api.py` (Core credit analysis)
- `requirements.txt` (LangChain-free dependencies)
- `Procfile` (Updated for main_direct.py)
- `railway.json` (Updated start command)
- `nixpacks.toml` (Updated start command)

## Deployment Methods

### Method 1: Railway Deployment (Recommended)

#### Step 1: Prepare Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Deploy LangChain-free system"
git push origin main
```

#### Step 2: Railway Configuration

The following files are already configured for Railway:

**Procfile:**

```
web: python main_direct.py
```

**railway.json:**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main_direct.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**nixpacks.toml:**

```toml
[start]
cmd = "python main_direct.py"
```

#### Step 3: Environment Variables

Set the following environment variables in Railway dashboard:

- `TILORES_GRAPHQL_API_URL`
- `TILORES_OAUTH_TOKEN_URL`
- `TILORES_CLIENT_ID`
- `TILORES_CLIENT_SECRET`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GOOGLE_API_KEY`
- `PORT=8080`

#### Step 4: Deploy

```bash
# Railway will automatically deploy from main branch
# Monitor deployment in Railway dashboard
```

### Method 2: Docker Deployment

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080

# Start application
CMD ["python", "main_direct.py"]
```

#### Step 2: Build and Deploy

```bash
# Build Docker image
docker build -t tilores-credit-api .

# Run container
docker run -d \
  --name tilores-api \
  -p 8080:8080 \
  -e TILORES_GRAPHQL_API_URL=$TILORES_GRAPHQL_API_URL \
  -e TILORES_OAUTH_TOKEN_URL=$TILORES_OAUTH_TOKEN_URL \
  -e TILORES_CLIENT_ID=$TILORES_CLIENT_ID \
  -e TILORES_CLIENT_SECRET=$TILORES_CLIENT_SECRET \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  tilores-credit-api
```

### Method 3: Traditional Server Deployment

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Create application directory
sudo mkdir -p /opt/tilores-api
sudo chown $USER:$USER /opt/tilores-api
cd /opt/tilores-api
```

#### Step 2: Application Deployment

```bash
# Clone repository
git clone https://github.com/your-repo/tilores_X.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/tilores-api.service
```

#### Step 3: Systemd Service Configuration

```ini
[Unit]
Description=Tilores Credit Analysis API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tilores-api
Environment=PATH=/opt/tilores-api/venv/bin
Environment=TILORES_GRAPHQL_API_URL=https://api.tilores.com/graphql
Environment=TILORES_OAUTH_TOKEN_URL=https://api.tilores.com/oauth/token
Environment=TILORES_CLIENT_ID=your_client_id
Environment=TILORES_CLIENT_SECRET=your_client_secret
Environment=OPENAI_API_KEY=sk-your_openai_key
Environment=GROQ_API_KEY=gsk_your_groq_key
Environment=GOOGLE_API_KEY=your_google_api_key
Environment=PORT=8080
ExecStart=/opt/tilores-api/venv/bin/python main_direct.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 4: Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable tilores-api

# Start service
sudo systemctl start tilores-api

# Check status
sudo systemctl status tilores-api
```

## Post-Deployment Verification

### Health Check

```bash
# Test health endpoint
curl http://your-domain:8080/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-XX", "version": "2.0"}
```

### API Testing

```bash
# Test chat completions endpoint
curl -X POST http://your-domain:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "What is Esteban Prices current credit score?"}
    ],
    "temperature": 0.7
  }'
```

### Model Listing

```bash
# Test models endpoint
curl http://your-domain:8080/v1/models

# Expected response: List of available models
```

## Monitoring & Maintenance

### Log Monitoring

```bash
# Railway logs
railway logs

# Docker logs
docker logs tilores-api

# Systemd logs
sudo journalctl -u tilores-api -f
```

### Performance Monitoring

- Monitor response times
- Track error rates
- Monitor API usage
- Check provider quotas

### Health Monitoring

- Set up health check alerts
- Monitor uptime
- Track response times
- Monitor error rates

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 8080
lsof -ti:8080

# Kill process if needed
kill $(lsof -ti:8080)
```

#### 2. Environment Variables Not Set

```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $TILORES_GRAPHQL_API_URL
```

#### 3. Dependencies Issues

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### 4. API Key Issues

- Verify API keys are valid
- Check provider quotas
- Ensure proper permissions

### Error Codes

- **500 Internal Server Error:** Check logs for specific error
- **404 Not Found:** Verify endpoint URLs
- **401 Unauthorized:** Check API keys
- **429 Too Many Requests:** Rate limiting active

## Security Considerations

### API Key Security

- Store API keys in environment variables
- Never commit keys to repository
- Rotate keys regularly
- Use least privilege principle

### Network Security

- Use HTTPS in production
- Implement proper CORS policies
- Use rate limiting
- Monitor for suspicious activity

### Data Security

- Encrypt sensitive data
- Implement proper logging
- Regular security audits
- Monitor access patterns

## Scaling Considerations

### Horizontal Scaling

- Use load balancer
- Multiple application instances
- Database connection pooling
- Caching layer (Redis)

### Vertical Scaling

- Increase server resources
- Optimize application code
- Database optimization
- CDN for static assets

## Backup & Recovery

### Application Backup

```bash
# Backup application code
tar -czf tilores-api-backup-$(date +%Y%m%d).tar.gz /opt/tilores-api

# Backup configuration
cp /etc/systemd/system/tilores-api.service /backup/
```

### Recovery Procedures

1. Restore application code
2. Restore configuration files
3. Restore environment variables
4. Restart services
5. Verify functionality

## Conclusion

This deployment guide provides comprehensive instructions for deploying the LangChain-free Tilores_X system to production. The system is now more robust, performant, and maintainable than the previous LangChain-based architecture.

**Status: Production Ready ✅**

For additional support, refer to the troubleshooting section or contact the development team.
