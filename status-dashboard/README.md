# KeikenV Status Dashboard

## Overview

The KeikenV Status Dashboard provides real-time monitoring of all services in your autonomous AI agent platform. It continuously monitors 29 services across multiple categories and provides health status, response times, and connectivity information.

## Access Points

### Production (HTTPS)
- **Domain**: https://status.nebarisoftware.com
- **Description**: Secure production access via Caddy reverse proxy with Let's Encrypt SSL

### Development  
- **Local**: http://localhost:8930
- **Description**: Direct access for development and testing

## Features

### Real-time Monitoring
- ✅ Automatic health checks every 30 seconds
- 📊 Response time monitoring
- 🔄 Auto-refresh dashboard
- 📱 Mobile-responsive design

### Service Categories

#### Core Infrastructure (7 services)
- OpenWebUI - AI Chat Interface
- n8n - Workflow Automation  
- Ollama - Local LLM Server
- Qdrant - Vector Database
- Redis - Cache & Memory Store
- PostgreSQL - Primary Database
- Flowise - AI Workflow Builder

#### AI Services (15 services)
- PresEnton - AI Presentation Generator
- MLflow - ML Experiment Tracking
- LiteLLM - Universal LLM API Proxy
- ComfyUI - Node-based AI Workflows
- Automatic1111 - Stable Diffusion WebUI
- InvokeAI - AI Image Generation
- Mem0 - AI Memory Layer
- Perplexica - AI-Powered Search Engine
- Keiken Teams API - Multi-Agent Teams API
- Keiken Main UI - Main Keiken Interface
- Keiken UI Interface - Collaborative Multi-Agent UI
- Keiken Code Interface - Codebase Analysis Interface
- Keiken Chat Interface - Single-Agent Chat Interface
- OpenMemory MCP - Memory Context Protocol
- Pinokio - AI App Launcher

#### Supporting Services (7 services)
- Searxng - Privacy Search Engine
- ClickHouse - Analytics Database
- MinIO - Object Storage
- Langfuse Web - LLM Observability
- Supabase Analytics - Database Analytics
- Neo4j - Graph Database
- Caddy - Reverse Proxy

### Status Indicators

- 🟢 **Healthy**: Service responding normally (HTTP 200-299)
- 🟡 **Degraded**: Some services unhealthy but system functional
- 🔴 **Unhealthy**: Service not responding or error status
- ⚪ **Unknown**: Service status cannot be determined

## API Endpoints

### Status API
```bash
GET /api/status          # Full status check (slower)
GET /api/status/cached   # Cached status (faster)
GET /api/health          # Dashboard health
```

### Sample Response
```json
{
  "overall": {
    "status": "healthy",
    "healthy": 22,
    "unhealthy": 0,
    "unknown": 2,
    "total": 29,
    "checkDuration": 1205,
    "lastUpdated": "2025-10-22T23:16:47.599Z"
  },
  "services": [...],
  "categories": {...}
}
```

## Service URLs

Each service card shows:
- Internal container URL (`http://service:port`)
- External HTTPS URL when available via domain
- Health status and response time
- Service description and current status

## Technical Details

### Health Check Logic
- Services are checked via HTTP GET requests
- Timeout: 5 seconds per service
- Status codes 200-499 considered "healthy"
- Status codes 500+ or network errors considered "unhealthy"
- Missing health endpoints marked as "unknown"

### Auto-refresh
- Dashboard updates every 30 seconds
- Manual refresh on browser focus
- Real-time status updates without page reload

### Container Details
- **Image**: node:18-slim
- **Port**: 3100 (internal), 8930 (external)
- **Network**: keiken-network + default
- **Dependencies**: express, axios, cors

## Deployment

The status dashboard is automatically deployed as part of the docker-compose stack:

```bash
docker-compose up -d status-dashboard
```

## Configuration

Service definitions are maintained in `/status-dashboard/server.js`. To add new services:

1. Edit the `services` array in `server.js`
2. Add service details (name, category, URLs, description)
3. Restart the status dashboard container
4. Optionally add Caddy routing for external access

## Troubleshooting

### Dashboard Not Loading
- Check container status: `docker ps | grep status-dashboard`
- View logs: `docker logs status-dashboard`
- Verify port 8930 is accessible

### Services Showing Unhealthy
- Check individual service logs
- Verify network connectivity between containers
- Confirm service is actually running and responsive

### Missing External URLs
- Some services may not have external access configured
- Internal URLs show container-to-container communication
- External URLs require port mapping or proxy configuration

## Monitoring Integration

The dashboard can be integrated with:
- Prometheus/Grafana for metrics collection
- Alert systems for service failure notifications  
- Log aggregation systems for centralized monitoring
- Health check services for external monitoring

---

*Part of the KeikenV Autonomous AI Agent Platform*