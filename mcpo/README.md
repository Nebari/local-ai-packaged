# MCPO (Model Context Protocol Orchestrator) Integration

## Overview

MCPO is a powerful MCP-to-OpenAPI proxy that exposes Model Context Protocol (MCP) servers as standard REST APIs. This integration allows KeikenV's multi-agent framework to seamlessly interact with MCP-compatible tools through familiar HTTP endpoints.

## Service Details

- **Container**: `mcpo`
- **Image**: `ghcr.io/open-webui/mcpo:main`
- **Port**: 8940 (external) → 8000 (internal)
- **API Documentation**: http://localhost:8940/docs
- **Health Check**: http://localhost:8940/health

## Key Features

### 🔄 Protocol Translation
- Converts MCP stdio protocols to HTTP REST APIs
- Auto-generates OpenAPI schemas for all MCP tools
- Provides interactive documentation for each endpoint

### 🛡️ Security & Stability
- API key authentication (`keiken-mcpo-secret-2024`)
- Standard HTTP security practices
- Error handling and request validation

### 🧠 Integrated MCP Servers

#### Built-in Tools
1. **Memory Server** (`/memory`)
   - In-memory storage for session data
   - Temporary variable storage
   - Cross-agent data sharing

2. **Time Server** (`/time`) 
   - Current time and date utilities
   - Timezone conversions (America/New_York)
   - Scheduling and temporal operations

3. **Filesystem Server** (`/filesystem`)
   - Secure file operations in `/tmp`
   - Temporary file management
   - Agent workspace handling

4. **Web Search** (`/web-search`)
   - Brave Search API integration
   - Real-time web information retrieval
   - Search result processing

5. **GitHub Server** (`/github`)
   - Repository management
   - Issue tracking
   - Pull request operations

6. **SQLite Server** (`/sqlite`)
   - Persistent data storage
   - Agent state management
   - Query execution

#### KeikenV Service Integrations
1. **OpenWebUI Local** (`/openwebui-local`)
   - Direct integration with Open WebUI
   - Chat interface bridging
   - User session management

2. **Mem0 Memory** (`/mem0-memory`)
   - AI memory system access
   - Long-term memory storage
   - Context preservation

3. **n8n Workflows** (`/n8n-workflows`)
   - Workflow automation triggers
   - Agent task orchestration
   - Process coordination

## Configuration

### Environment Variables
- `MCPO_API_KEY`: Authentication key for API access
- `BRAVE_API_KEY`: Optional Brave Search API key
- `GITHUB_TOKEN`: Optional GitHub access token
- `OPENWEBUI_API_KEY`: OpenWebUI integration key
- `MEM0_API_KEY`: Mem0 service authentication
- `N8N_API_KEY`: n8n workflow access key

### Configuration File
The MCPO configuration is stored in `/mcpo/mcpo.json` and follows the Claude Desktop format for MCP server definitions.

## Usage Examples

### Basic API Access
```bash
# List all available tools
curl -H "Authorization: Bearer keiken-mcpo-secret-2024" \
     http://localhost:8940/

# Get memory tool schema
curl -H "Authorization: Bearer keiken-mcpo-secret-2024" \
     http://localhost:8940/memory/docs

# Store data in memory
curl -X POST \
     -H "Authorization: Bearer keiken-mcpo-secret-2024" \
     -H "Content-Type: application/json" \
     -d '{"key": "agent_state", "value": "processing"}' \
     http://localhost:8940/memory/store
```

### Integration with KeikenV Agents
```python
import requests

class MCPClient:
    def __init__(self):
        self.base_url = "http://localhost:8940"
        self.headers = {
            "Authorization": "Bearer keiken-mcpo-secret-2024",
            "Content-Type": "application/json"
        }
    
    def search_web(self, query):
        response = requests.post(
            f"{self.base_url}/web-search/search",
            headers=self.headers,
            json={"query": query}
        )
        return response.json()
    
    def store_memory(self, key, value):
        response = requests.post(
            f"{self.base_url}/memory/store", 
            headers=self.headers,
            json={"key": key, "value": value}
        )
        return response.json()
```

### OpenWebUI Integration
MCPO can be registered as an OpenAPI server in OpenWebUI:
1. Navigate to Settings → Connections → OpenAPI Servers
2. Add new server: `http://localhost:8940`
3. Set API key: `keiken-mcpo-secret-2024`
4. Enable desired MCP tools for chat integration

## Agent Framework Integration

### Multi-Agent Coordination
```json
{
  "agent_config": {
    "mcp_proxy": "http://localhost:8940",
    "api_key": "keiken-mcpo-secret-2024",
    "available_tools": [
      "memory", "time", "web-search", 
      "github", "filesystem", "sqlite"
    ]
  }
}
```

### PraisonAI Teams Integration
Each PraisonAI team can leverage MCPO tools:
- **Research Team**: Web search, GitHub, filesystem
- **Coding Team**: GitHub, filesystem, memory, sqlite  
- **Business Team**: Memory, time, web search
- **Creative Team**: Filesystem, memory, web search

## Monitoring & Health

### Health Checks
- Endpoint: `GET /health`
- Returns server status and active MCP connections
- Monitored by KeikenV status dashboard

### Logs & Debugging
```bash
# View MCPO logs
docker logs mcpo

# Check individual MCP server health  
curl -H "Authorization: Bearer keiken-mcpo-secret-2024" \
     http://localhost:8940/memory/health
```

## Development & Extension

### Adding New MCP Servers
1. Edit `/mcpo/mcpo.json`
2. Add server configuration
3. Restart MCPO service
4. Verify at `/docs` endpoint

### Custom MCP Server Example
```json
{
  "custom-tool": {
    "command": "python",
    "args": ["/path/to/custom_mcp_server.py"],
    "description": "Custom business logic MCP server",
    "env": {
      "CUSTOM_API_KEY": "${CUSTOM_KEY:-}"
    }
  }
}
```

## Security Considerations

- API key authentication required for all endpoints
- MCP servers run in isolated containers
- File system access limited to `/tmp` directory
- Network access restricted to KeikenV services
- Environment variables for sensitive credentials

## Troubleshooting

### Common Issues
1. **503 Service Unavailable**: MCP server not responding
   - Check MCP server logs
   - Verify command/URL configuration

2. **401 Unauthorized**: API key issues
   - Verify `MCPO_API_KEY` environment variable
   - Check request headers

3. **Tool Not Found**: Configuration problems
   - Validate `mcpo.json` syntax
   - Restart MCPO service

### Debug Commands
```bash
# Test MCP server directly
uvx mcp-server-time --local-timezone=America/New_York

# Validate MCPO config
docker exec mcpo cat /app/config/mcpo.json

# Check MCPO environment
docker exec mcpo env | grep MCPO
```

## Integration Benefits

1. **Unified API Surface**: All MCP tools accessible via standard HTTP
2. **OpenAPI Compatibility**: Works with any OpenAPI client/framework
3. **Agent Interoperability**: Seamless tool sharing between agents
4. **Documentation**: Auto-generated docs for all capabilities
5. **Security**: Centralized authentication and access control
6. **Monitoring**: Health checks and logging integration

MCPO transforms KeikenV from a multi-agent platform into a comprehensive AI ecosystem with standardized tool access across all agents and services.