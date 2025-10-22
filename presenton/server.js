const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Storage configuration for file uploads
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const uploadDir = '/app/data/uploads';
        try {
            await fs.mkdir(uploadDir, { recursive: true });
            cb(null, uploadDir);
        } catch (error) {
            cb(error);
        }
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage });

// LiteLLM endpoint configuration
const LITELLM_ENDPOINT = process.env.LITELLM_ENDPOINT || 'http://litellm:4000';

// Generate presentation content using AI
async function generatePresentation(topic, style, slides_count = 8) {
    const prompt = `Create a professional presentation on "${topic}" with exactly ${slides_count} slides.
    Style: ${style}
    
    Format the response as JSON with this structure:
    {
        "title": "Presentation Title",
        "slides": [
            {
                "title": "Slide Title",
                "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
                "notes": "Speaker notes for this slide"
            }
        ]
    }
    
    Make each slide informative but concise. Include practical examples and actionable insights.`;

    try {
        const response = await axios.post(`${LITELLM_ENDPOINT}/v1/chat/completions`, {
            model: "gpt-4",
            messages: [
                {
                    role: "system",
                    content: "You are an expert presentation designer. Create engaging, well-structured presentations with clear, concise content."
                },
                {
                    role: "user",
                    content: prompt
                }
            ],
            temperature: 0.7,
            max_tokens: 2000
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const aiResponse = response.data.choices[0].message.content;

        // Try to parse JSON response
        try {
            return JSON.parse(aiResponse);
        } catch (parseError) {
            // Fallback: extract content manually if JSON parsing fails
            return {
                title: topic,
                slides: [
                    {
                        title: "Introduction",
                        content: ["Welcome to our presentation on " + topic],
                        notes: "AI response parsing failed, showing fallback content"
                    }
                ]
            };
        }
    } catch (error) {
        console.error('AI generation error:', error.message);
        throw new Error('Failed to generate presentation content');
    }
}

// Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'AI Presentation Generator' });
});

// Generate presentation
app.post('/api/generate', async (req, res) => {
    try {
        const { topic, style = 'professional', slides = 8 } = req.body;

        if (!topic) {
            return res.status(400).json({ error: 'Topic is required' });
        }

        console.log(`Generating presentation: "${topic}" (${slides} slides, ${style} style)`);

        const presentation = await generatePresentation(topic, style, parseInt(slides));

        // Save presentation to file
        const presentationId = Date.now().toString();
        const filePath = `/app/data/presentations/${presentationId}.json`;

        await fs.mkdir('/app/data/presentations', { recursive: true });
        await fs.writeFile(filePath, JSON.stringify(presentation, null, 2));

        res.json({
            success: true,
            presentation,
            presentationId
        });

    } catch (error) {
        console.error('Generation error:', error);
        res.status(500).json({
            error: 'Failed to generate presentation',
            details: error.message
        });
    }
});

// Get saved presentation
app.get('/api/presentations/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const filePath = `/app/data/presentations/${id}.json`;

        const data = await fs.readFile(filePath, 'utf8');
        const presentation = JSON.parse(data);

        res.json(presentation);
    } catch (error) {
        res.status(404).json({ error: 'Presentation not found' });
    }
});

// List presentations
app.get('/api/presentations', async (req, res) => {
    try {
        await fs.mkdir('/app/data/presentations', { recursive: true });
        const files = await fs.readdir('/app/data/presentations');
        const presentations = [];

        for (const file of files) {
            if (file.endsWith('.json')) {
                try {
                    const data = await fs.readFile(`/app/data/presentations/${file}`, 'utf8');
                    const presentation = JSON.parse(data);
                    presentations.push({
                        id: file.replace('.json', ''),
                        title: presentation.title,
                        slideCount: presentation.slides?.length || 0,
                        createdAt: file.replace('.json', '')
                    });
                } catch (parseError) {
                    console.error('Error parsing presentation file:', file, parseError);
                }
            }
        }

        res.json(presentations);
    } catch (error) {
        res.status(500).json({ error: 'Failed to list presentations' });
    }
});

