const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3100;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Service definitions with health check endpoints
const services = [
    // Core Infrastructure
    {
        name: 'OpenWebUI',
        category: 'Core Infrastructure',
        url: 'http://open-webui:8080',
        healthEndpoint: 'http://open-webui:8080',
        externalUrl: 'https://openwebui.nebarisoftware.com',
        description: 'AI Chat Interface'
    },
    {
        name: 'n8n',
        category: 'Core Infrastructure',
        url: 'http://n8n:5678',
        healthEndpoint: 'http://n8n:5678',
        externalUrl: 'https://n8n.nebarisoftware.com',
        description: 'Workflow Automation'
    },
    {
        name: 'Ollama',
        category: 'Core Infrastructure',
        url: 'http://ollama:11434',
        healthEndpoint: 'http://ollama:11434',
        externalUrl: 'https://ollama.nebarisoftware.com',
        description: 'Local LLM Server'
    },
    {
        name: 'Qdrant',
        category: 'Core Infrastructure',
        url: 'http://qdrant:6333',
        healthEndpoint: 'http://qdrant:6333',
        externalUrl: null,
        description: 'Vector Database'
    },
    {
        name: 'Redis',
        category: 'Core Infrastructure',
        url: 'redis://redis:6379',
        healthEndpoint: null, // Redis doesn't use HTTP - use container health
        externalUrl: null,
        description: 'Cache & Memory Store'
    },
    {
        name: 'PostgreSQL',
        category: 'Core Infrastructure',
        url: 'postgres://postgres:5432',
        healthEndpoint: null, // Will check via container health
        externalUrl: null,
        description: 'Primary Database'
    },
    {
        name: 'Flowise',
        category: 'Core Infrastructure',
        url: 'http://flowise:3001',
        healthEndpoint: 'http://flowise:3001',
        externalUrl: 'https://flowise.nebarisoftware.com',
        description: 'AI Workflow Builder'
    },

    // AI Services
    {
        name: 'PresEnton',
        category: 'AI Services',
        url: 'http://presenton:3000',
        healthEndpoint: 'http://presenton:3000',
        externalUrl: 'https://presenton.nebarisoftware.com',
        description: 'AI Presentation Generator'
    },
    {
        name: 'MLflow',
        category: 'AI Services',
        url: 'http://mlflow-server:5000',
        healthEndpoint: 'http://mlflow-server:5000',
        externalUrl: 'https://mlflow.nebarisoftware.com',
        description: 'ML Experiment Tracking'
    },
    {
        name: 'LiteLLM',
        category: 'AI Services',
        url: 'http://litellm:4000',
        healthEndpoint: 'http://litellm:4000',
        externalUrl: 'http://localhost:8010',
        description: 'Universal LLM API Proxy'
    },
    {
        name: 'ComfyUI',
        category: 'AI Services',
        url: 'http://comfyui:8188',
        healthEndpoint: 'http://comfyui:8188',
        externalUrl: 'https://comfyui.nebarisoftware.com',
        description: 'Node-based AI Workflows'
    },
    {
        name: 'Automatic1111',
        category: 'AI Services',
        url: 'http://automatic1111:7860',
        healthEndpoint: 'http://automatic1111:7860',
        externalUrl: 'https://automatic1111.nebarisoftware.com',
        description: 'Stable Diffusion WebUI'
    },
    {
        name: 'InvokeAI',
        category: 'AI Services',
        url: 'http://invokeai:9090',
        healthEndpoint: 'http://invokeai:9090',
        externalUrl: 'https://invokeai.nebarisoftware.com',
        description: 'AI Image Generation'
    },
    {
        name: 'Mem0',
        category: 'AI Services',
        url: 'http://mem0-server:8000',
        healthEndpoint: 'http://mem0-server:8000',
        externalUrl: 'https://mem0.nebarisoftware.com',
        description: 'AI Memory Layer'
    },
    {
        name: 'Perplexica',
        category: 'AI Services',
        url: 'http://perplexica:3000',
        healthEndpoint: 'http://perplexica:3000',
        externalUrl: 'https://perplexica.nebarisoftware.com',
        description: 'AI-Powered Search Engine'
    },
    {
        name: 'Keiken Teams API',
        category: 'AI Services',
        url: 'http://keiken-teams-api:8000',
        healthEndpoint: 'http://keiken-teams-api:8000',
        externalUrl: 'https://api.keikendemo.nebarisoftware.com',
        description: 'Multi-Agent Teams API'
    },
    {
        name: 'Keiken Main UI',
        category: 'AI Services',
        url: 'http://keiken-main-ui:8501',
        healthEndpoint: 'http://keiken-main-ui:8501',
        externalUrl: 'https://keikendemo.nebarisoftware.com',
        description: 'Main Keiken Interface'
    },
    {
        name: 'Keiken UI Interface',
        category: 'AI Services',
        url: 'http://keiken-ui-interface:8082',
        healthEndpoint: 'http://keiken-ui-interface:8082',
        externalUrl: 'https://ui.keikendemo.nebarisoftware.com',
        description: 'Collaborative Multi-Agent UI'
    },
    {
        name: 'Keiken Code Interface',
        category: 'AI Services',
        url: 'http://keiken-code-interface:8501',
        healthEndpoint: 'http://keiken-code-interface:8501',
        externalUrl: 'https://code.keikendemo.nebarisoftware.com',
        description: 'Codebase Analysis Interface'
    },
    {
        name: 'Keiken Chat Interface',
        category: 'AI Services',
        url: 'http://keiken-chat-interface:8503',
        healthEndpoint: 'http://keiken-chat-interface:8503',
        externalUrl: 'https://chat.keikendemo.nebarisoftware.com',
        description: 'Single-Agent Chat Interface'
    },
    {
        name: 'OpenMemory MCP',
        category: 'AI Services',
        url: 'http://openmemory-mcp:8000',
        healthEndpoint: 'http://openmemory-mcp:8000',
        externalUrl: 'https://openmemory.nebarisoftware.com',
        description: 'Memory Context Protocol'
    },
    {
        name: 'Pinokio',
        category: 'AI Services',
        url: 'http://pinokio:8900',
        healthEndpoint: 'http://pinokio:8900',
        externalUrl: 'https://pinokio.nebarisoftware.com',
        description: 'AI App Launcher'
    },
    {
        name: 'MCPO',
        category: 'AI Services',
        url: 'http://mcpo:8000',
        healthEndpoint: 'http://mcpo:8000/health',
        externalUrl: 'http://localhost:8940',
        description: 'MCP-to-OpenAPI Proxy'
    },

    // Supporting Services
    {
        name: 'Searxng',
        category: 'Supporting Services',
        url: 'http://searxng:8080',
        healthEndpoint: 'http://searxng:8080',
        externalUrl: 'https://searxng.nebarisoftware.com',
        description: 'Privacy Search Engine'
    },
    {
        name: 'ClickHouse',
        category: 'Supporting Services',
        url: 'http://clickhouse:8123',
        healthEndpoint: 'http://clickhouse:8123/ping',
        externalUrl: null,
        description: 'Analytics Database'
    },
    {
        name: 'MinIO',
        category: 'Supporting Services',
        url: 'http://minio:9000',
        healthEndpoint: 'http://minio:9000/minio/health/live',
        externalUrl: null,
        description: 'Object Storage'
    },
    {
        name: 'Langfuse Web',
        category: 'Supporting Services',
        url: 'http://langfuse-web:3000',
        healthEndpoint: 'http://langfuse-web:3000',
        externalUrl: 'https://langfuse.nebarisoftware.com',
        description: 'LLM Observability'
    },
    {
        name: 'Supabase Analytics',
        category: 'Supporting Services',
        url: 'http://supabase-analytics:4000',
        healthEndpoint: 'http://supabase-analytics:4000',
        externalUrl: 'https://supabase.nebarisoftware.com',
        description: 'Database Analytics'
    },
    {
        name: 'Neo4j',
        category: 'Supporting Services',
        url: 'http://neo4j:7474',
        healthEndpoint: 'http://neo4j:7474',
        externalUrl: 'https://neo4j.nebarisoftware.com',
        description: 'Graph Database'
    },
    {
        name: 'Caddy',
        category: 'Supporting Services',
        url: 'http://caddy:80',
        healthEndpoint: 'http://caddy:80',
        externalUrl: 'http://localhost:80',
        description: 'Reverse Proxy'
    }
];

