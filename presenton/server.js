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
const OLLAMA_ENDPOINT = process.env.OLLAMA_ENDPOINT || 'http://ollama:11434';

// Image generation using AI
async function generateSlideImage(slideTitle, slideContent, style = 'professional') {
    try {
        // Create a descriptive prompt for image generation
        const imagePrompt = `Create a ${style} slide background image for a presentation slide titled "${slideTitle}". 
        Content context: ${Array.isArray(slideContent) ? slideContent.join(', ') : slideContent}. 
        Style: clean, modern, ${style}, suitable for business presentation, high quality, 16:9 aspect ratio`;

        // Try to generate image using Ollama's vision capabilities or DALL-E style prompt
        try {
            const ollamaResponse = await axios.post(`${OLLAMA_ENDPOINT}/api/generate`, {
                model: "llama3.2-vision:11b",
                prompt: `Generate an image description for: ${imagePrompt}`,
                stream: false
            }, {
                timeout: 10000
            });

            if (ollamaResponse.data?.response) {
                // For now, return a placeholder URL - in production, this would generate actual images
                return generatePlaceholderImage(slideTitle, style);
            }
        } catch (ollamaError) {
            console.log('Ollama image generation unavailable');
        }

        // Fallback to placeholder image
        return generatePlaceholderImage(slideTitle, style);
    } catch (error) {
        console.error('Image generation error:', error.message);
        return generatePlaceholderImage(slideTitle, style);
    }
}

// Generate placeholder images with different styles
function generatePlaceholderImage(slideTitle, slideContent, style = 'professional') {
    const styleColors = {
        professional: { bg: '#2563eb', text: '#ffffff', accent: '#1d4ed8' },
        casual: { bg: '#10b981', text: '#ffffff', accent: '#059669' },
        academic: { bg: '#7c3aed', text: '#ffffff', accent: '#6d28d9' },
        creative: { bg: '#f59e0b', text: '#ffffff', accent: '#d97706' },
        technical: { bg: '#374151', text: '#ffffff', accent: '#1f2937' }
    };

    const colors = styleColors[style] || styleColors.professional;
    const title = slideTitle.slice(0, 60);

    // Generate concept-specific SVG visualizations
    const conceptSvg = generateConceptVisualization(title, slideContent, colors);

    // Convert SVG to data URL
    const svgBase64 = btoa(unescape(encodeURIComponent(conceptSvg)));
    return `data:image/svg+xml;base64,${svgBase64}`;
}

// Generate concept-specific visualizations based on slide content
function generateConceptVisualization(title, content, colors) {
    const contentText = Array.isArray(content) ? content.join(' ').toLowerCase() : content.toLowerCase();
    const titleLower = title.toLowerCase();

    // Determine visualization type based on content
    if (titleLower.includes('machine learning') || contentText.includes('algorithm') || contentText.includes('model')) {
        return generateMLVisualization(title, colors);
    } else if (titleLower.includes('data') || contentText.includes('database') || contentText.includes('analysis')) {
        return generateDataVisualization(title, colors);
    } else if (titleLower.includes('web') || contentText.includes('frontend') || contentText.includes('backend')) {
        return generateWebDevVisualization(title, colors);
    } else if (titleLower.includes('network') || contentText.includes('server') || contentText.includes('cloud')) {
        return generateNetworkVisualization(title, colors);
    } else if (titleLower.includes('process') || contentText.includes('workflow') || contentText.includes('stage')) {
        return generateProcessVisualization(title, colors);
    } else if (titleLower.includes('security') || contentText.includes('protection') || contentText.includes('encryption')) {
        return generateSecurityVisualization(title, colors);
    } else if (titleLower.includes('conclusion') || titleLower.includes('summary')) {
        return generateConclusionVisualization(title, colors);
    } else {
        return generateGenericVisualization(title, colors);
    }
}

