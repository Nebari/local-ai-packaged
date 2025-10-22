const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const axios = require('axios');
const simpleGit = require('simple-git');
const Docker = require('dockerode');
const { WebSocketServer } = require('ws');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });
const docker = new Docker({ socketPath: '/var/run/docker.sock' });

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Store for running applications
const runningApps = new Map();
const installedApps = new Map();

// WebSocket connection for real-time updates
wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    // Send current app status
    ws.send(JSON.stringify({
        type: 'app_status',
        running: Array.from(runningApps.keys()),
        installed: Array.from(installedApps.keys())
    }));
    
    ws.on('close', () => {
        console.log('WebSocket client disconnected');
    });
});

// Broadcast to all WebSocket clients
function broadcast(message) {
    wss.clients.forEach((client) => {
        if (client.readyState === 1) { // WebSocket.OPEN
            client.send(JSON.stringify(message));
        }
    });
}

// Pinokio Discovery API Configuration
const PINOKIO_API = {
    featured: 'https://pinokiocomputer.github.io/sitefeed/featured.json',
    community: 'https://api.github.com/search/repositories?q=topic:pinokio&sort=updated&direction=desc&per_page=100',
    blacklist: 'https://pinokiocomputer.github.io/sitefeed/blacklist.json'
};

// Cache for discovery data (refresh every 10 minutes)
let discoveryCache = {
    featured: null,
    community: null,
    blacklist: null,
    lastUpdate: 0
};

const CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

// Fetch discovery data from Pinokio's APIs
async function fetchDiscoveryData() {
    const now = Date.now();
    console.log(`fetchDiscoveryData called: lastUpdate=${discoveryCache.lastUpdate}, now=${now}, age=${now - discoveryCache.lastUpdate}ms`);
    
    if (discoveryCache.lastUpdate && (now - discoveryCache.lastUpdate) < CACHE_DURATION) {
        console.log('Using cached discovery data');
        return discoveryCache;
    }

    try {
        console.log('Fetching fresh discovery data from Pinokio APIs...');
        
        // Fetch featured apps
        const featuredResponse = await axios.get(PINOKIO_API.featured);
        discoveryCache.featured = featuredResponse.data;
        console.log(`Fetched ${featuredResponse.data?.length || 0} featured apps`);

        // Fetch community apps
        const communityResponse = await axios.get(PINOKIO_API.community);
        discoveryCache.community = communityResponse.data.items || [];
        console.log(`Fetched ${communityResponse.data.items?.length || 0} community apps`);

        // Fetch blacklist
        try {
            const blacklistResponse = await axios.get(PINOKIO_API.blacklist);
            discoveryCache.blacklist = blacklistResponse.data.accounts || [];
            console.log(`Fetched ${blacklistResponse.data.accounts?.length || 0} blacklisted accounts`);
        } catch (error) {
            console.warn('Failed to fetch blacklist, using empty list:', error.message);
            discoveryCache.blacklist = [];
        }

        discoveryCache.lastUpdate = now;
        console.log(`Discovery complete: ${discoveryCache.featured?.length || 0} featured, ${discoveryCache.community?.length || 0} community apps`);
        
        return discoveryCache;
    } catch (error) {
        console.error('Error fetching discovery data:', error.message);
        console.log('Returning existing cache or empty data');
        return discoveryCache;
    }
}