// Check service health
async function checkServiceHealth(service) {
    try {
        if (!service.healthEndpoint) {
            // For services without HTTP endpoints (like Redis), assume healthy if no explicit error
            return { status: 'healthy', responseTime: 0, error: 'No HTTP endpoint - assumed healthy', statusCode: 'N/A' };
        }

        const startTime = Date.now();
        const response = await axios.get(service.healthEndpoint, {
            timeout: 5000,
            maxRedirects: 0, // Don't follow redirects to avoid SSL issues
            validateStatus: function (status) {
                return status < 500; // Accept any status code below 500 as successful
            }
        });
        const responseTime = Date.now() - startTime;

        return {
            status: 'healthy',
            statusCode: response.status,
            responseTime: responseTime,
            error: null
        };
    } catch (error) {
        return {
            status: 'unhealthy',
            statusCode: error.response?.status || 0,
            responseTime: 0,
            error: error.message
        };
    }
}

// Check MCP server health (for HTTP/SSE types)
async function checkMcpServerHealth(serverName, serverConfig) {
    try {
        // Only check health for HTTP/SSE servers
        if (serverConfig.type === 'streamable-http' || serverConfig.type === 'sse') {
            const startTime = Date.now();
            const response = await axios.get(serverConfig.url, {
                timeout: 3000,
                headers: serverConfig.headers || {},
                validateStatus: function (status) {
                    return status < 500;
                }
            });
            const responseTime = Date.now() - startTime;

            return {
                name: serverName,
                status: 'healthy',
                statusCode: response.status,
                responseTime: responseTime,
                error: null,
                type: 'mcp-server',
                category: 'MCP Servers',
                url: serverConfig.url,
                description: serverConfig.description || `MCP Server: ${serverName}`,
                lastChecked: new Date().toISOString()
            };
        } else {
            // For stdio servers, assume healthy if configured
            return {
                name: serverName,
                status: 'healthy',
                statusCode: 'N/A',
                responseTime: 0,
                error: 'STDIO server - health assumed',
                type: 'mcp-server',
                category: 'MCP Servers',
                url: null,
                description: serverConfig.description || `MCP Server: ${serverName}`,
                lastChecked: new Date().toISOString()
            };
        }
    } catch (error) {
        return {
            name: serverName,
            status: 'unhealthy',
            statusCode: error.response?.status || 0,
            responseTime: 0,
            error: error.message,
            type: 'mcp-server',
            category: 'MCP Servers',
            url: serverConfig.url || null,
            description: serverConfig.description || `MCP Server: ${serverName}`,
            lastChecked: new Date().toISOString()
        };
    }
}

