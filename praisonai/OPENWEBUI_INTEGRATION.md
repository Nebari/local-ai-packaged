# OpenWebUI Integration Guide for PraisonAI Teams

## Adding PraisonAI Teams as Models in OpenWebUI

### Step 1: Access OpenWebUI Admin Settings
1. Go to https://openwebui.nebarisoftware.com
2. Click on your profile (bottom left)
3. Select "Admin Panel"
4. Navigate to "Settings" → "Models"

### Step 2: Add PraisonAI API Connection
1. Click "Add Model"
2. Configure the following:

**Model Configuration:**
```json
{
  "name": "PraisonAI Teams",
  "base_url": "http://praisonai-teams:8000/v1",
  "api_key": "not-required",
  "models": [
    {
      "id": "research-team",
      "name": "Research Team",
      "description": "Multi-agent research team with internet search"
    },
    {
      "id": "coding-team", 
      "name": "Coding Team",
      "description": "Software development specialists"
    },
    {
      "id": "business-team",
      "name": "Business Team", 
      "description": "Business analysis and strategy"
    },
    {
      "id": "creative-team",
      "name": "Creative Team",
      "description": "Content and marketing specialists"
    }
  ]
}
```

### Step 3: Alternative Manual Addition
If the above doesn't work, add each team as a separate model:

1. **Research Team Model:**
   - Name: `research-team`
   - Base URL: `http://praisonai-teams:8000/v1`
   - Model ID: `research-team`

2. **Coding Team Model:**
   - Name: `coding-team`  
   - Base URL: `http://praisonai-teams:8000/v1`
   - Model ID: `coding-team`

3. **Business Team Model:**
   - Name: `business-team`
   - Base URL: `http://praisonai-teams:8000/v1` 
   - Model ID: `business-team`

4. **Creative Team Model:**
   - Name: `creative-team`
   - Base URL: `http://praisonai-teams:8000/v1`
   - Model ID: `creative-team`

### Step 4: Usage in OpenWebUI

Once configured, you can:

1. Select any PraisonAI team from the model dropdown
2. Start chatting - your messages will be processed by the multi-agent team
3. Each team will collaborate to provide comprehensive responses

**Example Prompts:**

- **Research Team**: "Research the latest trends in AI and machine learning for 2024"
- **Coding Team**: "Help me design and implement a REST API for user management"
- **Business Team**: "Analyze the market opportunity for a new fintech startup"
- **Creative Team**: "Create a marketing campaign for a sustainable fashion brand"

### Step 5: Monitoring and Logs

You can monitor the PraisonAI service:

```bash
# View logs
docker logs praisonai-teams -f

# Check API status
curl http://localhost:8766/health

# List available teams
curl http://localhost:8766/teams
```

## Team Capabilities

### Research Team
- **Researcher**: Conducts web searches and gathers information
- **Analyst**: Processes and analyzes data
- **Writer**: Creates comprehensive reports

### Coding Team  
- **Architect**: Designs system architecture
- **Developer**: Implements code solutions
- **Tester**: Validates and tests code

### Business Team
- **Business Analyst**: Analyzes requirements and opportunities
- **Financial Analyst**: Provides financial insights
- **Strategist**: Develops strategic recommendations

### Creative Team
- **Creative Director**: Leads creative vision
- **Copywriter**: Creates marketing copy
- **Content Strategist**: Plans content strategy

Each team collaborates internally to provide comprehensive, multi-perspective responses to your queries.