// Transform Pinokio app data to our format
function transformPinokioApp(item, type = 'community') {
    const getImageFromGitHub = (url) => {
        if (!url) return 'https://github.com/github.png';
        
        const match = url.match(/github\.com\/([^\/]+)/);
        if (match) {
            return `https://github.com/${match[1]}.png`;
        }
        return 'https://github.com/github.png';
    };

    const getDockerImage = (name) => {
        // Map common AI apps to Docker images
        const dockerMappings = {
            'stable-diffusion-webui': 'ghcr.io/automatic1111/stable-diffusion-webui:latest',
            'comfyui': 'yanwk/comfyui-boot:latest', 
            'text-generation-webui': 'ghcr.io/oobabooga/text-generation-webui:latest',
            'ollama': 'ollama/ollama:latest',
            'whisper': 'onerahmet/openai-whisper-asr-webservice:latest',
            'jupyter': 'jupyter/ai-notebook:latest'
        };

        const lowerName = name.toLowerCase();
        for (const [key, image] of Object.entries(dockerMappings)) {
            if (lowerName.includes(key)) {
                return image;
            }
        }
        
        // Default to a generic Python environment for unknown apps
        return 'python:3.11-slim';
    };

    if (type === 'featured') {
        return {
            id: item.title?.toLowerCase().replace(/[^a-z0-9]/g, '-') || 'unknown',
            name: item.title || 'Unknown App',
            description: item.description || 'No description available',
            category: 'AI Application',
            image: getDockerImage(item.title || ''),
            repository: item.download || item.url,
            githubImage: item.image || getImageFromGitHub(item.download),
            ports: { "8080": "8080" }, // Default port
            env: {},
            volumes: {}
        };
    } else {
        return {
            id: item.name?.toLowerCase().replace(/[^a-z0-9]/g, '-') || 'unknown',
            name: item.name || 'Unknown App',
            description: item.description || 'No description available',
            category: 'Community',
            image: getDockerImage(item.name || ''),
            repository: item.html_url,
            githubImage: item.owner?.avatar_url || getImageFromGitHub(item.html_url),
            ports: { "8080": "8080" }, // Default port
            env: {},
            volumes: {}
        };
    }
}

// Fallback static apps for when discovery fails
const FALLBACK_APPS = {
    "stable-diffusion-webui": {
        name: "Stable Diffusion WebUI",
        description: "Advanced AI image generation with Stable Diffusion",
        category: "Image Generation",
        image: "ghcr.io/automatic1111/stable-diffusion-webui:latest",
        ports: { "7860": "7860" },
        env: {
            "COMMANDLINE_ARGS": "--listen --port 7860 --allow-code --medvram --xformers --enable-insecure-extension-access"
        },
        volumes: {
            "/app/data/stable-diffusion": "/app/data"
        }
    },
    "comfyui": {
        name: "ComfyUI",
        description: "Node-based Stable Diffusion GUI",
        category: "Image Generation", 
        image: "yanwk/comfyui-boot:latest",
        ports: { "8188": "8188" },
        env: {
            "CLI_ARGS": "--listen --port 8188"
        },
        volumes: {
            "/app/data/comfyui": "/app/ComfyUI"
        }
    },
    "text-generation-webui": {
        name: "Text Generation WebUI",
        description: "Advanced web UI for running large language models",
        category: "Text Generation",
        image: "ghcr.io/oobabooga/text-generation-webui:latest",
        ports: { "7860": "7860" },
        env: {
            "EXTRA_LAUNCH_ARGS": "--listen --listen-port 7860 --api"
        },
        volumes: {
            "/app/data/text-generation": "/app/text-generation-webui"
        }
    },
    "ollama": {
        name: "Ollama",
        description: "Run large language models locally",
        category: "Language Models",
        image: "ollama/ollama:latest",
        ports: { "11434": "11434" },
        volumes: {
            "/app/data/ollama": "/root/.ollama"
        }
    },
    "whisper": {
        name: "Whisper ASR",
        description: "OpenAI Whisper automatic speech recognition",
        category: "Audio",
        image: "onerahmet/openai-whisper-asr-webservice:latest",
        ports: { "9000": "9000" },
        env: {
            "ASR_MODEL": "base"
        }
    },
    "jupyter-ai": {
        name: "Jupyter AI Lab",
        description: "Jupyter notebook with AI extensions",
        category: "Development",
        image: "jupyter/ai-notebook:latest",
        ports: { "8888": "8888" },
        volumes: {
            "/app/data/jupyter": "/home/jovyan/work"
        }
    }
};

// API Routes

