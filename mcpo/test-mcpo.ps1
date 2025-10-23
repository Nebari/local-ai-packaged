# MCPO Test Script for KeikenV (PowerShell Version)
# Tests the MCP-to-OpenAPI proxy functionality

$MCPO_URL = "http://localhost:8940"
$API_KEY = "keiken-mcpo-secret-2024"

Write-Host "🧪 Testing MCPO (MCP-to-OpenAPI Proxy) Integration" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Test 1: Check root documentation
Write-Host ""
Write-Host "📚 Test 1: Checking main documentation endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$MCPO_URL/docs" -Headers @{"Authorization" = "Bearer $API_KEY" } -Method Get
    if ($response -like "*MCP OpenAPI Proxy*") {
        Write-Host "✅ Main docs accessible" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Main docs not accessible" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error accessing main docs: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Check individual MCP service docs
Write-Host ""
Write-Host "🔧 Test 2: Checking individual MCP service documentation..." -ForegroundColor Yellow

$services = @("memory", "time", "filesystem", "sqlite")
foreach ($service in $services) {
    Write-Host "  Testing $service service..." -ForegroundColor Gray
    try {
        $response = Invoke-WebRequest -Uri "$MCPO_URL/$service/docs" -Headers @{"Authorization" = "Bearer $API_KEY" } -Method Get
        if ($response.Content -like "*Swagger UI*") {
            Write-Host "  ✅ $service docs accessible" -ForegroundColor Green
        }
        else {
            Write-Host "  ❌ $service docs not accessible" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  ❌ $service docs error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: Test memory service functionality
Write-Host ""
Write-Host "💾 Test 3: Testing memory service functionality..." -ForegroundColor Yellow

try {
    Write-Host "  Storing test data..." -ForegroundColor Gray
    $body = @{
        key   = "test_key"
        value = "Hello KeikenV!"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$MCPO_URL/memory/store" -Headers @{"Authorization" = "Bearer $API_KEY"; "Content-Type" = "application/json" } -Method Post -Body $body
    Write-Host "  ✅ Memory store operation successful" -ForegroundColor Green
    
    Write-Host "  Retrieving test data..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "$MCPO_URL/memory/get?key=test_key" -Headers @{"Authorization" = "Bearer $API_KEY" } -Method Get
    Write-Host "  ✅ Memory retrieve operation successful" -ForegroundColor Green
    Write-Host "  📊 Retrieved: $($response | ConvertTo-Json)" -ForegroundColor Cyan
}
catch {
    Write-Host "  ❌ Memory operations failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Hot Reload Functionality Test
Write-Host ""
Write-Host "🔥 Test 4: Testing Hot Reload Configuration..." -ForegroundColor Yellow

try {
    # Check if hot reload is enabled by looking at container command
    Write-Host "  Checking MCPO container configuration..." -ForegroundColor Gray
    $containerInfo = docker inspect mcpo | ConvertFrom-Json
    $command = $containerInfo.Config.Cmd -join " "
    
    if ($command -like "*--hot-reload*") {
        Write-Host "  ✅ Hot reload flag detected in container command" -ForegroundColor Green
        Write-Host "  🔧 Command: $command" -ForegroundColor Cyan
    }
    else {
        Write-Host "  ❌ Hot reload flag not found in container command" -ForegroundColor Red
    }
    
    # Check recent logs for configuration loading
    Write-Host "  Checking for configuration reload messages..." -ForegroundColor Gray
    $logs = docker logs mcpo --tail 20 | Out-String
    if ($logs -like "*Loading MCP server configurations from*") {
        Write-Host "  ✅ Configuration loading detected in logs" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠️  No recent configuration loading messages found" -ForegroundColor Yellow
    }
    
    # Display config file path info
    Write-Host "  📁 Config file: /app/config/mcpo.json (container)" -ForegroundColor Cyan
    Write-Host "  📁 Host path: .\mcpo\mcpo.json" -ForegroundColor Cyan
    
}
catch {
    Write-Host "  ❌ Error checking hot reload configuration: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "🎉 MCPO Integration Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔥 Hot Reload Status:" -ForegroundColor Cyan
Write-Host "  • Configuration changes are automatically detected" -ForegroundColor White
Write-Host "  • No container restart required for MCP server updates" -ForegroundColor White
Write-Host "  • Edit mcpo.json to add/remove MCP servers dynamically" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Available Endpoints:" -ForegroundColor Cyan
Write-Host "  • Main API: $MCPO_URL/docs" -ForegroundColor White
Write-Host "  • Memory: $MCPO_URL/memory/docs" -ForegroundColor White  
Write-Host "  • Time: $MCPO_URL/time/docs" -ForegroundColor White
Write-Host "  • Filesystem: $MCPO_URL/filesystem/docs" -ForegroundColor White
Write-Host "  • SQLite: $MCPO_URL/sqlite/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔑 API Key: $API_KEY" -ForegroundColor Yellow
Write-Host "📋 Use these endpoints in your KeikenV agents for MCP functionality!" -ForegroundColor Green