// Get MCP servers from MCPO configuration
async function getMcpServers() {
    try {
        const configPath = findMcpoConfigPath();
        if (!fs.existsSync(configPath)) {
            return [];
        }

        const configContent = fs.readFileSync(configPath, 'utf8');
        const config = JSON.parse(configContent);

        if (!config.mcpServers) {
            return [];
        }

        // Check health for each MCP server
        const mcpPromises = Object.entries(config.mcpServers).map(async ([name, serverConfig]) => {
            return await checkMcpServerHealth(name, serverConfig);
        });

        return await Promise.all(mcpPromises);
    } catch (error) {
        console.error('Failed to get MCP servers:', error.message);
        return [];
    }
}

// Get overall system status
async function getSystemStatus() {
    const startTime = Date.now();

    // Check regular services
    const servicePromises = services.map(async (service) => {
        const health = await checkServiceHealth(service);
        return {
            ...service,
            ...health,
            lastChecked: new Date().toISOString()
        };
    });

    // Check MCP servers
    const mcpServersPromise = getMcpServers();

    const [serviceStatuses, mcpServers] = await Promise.all([
        Promise.all(servicePromises),
        mcpServersPromise
    ]);

    // Combine all services
    const allServices = [...serviceStatuses, ...mcpServers];
    const totalTime = Date.now() - startTime;

    const healthy = allServices.filter(s => s.status === 'healthy').length;
    const unhealthy = allServices.filter(s => s.status === 'unhealthy').length;
    const unknown = allServices.filter(s => s.status === 'unknown').length;

    const overallStatus = unhealthy === 0 ? 'healthy' : unhealthy < allServices.length / 2 ? 'degraded' : 'unhealthy';

    return {
        overall: {
            status: overallStatus,
            healthy: healthy,
            unhealthy: unhealthy,
            unknown: unknown,
            total: allServices.length,
            regularServices: serviceStatuses.length,
            mcpServers: mcpServers.length,
            checkDuration: totalTime,
            lastUpdated: new Date().toISOString()
        },
        services: serviceStatuses,
        mcpServers: mcpServers,
        allServices: allServices,
        categories: groupServicesByCategory(allServices)
    };
}