// Machine Learning visualization with neural network nodes
function generateMLVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Neural network visualization -->
        <!-- Input layer -->
        <circle cx="150" cy="150" r="15" fill="${colors.text}" opacity="0.9"/>
        <circle cx="150" cy="200" r="15" fill="${colors.text}" opacity="0.9"/>
        <circle cx="150" cy="250" r="15" fill="${colors.text}" opacity="0.9"/>
        <circle cx="150" cy="300" r="15" fill="${colors.text}" opacity="0.9"/>
        
        <!-- Hidden layer -->
        <circle cx="300" cy="120" r="12" fill="${colors.text}" opacity="0.8"/>
        <circle cx="300" cy="170" r="12" fill="${colors.text}" opacity="0.8"/>
        <circle cx="300" cy="220" r="12" fill="${colors.text}" opacity="0.8"/>
        <circle cx="300" cy="270" r="12" fill="${colors.text}" opacity="0.8"/>
        <circle cx="300" cy="320" r="12" fill="${colors.text}" opacity="0.8"/>
        
        <!-- Output layer -->
        <circle cx="450" cy="175" r="15" fill="${colors.text}" opacity="0.9"/>
        <circle cx="450" cy="225" r="15" fill="${colors.text}" opacity="0.9"/>
        <circle cx="450" cy="275" r="15" fill="${colors.text}" opacity="0.9"/>
        
        <!-- Connections -->
        <line x1="165" y1="150" x2="285" y2="120" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="165" y1="200" x2="285" y2="170" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="165" y1="250" x2="285" y2="220" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="315" y1="170" x2="435" y2="175" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="315" y1="220" x2="435" y2="225" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="315" y1="270" x2="435" y2="275" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        
        <!-- Labels -->
        <text x="150" y="350" text-anchor="middle" fill="${colors.text}" font-family="Arial" font-size="14" font-weight="bold">Input</text>
        <text x="300" y="350" text-anchor="middle" fill="${colors.text}" font-family="Arial" font-size="14" font-weight="bold">Hidden</text>
        <text x="450" y="350" text-anchor="middle" fill="${colors.text}" font-family="Arial" font-size="14" font-weight="bold">Output</text>
        
        <!-- Title -->
        <foreignObject x="500" y="100" width="280" height="200">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 28px; 
                font-weight: bold; 
                text-align: center; 
                line-height: 1.3;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Data visualization with charts and graphs
function generateDataVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Bar chart visualization -->
        <rect x="100" y="250" width="40" height="100" fill="${colors.text}" opacity="0.8"/>
        <rect x="160" y="200" width="40" height="150" fill="${colors.text}" opacity="0.8"/>
        <rect x="220" y="150" width="40" height="200" fill="${colors.text}" opacity="0.8"/>
        <rect x="280" y="180" width="40" height="170" fill="${colors.text}" opacity="0.8"/>
        
        <!-- Pie chart -->
        <circle cx="500" cy="200" r="80" fill="none" stroke="${colors.text}" stroke-width="8" stroke-dasharray="150 200" opacity="0.8" transform="rotate(-90 500 200)"/>
        <circle cx="500" cy="200" r="80" fill="none" stroke="${colors.text}" stroke-width="8" stroke-dasharray="100 250" opacity="0.6" transform="rotate(60 500 200)"/>
        <circle cx="500" cy="200" r="80" fill="none" stroke="${colors.text}" stroke-width="8" stroke-dasharray="80 270" opacity="0.4" transform="rotate(160 500 200)"/>
        
        <!-- Data points scatter -->
        <circle cx="120" cy="120" r="6" fill="${colors.text}" opacity="0.7"/>
        <circle cx="180" cy="140" r="6" fill="${colors.text}" opacity="0.7"/>
        <circle cx="240" cy="110" r="6" fill="${colors.text}" opacity="0.7"/>
        <circle cx="300" cy="130" r="6" fill="${colors.text}" opacity="0.7"/>
        <circle cx="360" cy="100" r="6" fill="${colors.text}" opacity="0.7"/>
        
        <!-- Title -->
        <foreignObject x="50" y="50" width="700" height="100">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 32px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Web development visualization with browser and code elements
function generateWebDevVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Browser window -->
        <rect x="150" y="120" width="300" height="200" fill="${colors.text}" opacity="0.1" rx="10"/>
        <rect x="150" y="120" width="300" height="30" fill="${colors.text}" opacity="0.3" rx="10 10 0 0"/>
        <circle cx="170" cy="135" r="5" fill="${colors.bg}" opacity="0.8"/>
        <circle cx="185" cy="135" r="5" fill="${colors.bg}" opacity="0.8"/>
        <circle cx="200" cy="135" r="5" fill="${colors.bg}" opacity="0.8"/>
        
        <!-- Code brackets -->
        <text x="480" y="180" fill="${colors.text}" font-family="monospace" font-size="40" opacity="0.7">&lt;</text>
        <text x="520" y="180" fill="${colors.text}" font-family="monospace" font-size="40" opacity="0.7">/</text>
        <text x="560" y="180" fill="${colors.text}" font-family="monospace" font-size="40" opacity="0.7">&gt;</text>
        
        <text x="480" y="220" fill="${colors.text}" font-family="monospace" font-size="40" opacity="0.7">&lt;</text>
        <text x="560" y="220" fill="${colors.text}" font-family="monospace" font-size="40" opacity="0.7">&gt;</text>
        
        <!-- Server/database icon -->
        <rect x="80" y="180" width="40" height="60" fill="${colors.text}" opacity="0.7" rx="5"/>
        <rect x="80" y="190" width="40" height="8" fill="${colors.bg}" opacity="0.8"/>
        <rect x="80" y="210" width="40" height="8" fill="${colors.bg}" opacity="0.8"/>
        <rect x="80" y="230" width="40" height="8" fill="${colors.bg}" opacity="0.8"/>
        
        <!-- Connection lines -->
        <line x1="120" y1="210" x2="150" y2="210" stroke="${colors.text}" stroke-width="3" opacity="0.6"/>
        <line x1="450" y1="210" x2="480" y2="210" stroke="${colors.text}" stroke-width="3" opacity="0.6"/>
        
        <!-- Title -->
        <foreignObject x="100" y="280" width="600" height="100">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 28px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Process/workflow visualization with connected steps
function generateProcessVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Process steps -->
        <circle cx="150" cy="200" r="30" fill="${colors.text}" opacity="0.8"/>
        <text x="150" y="205" text-anchor="middle" fill="${colors.bg}" font-family="Arial" font-size="16" font-weight="bold">1</text>
        
        <circle cx="300" cy="200" r="30" fill="${colors.text}" opacity="0.8"/>
        <text x="300" y="205" text-anchor="middle" fill="${colors.bg}" font-family="Arial" font-size="16" font-weight="bold">2</text>
        
        <circle cx="450" cy="200" r="30" fill="${colors.text}" opacity="0.8"/>
        <text x="450" y="205" text-anchor="middle" fill="${colors.bg}" font-family="Arial" font-size="16" font-weight="bold">3</text>
        
        <circle cx="600" cy="200" r="30" fill="${colors.text}" opacity="0.8"/>
        <text x="600" y="205" text-anchor="middle" fill="${colors.bg}" font-family="Arial" font-size="16" font-weight="bold">4</text>
        
        <!-- Arrows -->
        <polygon points="200,200 240,190 240,210" fill="${colors.text}" opacity="0.7"/>
        <polygon points="350,200 390,190 390,210" fill="${colors.text}" opacity="0.7"/>
        <polygon points="500,200 540,190 540,210" fill="${colors.text}" opacity="0.7"/>
        
        <!-- Title -->
        <foreignObject x="100" y="100" width="600" height="80">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 28px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Generic concept visualization
function generateGenericVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Abstract geometric shapes -->
        <polygon points="150,150 200,120 250,150 200,180" fill="${colors.text}" opacity="0.7"/>
        <rect x="300" y="130" width="80" height="80" fill="${colors.text}" opacity="0.6" rx="10"/>
        <circle cx="500" cy="170" r="40" fill="${colors.text}" opacity="0.5"/>
        
        <!-- Connecting lines -->
        <line x1="250" y1="150" x2="300" y2="170" stroke="${colors.text}" stroke-width="3" opacity="0.6"/>
        <line x1="380" y1="170" x2="460" y2="170" stroke="${colors.text}" stroke-width="3" opacity="0.6"/>
        
        <!-- Title -->
        <foreignObject x="50" y="250" width="700" height="150">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 32px; 
                font-weight: bold; 
                text-align: center; 
                line-height: 1.2;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Network visualization
function generateNetworkVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Network nodes -->
        <circle cx="200" cy="150" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="350" cy="120" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="500" cy="150" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="200" cy="280" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="350" cy="250" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="500" cy="280" r="20" fill="${colors.text}" opacity="0.8"/>
        <circle cx="350" cy="185" r="25" fill="${colors.text}" opacity="0.9"/>
        
        <!-- Network connections -->
        <line x1="220" y1="150" x2="330" y2="140" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="370" y1="120" x2="480" y2="150" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="220" y1="280" x2="330" y2="250" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="370" y1="250" x2="480" y2="280" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="350" y1="140" x2="350" y2="160" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="350" y1="210" x2="350" y2="230" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        
        <!-- Title -->
        <foreignObject x="100" y="320" width="600" height="100">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 28px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Security visualization with shield and lock icons
function generateSecurityVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Shield -->
        <path d="M300 120 L350 100 L400 120 L400 200 L350 250 L300 200 Z" fill="${colors.text}" opacity="0.8"/>
        <text x="350" y="185" text-anchor="middle" fill="${colors.bg}" font-family="Arial" font-size="24" font-weight="bold">🔒</text>
        
        <!-- Security layers -->
        <circle cx="350" cy="175" r="60" fill="none" stroke="${colors.text}" stroke-width="2" opacity="0.5"/>
        <circle cx="350" cy="175" r="80" fill="none" stroke="${colors.text}" stroke-width="2" opacity="0.4"/>
        <circle cx="350" cy="175" r="100" fill="none" stroke="${colors.text}" stroke-width="2" opacity="0.3"/>
        
        <!-- Title -->
        <foreignObject x="100" y="280" width="600" height="100">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 28px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

// Conclusion visualization with checkmarks and summary elements
function generateConclusionVisualization(title, colors) {
    return `<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:1" />
                <stop offset="100%" style="stop-color:${colors.accent};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="800" height="450" fill="url(#grad)"/>
        
        <!-- Checkmarks -->
        <circle cx="200" cy="150" r="25" fill="${colors.text}" opacity="0.8"/>
        <path d="M190 150 L197 157 L210 143" stroke="${colors.bg}" stroke-width="3" fill="none"/>
        
        <circle cx="300" cy="200" r="25" fill="${colors.text}" opacity="0.8"/>
        <path d="M290 200 L297 207 L310 193" stroke="${colors.bg}" stroke-width="3" fill="none"/>
        
        <circle cx="400" cy="170" r="25" fill="${colors.text}" opacity="0.8"/>
        <path d="M390 170 L397 177 L410 163" stroke="${colors.bg}" stroke-width="3" fill="none"/>
        
        <!-- Summary box -->
        <rect x="480" y="140" width="120" height="80" fill="${colors.text}" opacity="0.2" rx="10"/>
        <text x="540" y="165" text-anchor="middle" fill="${colors.text}" font-family="Arial" font-size="16" font-weight="bold">Summary</text>
        <line x1="500" y1="175" x2="580" y2="175" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="500" y1="185" x2="570" y2="185" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="500" y1="195" x2="580" y2="195" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        <line x1="500" y1="205" x2="560" y2="205" stroke="${colors.text}" stroke-width="2" opacity="0.6"/>
        
        <!-- Title -->
        <foreignObject x="100" y="260" width="600" height="100">
            <div xmlns="http://www.w3.org/1999/xhtml" style="
                color: ${colors.text}; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 32px; 
                font-weight: bold; 
                text-align: center; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">${title}</div>
        </foreignObject>
    </svg>`;
}

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
        // Try Ollama first (more reliable for local setup)
        try {
            const ollamaResponse = await axios.post(`${OLLAMA_ENDPOINT}/api/generate`, {
                model: "llama3.1:8b",
                prompt: `${prompt}\n\nPlease respond with valid JSON only.`,
                stream: false,
                options: {
                    temperature: 0.7
                }
            }, {
                timeout: 30000
            });

            if (ollamaResponse.data && ollamaResponse.data.response) {
                try {
                    // Try to parse the JSON response
                    const jsonMatch = ollamaResponse.data.response.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        const presentation = JSON.parse(jsonMatch[0]);
                        if (presentation.title && presentation.slides) {
                            console.log('Successfully generated presentation using Ollama');
                            // Add images to each slide
                            const enhancedPresentation = await addImagesToPresentation(presentation, style);
                            return enhancedPresentation;
                        }
                    }
                } catch (parseError) {
                    console.log('Ollama response parsing failed, trying LiteLLM');
                }
            }
        } catch (ollamaError) {
            console.log('Ollama unavailable, trying LiteLLM:', ollamaError.message);
        }

        // Fallback to LiteLLM
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
            },
            timeout: 10000
        });

        const aiResponse = response.data.choices[0].message.content;

        // Try to parse JSON response
        try {
            const presentation = JSON.parse(aiResponse);
            // Add images to each slide
            const enhancedPresentation = await addImagesToPresentation(presentation, style);
            return enhancedPresentation;
        } catch (parseError) {
            console.warn('AI response parsing failed, using fallback structure');
            return await createFallbackPresentation(topic, style, slides_count);
        }
    } catch (error) {
        console.error('AI generation error:', error.message);
        console.log('Using fallback presentation generation');
        return await createFallbackPresentation(topic, style, slides_count);
    }
}

