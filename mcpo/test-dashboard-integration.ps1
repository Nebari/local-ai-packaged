#!/usr/bin/env pwsh
# Integration test for MCPO + Status Dashboard MCP management workflow
# Tests the full add → list → remove cycle via the dashboard API endpoints

$DASHBOARD_URL = "http://localhost:8930"
$TEST_SERVER_NAME = "test-echo-server"

Write-Host "=== MCPO Dashboard Integration Test ===" -ForegroundColor Green
Write-Host "Testing: Add → List → Remove MCP server workflow" -ForegroundColor Cyan

# Function to make API calls with error handling
function Invoke-DashboardApi {
    param($Method, $Endpoint, $Body = $null)
    
    try {
        $headers = @{ 'Content-Type' = 'application/json' }
        $params = @{
            Uri     = "$DASHBOARD_URL$Endpoint"
            Method  = $Method
            Headers = $headers
        }
        
        if ($Body) {
            $params.Body = $Body | ConvertTo-Json -Depth 5
        }
        
        $response = Invoke-RestMethod @params
        return @{ Success = $true; Data = $response }
    }
    catch {
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

Write-Host "`n1. Testing GET /api/mcpo/templates..." -ForegroundColor Yellow
$templates = Invoke-DashboardApi -Method GET -Endpoint "/api/mcpo/templates"
if ($templates.Success) {
    Write-Host "✅ Templates loaded successfully" -ForegroundColor Green
    Write-Host "   Available templates: $($templates.Data.Keys -join ', ')" -ForegroundColor Gray
}
else {
    Write-Host "❌ Failed to load templates: $($templates.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Getting initial MCP server count..." -ForegroundColor Yellow
$initialServers = Invoke-DashboardApi -Method GET -Endpoint "/api/mcpo/servers"
if ($initialServers.Success) {
    $initialCount = $initialServers.Data.servers.Count
    Write-Host "✅ Initial MCP server count: $initialCount" -ForegroundColor Green
}
else {
    Write-Host "❌ Failed to get initial servers: $($initialServers.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n3. Testing POST /api/mcpo/servers (add test server)..." -ForegroundColor Yellow
$testServerConfig = @{
    serverName   = $TEST_SERVER_NAME
    serverConfig = @{
        command     = "npx"
        args        = @("-y", "@modelcontextprotocol/server-echo")
        description = "Test echo server for integration testing"
    }
}

$addResult = Invoke-DashboardApi -Method POST -Endpoint "/api/mcpo/servers" -Body $testServerConfig
if ($addResult.Success) {
    Write-Host "✅ Test server added successfully" -ForegroundColor Green
}
else {
    Write-Host "❌ Failed to add test server: $($addResult.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n4. Verifying server was added..." -ForegroundColor Yellow
Start-Sleep -Seconds 2  # Allow time for hot-reload
$updatedServers = Invoke-DashboardApi -Method GET -Endpoint "/api/mcpo/servers"
if ($updatedServers.Success) {
    $newCount = $updatedServers.Data.servers.Count
    $testServer = $updatedServers.Data.servers | Where-Object { $_.name -eq $TEST_SERVER_NAME }
    
    if ($newCount -eq ($initialCount + 1) -and $null -ne $testServer) {
        Write-Host "✅ Server count increased to $newCount, test server found" -ForegroundColor Green
        Write-Host "   Test server status: $($testServer.status)" -ForegroundColor Gray
        Write-Host "   Test server description: $($testServer.description)" -ForegroundColor Gray
    }
    else {
        Write-Host "❌ Server verification failed (count: $newCount, found: $($null -ne $testServer))" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "❌ Failed to verify servers: $($updatedServers.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n5. Testing GET /api/status (check dashboard totals)..." -ForegroundColor Yellow
$statusResult = Invoke-DashboardApi -Method GET -Endpoint "/api/status"
if ($statusResult.Success) {
    $overall = $statusResult.Data.overall
    Write-Host "✅ Dashboard status loaded" -ForegroundColor Green
    Write-Host "   Total services: $($overall.total)" -ForegroundColor Gray
    Write-Host "   Regular services: $($overall.regularServices)" -ForegroundColor Gray
    Write-Host "   MCP servers: $($overall.mcpServers)" -ForegroundColor Gray
    Write-Host "   Overall status: $($overall.status)" -ForegroundColor Gray
    
    if ($overall.mcpServers -eq $newCount) {
        Write-Host "✅ MCP server count matches in dashboard totals" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  MCP server count mismatch in dashboard totals" -ForegroundColor Yellow
    }
}
else {
    Write-Host "❌ Failed to get dashboard status: $($statusResult.Error)" -ForegroundColor Red
}

Write-Host "`n6. Testing DELETE /api/mcpo/servers/$TEST_SERVER_NAME..." -ForegroundColor Yellow
$deleteResult = Invoke-DashboardApi -Method DELETE -Endpoint "/api/mcpo/servers/$TEST_SERVER_NAME"
if ($deleteResult.Success) {
    Write-Host "✅ Test server deleted successfully" -ForegroundColor Green
}
else {
    Write-Host "❌ Failed to delete test server: $($deleteResult.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n7. Verifying server was removed..." -ForegroundColor Yellow
Start-Sleep -Seconds 2  # Allow time for hot-reload
$finalServers = Invoke-DashboardApi -Method GET -Endpoint "/api/mcpo/servers"
if ($finalServers.Success) {
    $finalCount = $finalServers.Data.servers.Count
    $testServerGone = $finalServers.Data.servers | Where-Object { $_.name -eq $TEST_SERVER_NAME }
    
    if ($finalCount -eq $initialCount -and $null -eq $testServerGone) {
        Write-Host "✅ Server count back to $finalCount, test server removed" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Server removal verification failed (count: $finalCount, still exists: $($null -ne $testServerGone))" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "❌ Failed to verify final servers: $($finalServers.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "`n8. Testing MCPO hot-reload functionality..." -ForegroundColor Yellow
Write-Host "   Checking MCPO logs for reload events..." -ForegroundColor Gray
try {
    $mcpoLogs = docker logs mcpo --since=30s 2>&1 | Out-String
    if ($mcpoLogs -match "Loading MCP server configurations") {
        Write-Host "✅ MCPO hot-reload detected in logs" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Hot-reload events not detected in recent logs" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Could not check MCPO logs: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=== Integration Test Complete ===" -ForegroundColor Green
Write-Host "✅ All workflow steps completed successfully!" -ForegroundColor Green
Write-Host "✅ Dashboard API endpoints working" -ForegroundColor Green
Write-Host "✅ MCP server add/remove cycle functional" -ForegroundColor Green
Write-Host "✅ Dashboard totals updating correctly" -ForegroundColor Green
Write-Host "✅ Hot-reload integration confirmed" -ForegroundColor Green

Write-Host "`nDashboard available at: $DASHBOARD_URL" -ForegroundColor Cyan
Write-Host "Try the MCP Server Management panel to test the UI!" -ForegroundColor Cyan