// Get available apps
app.get('/api/apps', async (req, res) => {
    try {
        const discoveryData = await fetchDiscoveryData();
        const apps = [];

        // Add featured apps
        if (discoveryData.featured && Array.isArray(discoveryData.featured)) {
            discoveryData.featured.forEach(item => {
                const app = transformPinokioApp(item, 'featured');
                apps.push({
                    ...app,
                    type: 'featured',
                    installed: installedApps.has(app.id),
                    running: runningApps.has(app.id)
                });
            });
        }

        // Add community apps (filtered by blacklist)
        if (discoveryData.community && Array.isArray(discoveryData.community)) {
            const blacklist = discoveryData.blacklist || [];
            const filteredCommunity = discoveryData.community.filter(item => {
                const ownerName = item.owner?.login?.toLowerCase();
                return ownerName && !blacklist.map(a => a.toLowerCase()).includes(ownerName);
            });

            filteredCommunity.slice(0, 50).forEach(item => { // Limit to 50 community apps
                const app = transformPinokioApp(item, 'community');
                apps.push({
                    ...app,
                    type: 'community',
                    installed: installedApps.has(app.id),
                    running: runningApps.has(app.id)
                });
            });
        }

        // Add fallback apps if no discovery data
        if (apps.length === 0) {
            const fallbackApps = Object.entries(FALLBACK_APPS).map(([id, app]) => ({
                id,
                ...app,
                type: 'fallback',
                installed: installedApps.has(id),
                running: runningApps.has(id)
            }));
            apps.push(...fallbackApps);
        }
        
        res.json(apps);
    } catch (error) {
        console.error('Error in /api/apps:', error);
        res.status(500).json({ error: error.message });
    }
});

// Install an app
app.post('/api/apps/:id/install', async (req, res) => {
    const { id } = req.params;
    
    try {
        // Find the app in discovery data or fallback
        const discoveryData = await fetchDiscoveryData();
        let app = null;

        // Check featured apps
        if (discoveryData.featured) {
            const featuredApp = discoveryData.featured.find(item => 
                transformPinokioApp(item, 'featured').id === id
            );
            if (featuredApp) {
                app = transformPinokioApp(featuredApp, 'featured');
            }
        }

        // Check community apps if not found in featured
        if (!app && discoveryData.community) {
            const communityApp = discoveryData.community.find(item => 
                transformPinokioApp(item, 'community').id === id
            );
            if (communityApp) {
                app = transformPinokioApp(communityApp, 'community');
            }
        }

        // Check fallback apps if not found in discovery
        if (!app && FALLBACK_APPS[id]) {
            app = FALLBACK_APPS[id];
        }

        if (!app) {
            return res.status(404).json({ error: 'App not found' });
        }
        
        broadcast({
            type: 'install_progress',
            app: id,
            status: 'pulling_image',
            message: `Pulling Docker image: ${app.image}`
        });
        
        // Pull the Docker image
        await new Promise((resolve, reject) => {
            docker.pull(app.image, (err, stream) => {
                if (err) return reject(err);
                
                docker.modem.followProgress(stream, (err, res) => {
                    if (err) return reject(err);
                    resolve(res);
                });
            });
        });
        
        // Create data directory
        const dataDir = path.join('/app/data', id);
        await fs.mkdir(dataDir, { recursive: true });
        
        // Mark as installed
        installedApps.set(id, {
            ...app,
            installedAt: new Date().toISOString(),
            dataDir
        });
        
        broadcast({
            type: 'install_complete',
            app: id,
            message: `${app.name} installed successfully`
        });
        
        res.json({ success: true, message: `${app.name} installed successfully` });
        
    } catch (error) {
        console.error(`Error installing app ${id}:`, error);
        broadcast({
            type: 'install_error',
            app: id,
            error: error.message
        });
        res.status(500).json({ error: error.message });
    }
});

