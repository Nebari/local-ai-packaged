# Keiken Agent Portal Deployment Guide

## Production Deployment Configuration

### Backend (keiken.nebarisoftware.com)
The Keiken Multi-Agent Teams API should be deployed at `https://keiken.nebarisoftware.com`

**Key Endpoints:**
- `/api/agent` - Main agent execution endpoint
- `/v1/chat/completions` - OpenAI-compatible chat completions
- `/v1/models` - List available teams as models
- `/teams/{team_id}/execute` - Direct team execution for n8n
- `/docs` - API documentation

**Environment Variables:**
```bash
# Required for production
OLLAMA_URL=http://ollama:11434
SEARXNG_URL=http://searxng:8080
CORS_ORIGINS=https://keikendemo.nebarisoftware.com,https://open-webui:8080

# Optional
LOG_LEVEL=INFO
MAX_TOKENS=4096
```

### Frontend Deployments

#### 1. Chat Interface (keikendemo.nebarisoftware.com/chat)
Deploy the Streamlit chat UI at `https://keikendemo.nebarisoftware.com/chat`

**Features:**
- General-purpose AI conversation
- Multi-agent team selection  
- Conversation memory
- Thinking tag display

#### 2. Code Interface (keikendemo.nebarisoftware.com/code)  
Deploy the Streamlit code UI at `https://keikendemo.nebarisoftware.com/code`

**Features:**
- Codebase ZIP upload and analysis
- File structure visualization
- AI-powered code review and generation
- Context-aware programming assistance

### Team Configuration

**Available Teams (Models):**
- `Research` - Research Team with parallel workflow
- `CreativeStudio` - Creative Studio with sequential workflow  
- `SalesOps` - Sales Operations with routing workflow

### Open WebUI Integration

The backend provides OpenAI-compatible endpoints that can be integrated with Open WebUI:

1. **Server URL:** `https://keiken.nebarisoftware.com`
2. **Available Models:** Research, CreativeStudio, SalesOps
3. **Features:** 
   - Full conversation context
   - Thinking tags for reasoning transparency
   - Streaming responses
   - Internet search capabilities (Research team)

### Thinking Tags Feature

All agent responses include reasoning wrapped in `<thinking>` tags:
- Frontend automatically parses and displays reasoning in expandable sections
- Provides transparency into AI decision-making process  
- Follows team-specific workflow instructions

### Docker Compose Override for Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  praisonai-teams:
    environment:
      - CORS_ORIGINS=https://keikendemo.nebarisoftware.com
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.keiken-api.rule=Host(`keiken.nebarisoftware.com`)"
      - "traefik.http.routers.keiken-api.tls.certresolver=letsencrypt"
      
  praisonai-ui:
    environment:
      - API_BASE_URL=https://keiken.nebarisoftware.com
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.keiken-chat.rule=Host(`keikendemo.nebarisoftware.com`) && PathPrefix(`/chat`)"
      - "traefik.http.routers.keiken-chat.tls.certresolver=letsencrypt"
      
  keiken-code-ui:
    environment:
      - API_BASE_URL=https://keiken.nebarisoftware.com
    labels:
      - "traefik.enable=true"  
      - "traefik.http.routers.keiken-code.rule=Host(`keikendemo.nebarisoftware.com`) && PathPrefix(`/code`)"
      - "traefik.http.routers.keiken-code.tls.certresolver=letsencrypt"
```

### Testing Production Deployment

1. **API Health Check:** `GET https://keiken.nebarisoftware.com/health`
2. **Models List:** `GET https://keiken.nebarisoftware.com/v1/models`
3. **Chat Test:** `POST https://keiken.nebarisoftware.com/v1/chat/completions`
4. **UI Access:** `https://keikendemo.nebarisoftware.com/chat`

### Security Considerations

- Enable CORS for specific origins only
- Use HTTPS for all endpoints  
- Implement rate limiting for API endpoints
- Monitor usage and costs for Ollama/LLM usage
- Validate input sanitization for user queries