// Serve the main HTML page
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PresEnton - AI Presentation Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 2rem;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #555;
        }
        
        input[type="text"], select, textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .presentation-viewer {
            display: none;
            background: white;
            border-radius: 20px;
            padding: 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .slide {
            padding: 3rem;
            min-height: 500px;
            border-bottom: 1px solid #eee;
        }
        
        .slide:last-child {
            border-bottom: none;
        }
        
        .slide h2 {
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 1.5rem;
        }
        
        .slide ul {
            list-style: none;
            padding: 0;
        }
        
        .slide li {
            padding: 0.5rem 0;
            padding-left: 2rem;
            position: relative;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        .slide li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
        
        .slide-notes {
            background: #f8f9fa;
            padding: 1rem 3rem;
            font-style: italic;
            color: #666;
        }
        
        .controls {
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
        }
        
        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c00;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .success {
            background: #efe;
            border: 1px solid #cfc;
            color: #060;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PresEnton</h1>
            <p>AI-Powered Presentation Generator</p>
        </div>
        
        <div id="generator-form" class="main-card">
            <form id="presentation-form">
                <div class="form-group">
                    <label for="topic">Presentation Topic</label>
                    <input type="text" id="topic" name="topic" placeholder="e.g., Machine Learning Fundamentals" required>
                </div>
                
                <div class="form-group">
                    <label for="style">Presentation Style</label>
                    <select id="style" name="style">
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="academic">Academic</option>
                        <option value="creative">Creative</option>
                        <option value="technical">Technical</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="slides">Number of Slides</label>
                    <select id="slides" name="slides">
                        <option value="5">5 slides</option>
                        <option value="8" selected>8 slides</option>
                        <option value="10">10 slides</option>
                        <option value="12">12 slides</option>
                        <option value="15">15 slides</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Generate Presentation</button>
            </form>
        </div>
        
        <div id="loading" class="loading main-card">
            <div class="spinner"></div>
            <p>Creating your presentation with AI...</p>
        </div>
        
        <div id="presentation-viewer" class="presentation-viewer">
            <div id="presentation-content"></div>
            <div class="controls">
                <button class="btn" onclick="downloadPresentation()">📥 Download JSON</button>
                <button class="btn" onclick="showGenerator()">✨ Create New</button>
            </div>
        </div>
        
        <div id="message"></div>
    </div>

    <script>
        let currentPresentation = null;
        
        document.getElementById('presentation-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            showLoading();
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentPresentation = result.presentation;
                    displayPresentation(result.presentation);
                    showMessage('Presentation generated successfully!', 'success');
                } else {
                    throw new Error(result.error || 'Generation failed');
                }
                
            } catch (error) {
                console.error('Generation error:', error);
                showMessage('Failed to generate presentation: ' + error.message, 'error');
                showGenerator();
            }
        });
        
        function showLoading() {
            document.getElementById('generator-form').style.display = 'none';
            document.getElementById('presentation-viewer').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }
        
        function showGenerator() {
            document.getElementById('generator-form').style.display = 'block';
            document.getElementById('presentation-viewer').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
        }
        
        function displayPresentation(presentation) {
            const content = document.getElementById('presentation-content');
            
            let html = '';
            presentation.slides.forEach((slide, index) => {
                html += \`
                    <div class="slide">
                        <h2>\${slide.title}</h2>
                        <ul>
                            \${slide.content.map(point => \`<li>\${point}</li>\`).join('')}
                        </ul>
                    </div>
                    \${slide.notes ? \`<div class="slide-notes">💡 Speaker Notes: \${slide.notes}</div>\` : ''}
                \`;
            });
            
            content.innerHTML = html;
            
            document.getElementById('generator-form').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
            document.getElementById('presentation-viewer').style.display = 'block';
        }
        
        function downloadPresentation() {
            if (!currentPresentation) return;
            
            const dataStr = JSON.stringify(currentPresentation, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = \`\${currentPresentation.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json\`;
            link.click();
        }
        
        function showMessage(message, type) {
            const messageEl = document.getElementById('message');
            messageEl.innerHTML = \`<div class="\${type}">\${message}</div>\`;
            setTimeout(() => {
                messageEl.innerHTML = '';
            }, 5000);
        }
        
        // Check service health on load
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showMessage('AI Presentation service is ready!', 'success');
                }
            })
            .catch(error => {
                showMessage('Service connection error. Please check configuration.', 'error');
            });
    </script>
</body>
</html>
    `);
});

// Start server
app.listen(port, '0.0.0.0', () => {
    console.log(`PresEnton AI Presentation Generator running on port ${port}`);
    console.log('Access the service at: http://localhost:' + port);
});