// Start an app
app.post('/api/apps/:id/start', async (req, res) => {
    const { id } = req.params;
    
    try {
        // Find the app in discovery data or fallback
        const discoveryData = await fetchDiscoveryData();
        let app = null;

        // Check featured apps
        if (discoveryData.featured) {
            const featuredApp = discoveryData.featured.find(item => 
                transformPinokioApp(item, 'featured').id === id
            );
            if (featuredApp) {
                app = transformPinokioApp(featuredApp, 'featured');
            }
        }

        // Check community apps if not found in featured
        if (!app && discoveryData.community) {
            const communityApp = discoveryData.community.find(item => 
                transformPinokioApp(item, 'community').id === id
            );
            if (communityApp) {
                app = transformPinokioApp(communityApp, 'community');
            }
        }

        // Check fallback apps if not found in discovery
        if (!app && FALLBACK_APPS[id]) {
            app = FALLBACK_APPS[id];
        }

        if (!app) {
            return res.status(404).json({ error: 'App not found' });
        }
        
        if (runningApps.has(id)) {
            return res.status(400).json({ error: 'App is already running' });
        }
        const installedApp = installedApps.get(id);
        
        broadcast({
            type: 'start_progress',
            app: id,
            status: 'starting',
            message: `Starting ${app.name}...`
        });
        
        // Create container configuration
        const containerConfig = {
            Image: app.image,
            name: `pinokio-${id}`,
            HostConfig: {
                PortBindings: {},
                Binds: []
            },
            Env: Object.entries(app.env || {}).map(([key, value]) => `${key}=${value}`)
        };
        
        // Configure port bindings
        if (app.ports) {
            for (const [hostPort, containerPort] of Object.entries(app.ports)) {
                containerConfig.ExposedPorts = containerConfig.ExposedPorts || {};
                containerConfig.ExposedPorts[`${containerPort}/tcp`] = {};
                containerConfig.HostConfig.PortBindings[`${containerPort}/tcp`] = [{ HostPort: hostPort }];
            }
        }
        
        // Configure volumes
        if (app.volumes) {
            for (const [hostPath, containerPath] of Object.entries(app.volumes)) {
                const fullHostPath = hostPath.startsWith('/app/data') ? hostPath : path.join('/app/data', id, hostPath);
                await fs.mkdir(fullHostPath, { recursive: true });
                containerConfig.HostConfig.Binds.push(`${fullHostPath}:${containerPath}`);
            }
        }
        
        // Create and start container
        const container = await docker.createContainer(containerConfig);
        await container.start();
        
        // Store running app info
        runningApps.set(id, {
            container: container,
            startedAt: new Date().toISOString(),
            ports: app.ports,
            ...app
        });
        
        broadcast({
            type: 'start_complete',
            app: id,
            ports: app.ports,
            message: `${app.name} started successfully`
        });
        
        res.json({ 
            success: true, 
            message: `${app.name} started successfully`,
            ports: app.ports 
        });
        
    } catch (error) {
        console.error(`Error starting app ${id}:`, error);
        broadcast({
            type: 'start_error',
            app: id,
            error: error.message
        });
        res.status(500).json({ error: error.message });
    }
});

// Stop an app
app.post('/api/apps/:id/stop', async (req, res) => {
    const { id } = req.params;
    
    try {
        if (!runningApps.has(id)) {
            return res.status(404).json({ error: 'App not running' });
        }
        
        const runningApp = runningApps.get(id);
        
        broadcast({
            type: 'stop_progress',
            app: id,
            status: 'stopping',
            message: `Stopping ${runningApp.name}...`
        });
        
        // Stop and remove container
        await runningApp.container.stop();
        await runningApp.container.remove();
        
        // Remove from running apps
        runningApps.delete(id);
        
        broadcast({
            type: 'stop_complete',
            app: id,
            message: `${runningApp.name} stopped successfully`
        });
        
        res.json({ success: true, message: `${runningApp.name} stopped successfully` });
        
    } catch (error) {
        console.error(`Error stopping app ${id}:`, error);
        broadcast({
            type: 'stop_error',
            app: id,
            error: error.message
        });
        res.status(500).json({ error: error.message });
    }
});

// Get app logs
app.get('/api/apps/:id/logs', async (req, res) => {
    const { id } = req.params;
    
    try {
        if (!runningApps.has(id)) {
            return res.status(404).json({ error: 'App not running' });
        }
        
        const runningApp = runningApps.get(id);
        const logs = await runningApp.container.logs({
            stdout: true,
            stderr: true,
            tail: 100
        });
        
        res.json({ logs: logs.toString() });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get system status
app.get('/api/status', async (req, res) => {
    try {
        const dockerInfo = await docker.info();
        
        res.json({
            docker: {
                containers: dockerInfo.Containers,
                containersRunning: dockerInfo.ContainersRunning,
                images: dockerInfo.Images
            },
            apps: {
                installed: installedApps.size,
                running: runningApps.size
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve the main UI
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Cleanup function
async function cleanup() {
    console.log('Shutting down Pinokio Web...');
    
    // Stop all running containers
    for (const [id, runningApp] of runningApps) {
        try {
            console.log(`Stopping ${runningApp.name}...`);
            await runningApp.container.stop();
            await runningApp.container.remove();
        } catch (error) {
            console.error(`Error stopping ${runningApp.name}:`, error);
        }
    }
    
    process.exit(0);
}

// Handle shutdown gracefully
process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);

// Start server
const PORT = process.env.PORT || 8900;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Pinokio Web Interface running on port ${PORT}`);
    console.log(`Access the UI at: http://localhost:${PORT}`);
});