function groupServicesByCategory(serviceStatuses) {
    const categories = {};
    serviceStatuses.forEach(service => {
        if (!categories[service.category]) {
            categories[service.category] = [];
        }
        categories[service.category].push(service);
    });
    return categories;
}

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/api/status', async (req, res) => {
    try {
        const status = await getSystemStatus();
        res.json(status);
    } catch (error) {
        res.status(500).json({ error: 'Failed to check system status', message: error.message });
    }
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'KeikenV Status Dashboard',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Service management endpoints
app.post('/api/services/:action', async (req, res) => {
    const { action } = req.params;
    const { services: targetServices } = req.body;

    // Security check - only allow specific actions
    const allowedActions = ['start', 'stop', 'restart'];
    if (!allowedActions.includes(action)) {
        return res.status(400).json({ error: 'Invalid action' });
    }

    try {
        const { spawn } = require('child_process');
        let command, args;

        if (targetServices && Array.isArray(targetServices)) {
            // Specific services
            command = 'docker-compose';
            args = ['--profile', 'gpu-nvidia', action, ...targetServices];
        } else {
            // All services
            switch (action) {
                case 'start':
                    command = 'docker-compose';
                    args = ['--profile', 'gpu-nvidia', 'up', '-d'];
                    break;
                case 'stop':
                    command = 'docker-compose';
                    args = ['--profile', 'gpu-nvidia', 'down'];
                    break;
                case 'restart':
                    command = 'docker-compose';
                    args = ['--profile', 'gpu-nvidia', 'restart'];
                    break;
            }
        }

        const process = spawn(command, args, {
            cwd: '/host-docker-compose',
            stdio: 'pipe'
        });

        let output = '';
        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        process.stderr.on('data', (data) => {
            output += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                res.json({
                    success: true,
                    message: `Successfully executed ${action}`,
                    output: output
                });
            } else {
                res.status(500).json({
                    success: false,
                    message: `Failed to ${action} services`,
                    output: output
                });
            }
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// Individual service management
app.post('/api/service/:serviceName/:action', async (req, res) => {
    const { serviceName, action } = req.params;

    // Security check
    const allowedActions = ['start', 'stop', 'restart'];
    if (!allowedActions.includes(action)) {
        return res.status(400).json({ error: 'Invalid action' });
    }

    // Find service in our list to validate it exists
    const service = services.find(s => s.name.toLowerCase().replace(/\s+/g, '-') === serviceName);
    if (!service) {
        return res.status(404).json({ error: 'Service not found' });
    }

    try {
        const { spawn } = require('child_process');

        // Get the container name from the service URL
        const containerName = service.url.split('://')[1].split(':')[0];

        const process = spawn('docker', [action, containerName], {
            stdio: 'pipe'
        });

        let output = '';
        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        process.stderr.on('data', (data) => {
            output += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                res.json({
                    success: true,
                    message: `Successfully ${action}ed ${service.name}`,
                    output: output
                });
            } else {
                res.status(500).json({
                    success: false,
                    message: `Failed to ${action} ${service.name}`,
                    output: output
                });
            }
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// MCP Configuration Management
const fs = require('fs');
// Candidate locations where mcpo.json might be mounted inside the container.
// Compose mounts may vary; check multiple sensible paths and pick the first that exists.
const mcpoConfigCandidates = [
    '/app/mcpo-config/mcpo.json', // explicit mount used by docker-compose for status-dashboard
    '/app/config/mcpo.json',      // same location mcpo container uses
    '/mcpo/mcpo.json',            // fallback common mount
    // as a last resort, look for a mcpo directory next to the app code
    require('path').join(__dirname, '..', 'mcpo', 'mcpo.json')
];

function findMcpoConfigPath() {
    for (const p of mcpoConfigCandidates) {
        try {
            if (fs.existsSync(p)) return p;
        } catch (e) {
            // ignore permission errors here and continue
        }
    }
    // If none exist, return the primary candidate where we'll create the file when needed
    return mcpoConfigCandidates[0];
}

function ensureMcpoConfigDirExists(configPath) {
    try {
        const dir = require('path').dirname(configPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    } catch (e) {
        // ignore here; callers will handle errors
    }
}

// Get current MCPO configuration
app.get('/api/mcpo/config', (req, res) => {
    try {
        const configPath = findMcpoConfigPath();
        if (fs.existsSync(configPath)) {
            const configContent = fs.readFileSync(configPath, 'utf8');
            const config = JSON.parse(configContent);
            res.json(config);
        } else {
            res.status(404).json({ error: 'MCPO configuration file not found', pathTried: configPath });
        }
    } catch (error) {
        res.status(500).json({ error: 'Failed to read MCPO configuration', message: error.message });
    }
});

// Add new MCP server to configuration
app.post('/api/mcpo/servers', (req, res) => {
    try {
        const { serverName, serverConfig } = req.body;

        // Validate input
        if (!serverName || !serverConfig) {
            return res.status(400).json({ error: 'Server name and configuration are required' });
        }

        // Validate server name (alphanumeric, hyphens, underscores only)
        if (!/^[a-zA-Z0-9_-]+$/.test(serverName)) {
            return res.status(400).json({ error: 'Server name must contain only letters, numbers, hyphens, and underscores' });
        }

        // Read current configuration (look for mcpo.json in common locations)
        const configPath = findMcpoConfigPath();
        let config = { mcpServers: {} };
        if (fs.existsSync(configPath)) {
            const configContent = fs.readFileSync(configPath, 'utf8');
            config = JSON.parse(configContent);
        }

        // Check if server already exists
        if (config.mcpServers && config.mcpServers[serverName]) {
            return res.status(409).json({ error: `Server "${serverName}" already exists` });
        }

        // Add new server
        if (!config.mcpServers) {
            config.mcpServers = {};
        }
        config.mcpServers[serverName] = serverConfig;

        // Write updated configuration. Ensure directory exists for primary candidate when creating new file.
        ensureMcpoConfigDirExists(configPath);
        const updatedConfig = JSON.stringify(config, null, 2);
        fs.writeFileSync(configPath, updatedConfig, 'utf8');

        res.json({
            success: true,
            message: `MCP server "${serverName}" added successfully`,
            config: config
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to add MCP server',
            message: error.message
        });
    }
});

// Remove MCP server from configuration
app.delete('/api/mcpo/servers/:serverName', (req, res) => {
    try {
        const { serverName } = req.params;

        // Read current configuration from available locations
        const configPath = findMcpoConfigPath();
        if (!fs.existsSync(configPath)) {
            return res.status(404).json({ error: 'MCPO configuration file not found', pathTried: configPath });
        }

        const configContent = fs.readFileSync(configPath, 'utf8');
        const config = JSON.parse(configContent);

        // Check if server exists
        if (!config.mcpServers || !config.mcpServers[serverName]) {
            return res.status(404).json({ error: `Server "${serverName}" not found` });
        }

        // Remove server
        delete config.mcpServers[serverName];

        // Write updated configuration
        const updatedConfig = JSON.stringify(config, null, 2);
        fs.writeFileSync(configPath, updatedConfig, 'utf8');

        res.json({
            success: true,
            message: `MCP server "${serverName}" removed successfully`,
            config: config
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to remove MCP server',
            message: error.message
        });
    }
});

// Get available MCP server templates/presets
app.get('/api/mcpo/templates', (req, res) => {
    const templates = {
        'stdio': {
            name: 'Standard I/O Server',
            description: 'MCP server that communicates via standard input/output',
            config: {
                command: 'npx',
                args: ['-y', '@modelcontextprotocol/server-example'],
                description: 'Example MCP server description'
            }
        },
        'http': {
            name: 'HTTP Server',
            description: 'MCP server accessible via HTTP endpoints',
            config: {
                type: 'streamable-http',
                url: 'http://localhost:8080/mcp',
                description: 'HTTP-based MCP server',
                headers: {
                    'Authorization': 'Bearer your-api-key',
                    'Content-Type': 'application/json'
                }
            }
        },
        'sse': {
            name: 'Server-Sent Events',
            description: 'MCP server using Server-Sent Events for communication',
            config: {
                type: 'sse',
                url: 'http://localhost:8080/sse',
                description: 'SSE-based MCP server',
                headers: {
                    'Authorization': 'Bearer your-api-key'
                }
            }
        }
    };

    res.json(templates);
});

// Get MCP servers with health status
app.get('/api/mcpo/servers', async (req, res) => {
    try {
        const mcpServers = await getMcpServers();
        res.json({
            success: true,
            servers: mcpServers,
            count: mcpServers.length
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to get MCP servers',
            message: error.message
        });
    }
});

// Periodic status updates (every 30 seconds)
let cachedStatus = null;
async function updateStatusCache() {
    try {
        cachedStatus = await getSystemStatus();
        console.log(`[${new Date().toISOString()}] Status updated: ${cachedStatus.overall.healthy}/${cachedStatus.overall.total} services healthy`);
    } catch (error) {
        console.error('Failed to update status cache:', error.message);
    }
}

// Initial status check
updateStatusCache();
setInterval(updateStatusCache, 30000);

// Get cached status (faster response)
app.get('/api/status/cached', (req, res) => {
    if (cachedStatus) {
        res.json(cachedStatus);
    } else {
        res.status(503).json({ error: 'Status cache not ready' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 KeikenV Status Dashboard running on port ${PORT}`);
    console.log(`📊 Monitoring ${services.length} services across ${[...new Set(services.map(s => s.category))].length} categories`);
});