// Add images to presentation slides
async function addImagesToPresentation(presentation, style) {
    const enhancedSlides = await Promise.all(
        presentation.slides.map(async (slide) => {
            const image = await generateSlideImage(slide.title, slide.content, style);
            return {
                ...slide,
                image: image
            };
        })
    );

    return {
        ...presentation,
        slides: enhancedSlides
    };
}

// Fallback presentation generator when AI is unavailable
async function createFallbackPresentation(topic, style, slides_count) {
    const styleTemplates = {
        professional: {
            intro: "Welcome to our comprehensive overview of",
            points: ["Key concepts and definitions", "Industry applications", "Best practices and methodologies"],
            conclusion: "Implementing these strategies for success"
        },
        casual: {
            intro: "Let's dive into the fascinating world of",
            points: ["Cool things you should know", "Real-world examples", "Why this matters to you"],
            conclusion: "Wrapping up our journey"
        },
        academic: {
            intro: "An analytical examination of",
            points: ["Theoretical foundations", "Research methodologies", "Empirical evidence and findings"],
            conclusion: "Implications for future research"
        },
        creative: {
            intro: "Exploring the creative possibilities of",
            points: ["Innovative approaches", "Creative applications", "Inspiration and ideas"],
            conclusion: "Unleashing your creative potential"
        },
        technical: {
            intro: "Technical deep-dive into",
            points: ["System architecture", "Implementation details", "Performance considerations"],
            conclusion: "Technical recommendations and next steps"
        }
    };

    const template = styleTemplates[style] || styleTemplates.professional;
    const slides = [];

    // Title slide
    const titleSlide = {
        title: topic.charAt(0).toUpperCase() + topic.slice(1),
        content: [
            `${template.intro} ${topic}`,
            `${style.charAt(0).toUpperCase() + style.slice(1)} presentation format`,
            "AI-generated content for educational purposes"
        ],
        notes: "Welcome the audience and introduce the topic with enthusiasm",
        image: await generateSlideImage(topic, `Introduction to ${topic}`, style)
    };
    slides.push(titleSlide);

    // Content slides
    const contentSlides = Math.max(1, slides_count - 2); // Reserve slots for intro and conclusion
    for (let i = 0; i < contentSlides; i++) {
        const slideNum = i + 1;
        const slideTitle = `${topic} - Part ${slideNum}`;
        const slideContent = [
            template.points[i % template.points.length],
            `Key insight ${slideNum} about ${topic}`,
            `Practical application in ${style} context`,
            "Supporting evidence and examples"
        ];

        slides.push({
            title: slideTitle,
            content: slideContent,
            notes: `Elaborate on the key concepts presented in slide ${slideNum}. Provide specific examples and engage the audience with questions.`,
            image: await generateSlideImage(slideTitle, slideContent, style)
        });
    }

    // Conclusion slide
    if (slides_count > 1) {
        const conclusionContent = [
            template.conclusion,
            `Key takeaways from ${topic}`,
            "Questions and discussion",
            "Thank you for your attention"
        ];

        slides.push({
            title: "Conclusion",
            content: conclusionContent,
            notes: "Summarize the main points and encourage audience engagement through questions.",
            image: await generateSlideImage("Conclusion", conclusionContent, style)
        });
    }

    return {
        title: `${topic.charAt(0).toUpperCase() + topic.slice(1)} - ${style.charAt(0).toUpperCase() + style.slice(1)} Presentation`,
        slides: slides.slice(0, slides_count) // Ensure exact slide count
    };
}// Routes

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
            position: relative;
        }
        
        .slide-image {
            width: 100%;
            height: 200px;
            margin-bottom: 2rem;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        
        .slide-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .slide-image:hover img {
            transform: scale(1.05);
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
                        \${slide.image ? \`<div class="slide-image"><img src="\${slide.image}" alt="\${slide.title}" /></div>\` : ''}
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