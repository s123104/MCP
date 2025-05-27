# MCP Docker 自動安裝腳本 (Windows PowerShell)
# 版本: 2.0
# 支援 Windows 10/11 with Docker Desktop
# 需要管理員權限執行

param(
    [string]$Action = "install",
    [switch]$SkipChecks = $false,
    [switch]$Verbose = $false
)

# 設定錯誤處理
$ErrorActionPreference = "Stop"

# 顏色和圖標定義
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
}

$Icons = @{
    Success = "✅"
    Error = "❌"
    Warning = "⚠️"
    Info = "ℹ️"
    Rocket = "🚀"
    Docker = "🐳"
    Gear = "⚙️"
}

# 日誌函數
function Write-ColorOutput($ForegroundColor, $Message) {
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-LogInfo($Message) {
    Write-ColorOutput $Colors.Blue "$($Icons.Info) [INFO] $Message"
}

function Write-LogSuccess($Message) {
    Write-ColorOutput $Colors.Green "$($Icons.Success) [SUCCESS] $Message"
}

function Write-LogWarning($Message) {
    Write-ColorOutput $Colors.Yellow "$($Icons.Warning) [WARNING] $Message"
}

function Write-LogError($Message) {
    Write-ColorOutput $Colors.Red "$($Icons.Error) [ERROR] $Message"
}

function Write-LogStep($Message) {
    Write-ColorOutput $Colors.Magenta "$($Icons.Gear) [STEP] $Message"
}

# 顯示橫幅
function Show-Banner {
    Write-ColorOutput $Colors.Cyan @"
    ███╗   ███╗ ██████╗██████╗     ██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗ 
    ████╗ ████║██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    ██╔████╔██║██║     ██████╔╝    ██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝
    ██║╚██╔╝██║██║     ██╔═══╝     ██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║╚██████╗██║         ██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝     ╚═╝ ╚═════╝╚═╝         ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    
    Model Context Protocol Docker 自動安裝器 v2.0 (Windows)
    支援 Claude Desktop, VS Code, Cursor 自動配置
"@
}

# 檢查管理員權限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 檢查系統需求
function Test-SystemRequirements {
    Write-LogStep "檢查系統需求..."
    
    # 檢查 Windows 版本
    $windowsVersion = [System.Environment]::OSVersion.Version
    if ($windowsVersion.Major -lt 10) {
        Write-LogError "需要 Windows 10 或更新版本"
        exit 1
    }
    Write-LogInfo "Windows 版本: $($windowsVersion.Major).$($windowsVersion.Minor)"
    
    # 檢查 PowerShell 版本
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        Write-LogError "需要 PowerShell 5.0 或更新版本"
        exit 1
    }
    Write-LogInfo "PowerShell 版本: $($psVersion.Major).$($psVersion.Minor)"
    
    Write-LogSuccess "系統需求檢查通過"
}

# 檢查 Docker 狀態
function Test-Docker {
    Write-LogStep "檢查 Docker 狀態..."
    
    try {
        $dockerVersion = docker --version
        Write-LogInfo "Docker 版本: $dockerVersion"
        
        # 檢查 Docker 是否運行
        docker info | Out-Null
        Write-LogSuccess "Docker 運行正常"
        return $true
    }
    catch {
        Write-LogError "Docker 未安裝或未運行"
        Write-LogInfo "請確保 Docker Desktop 已安裝並正在運行"
        Write-LogInfo "下載地址: https://www.docker.com/products/docker-desktop"
        return $false
    }
}

# MCP 服務器定義 (基於真實 Docker Hub 資料)
$MCPServers = @{
    "github" = @{
        Image = "mcp/github"
        Description = "GitHub API 工具和儲存庫管理"
        Downloads = "10000+"
        EnvVars = @("GITHUB_TOKEN")
    }
    "puppeteer" = @{
        Image = "mcp/puppeteer"
        Description = "瀏覽器自動化和網頁抓取"
        Downloads = "10000+"
        EnvVars = @("DOCKER_CONTAINER")
    }
    "time" = @{
        Image = "mcp/time"
        Description = "時間和時區轉換功能"
        Downloads = "10000+"
        EnvVars = @()
    }
    "postgres" = @{
        Image = "mcp/postgres"
        Description = "PostgreSQL 唯讀存取"
        Downloads = "10000+"
        EnvVars = @("POSTGRES_URL")
    }
    "playwright" = @{
        Image = "mcp/playwright"
        Description = "Playwright 網頁自動化"
        Downloads = "5000+"
        EnvVars = @()
    }
    "sentry" = @{
        Image = "mcp/sentry"
        Description = "Sentry.io 錯誤追蹤整合" 
        Downloads = "1700+"
        EnvVars = @("SENTRY_DSN", "SENTRY_ORG")
    }
    "filesystem" = @{
        Image = "mcp/filesystem"
        Description = "本地檔案系統存取"
        Downloads = "1000+"
        EnvVars = @()
    }
    "slack" = @{
        Image = "mcp/slack"
        Description = "Slack 工作區整合"
        Downloads = "800+"
        EnvVars = @("SLACK_BOT_TOKEN")
    }
}

# 選擇 MCP 服務器
function Select-MCPServers {
    Write-LogStep "選擇要安裝的 MCP 服務器..."
    
    Write-ColorOutput $Colors.Cyan "`n可用的 MCP 服務器："
    Write-Output "=================================="
    
    $serverNames = $MCPServers.Keys | Sort-Object
    for ($i = 0; $i -lt $serverNames.Count; $i++) {
        $serverName = $serverNames[$i]
        $server = $MCPServers[$serverName]
        Write-Output ("{0,2}) {1,-15} - {2} (下載量: {3})" -f ($i + 1), $serverName, $server.Description, $server.Downloads)
    }
    
    Write-Output "`n輸入選項 (用空格分隔多個選項，例如: 1 2 3)："
    Write-Output "或輸入 'all' 安裝所有服務器："
    $selection = Read-Host
    
    $selectedServers = @()
    if ($selection -eq "all") {
        $selectedServers = $serverNames
    }
    else {
        $numbers = $selection -split '\s+'
        foreach ($num in $numbers) {
            if ($num -match '^\d+$' -and [int]$num -ge 1 -and [int]$num -le $serverNames.Count) {
                $selectedServers += $serverNames[[int]$num - 1]
            }
        }
    }
    
    if ($selectedServers.Count -eq 0) {
        Write-LogWarning "未選擇任何服務器，將安裝基本服務器 (github, time, puppeteer)"
        $selectedServers = @("github", "time", "puppeteer")
    }
    
    Write-LogInfo "已選擇服務器: $($selectedServers -join ', ')"
    return $selectedServers
}

# 拉取 Docker 映像
function Get-DockerImages($SelectedServers) {
    Write-LogStep "拉取選定的 MCP Docker 映像..."
    
    $failedImages = @()
    
    foreach ($serverName in $SelectedServers) {
        $server = $MCPServers[$serverName]
        $image = $server.Image
        
        Write-LogInfo "拉取 $image..."
        
        try {
            docker pull $image | Out-Null
            Write-LogSuccess "✓ $image 拉取成功"
        }
        catch {
            Write-LogError "✗ $image 拉取失敗"
            $failedImages += $image
        }
    }
    
    if ($failedImages.Count -gt 0) {
        Write-LogWarning "以下映像拉取失敗: $($failedImages -join ', ')"
        Write-LogInfo "請檢查網路連接或映像名稱是否正確"
    }
}

# 建立 Docker 網路
function New-DockerNetwork {
    Write-LogStep "建立 MCP 專用 Docker 網路..."
    
    try {
        docker network create mcp-network --driver bridge --subnet=172.20.0.0/16 | Out-Null
        Write-LogSuccess "MCP 網路建立成功"
    }
    catch {
        Write-LogWarning "MCP 網路已存在或建立失敗"
    }
}

# 生成環境變數配置
function New-EnvConfig {
    Write-LogStep "生成環境變數配置..."
    
    $envContent = @"
# MCP Docker 環境變數配置
# 請根據需要填入實際的 API 金鑰和配置

# GitHub 整合
GITHUB_TOKEN=your_github_personal_access_token_here

# PostgreSQL 資料庫 (如果需要)
POSTGRES_URL=postgresql://username:password@host:5432/database

# Slack 整合 (如果需要)
SLACK_BOT_TOKEN=your_slack_bot_token_here

# Sentry 整合 (如果需要)
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ORG=your_sentry_org

# 其他配置
DOCKER_CONTAINER=true
"@
    
    $envContent | Out-File -FilePath "mcp.env" -Encoding UTF8
    Write-LogSuccess "環境變數範本已建立: mcp.env"
    Write-LogInfo "請編輯 mcp.env 檔案並填入實際的 API 金鑰"
}

# 生成 Claude Desktop 配置
function New-ClaudeConfig($SelectedServers) {
    Write-LogStep "生成 Claude Desktop 配置..."
    
    $configDir = "$env:APPDATA\Claude"
    $configFile = "$configDir\claude_desktop_config.json"
    
    # 建立配置目錄
    if (!(Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # 備份現有配置
    if (Test-Path $configFile) {
        $backupFile = "$configFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $configFile $backupFile
        Write-LogInfo "現有配置已備份至: $backupFile"
    }
    
    # 生成配置對象
    $config = @{
        mcpServers = @{}
    }
    
    foreach ($serverName in $SelectedServers) {
        $server = $MCPServers[$serverName]
        $image = $server.Image
        
        $serverConfig = @{
            command = "docker"
            args = @("run", "-i", "--rm", "--read-only", "--security-opt", "no-new-privileges")
        }
        
        # 根據服務器類型設定記憶體限制
        switch ($serverName) {
            "puppeteer" { $serverConfig.args += @("--memory", "512m") }
            "time" { $serverConfig.args += @("--memory", "128m") }
            default { $serverConfig.args += @("--memory", "256m") }
        }
        
        # 添加環境變數
        $envConfig = @{}
        foreach ($envVar in $server.EnvVars) {
            $serverConfig.args += @("-e", $envVar)
            
            switch ($envVar) {
                "GITHUB_TOKEN" { $envConfig[$envVar] = "填入您的 GitHub Token" }
                "POSTGRES_URL" { $envConfig[$envVar] = "填入您的 PostgreSQL 連接字串" }
                "SLACK_BOT_TOKEN" { $envConfig[$envVar] = "填入您的 Slack Bot Token" }
                "DOCKER_CONTAINER" { $envConfig[$envVar] = "true" }
                default { $envConfig[$envVar] = "填入對應的配置值" }
            }
        }
        
        $serverConfig.args += $image
        
        if ($envConfig.Count -gt 0) {
            $serverConfig.env = $envConfig
        }
        
        $config.mcpServers[$serverName] = $serverConfig
    }
    
    # 輸出到檔案
    $jsonConfig = $config | ConvertTo-Json -Depth 10
    $jsonConfig | Out-File -FilePath "claude_desktop_config.json" -Encoding UTF8
    
    Write-LogSuccess "Claude Desktop 配置已生成: claude_desktop_config.json"
    Write-LogInfo "配置檔案位置: $configFile"
    Write-LogWarning "請記得填入實際的 API 金鑰後重啟 Claude Desktop"
}

# 生成 VS Code 配置
function New-VSCodeConfig($SelectedServers) {
    Write-LogStep "生成 VS Code MCP 配置..."
    
    $inputs = @()
    $servers = @{}
    
    # 生成輸入提示
    foreach ($serverName in $SelectedServers) {
        $server = $MCPServers[$serverName]
        
        foreach ($envVar in $server.EnvVars) {
            $isPassword = $envVar -match "(TOKEN|KEY|PASSWORD|SECRET)"
            
            $inputs += @{
                type = "promptString"
                id = "$($serverName)_$($envVar.ToLower())"
                description = "$($server.Description) $envVar"
                password = $isPassword
            }
        }
    }
    
    # 生成服務器配置
    foreach ($serverName in $SelectedServers) {
        $server = $MCPServers[$serverName]
        
        $serverConfig = @{
            command = "docker"
            args = @("run", "-i", "--rm", "--read-only", "--security-opt", "no-new-privileges")
        }
        
        $envConfig = @{}
        foreach ($envVar in $server.EnvVars) {
            $inputId = "$($serverName)_$($envVar.ToLower())"
            $serverConfig.args += @("-e", $envVar)
            $envConfig[$envVar] = "`${input:$inputId}"
        }
        
        $serverConfig.args += $server.Image
        
        if ($envConfig.Count -gt 0) {
            $serverConfig.env = $envConfig
        }
        
        $servers[$serverName] = $serverConfig
    }
    
    $vscodeConfig = @{
        inputs = $inputs
        servers = $servers
    }
    
    $jsonConfig = $vscodeConfig | ConvertTo-Json -Depth 10
    $jsonConfig | Out-File -FilePath "mcp.json" -Encoding UTF8
    
    Write-LogSuccess "VS Code MCP 配置已生成: mcp.json"
    Write-LogInfo "請將此檔案複製到您的 VS Code 專案的 .vscode\ 目錄中"
}

# 生成 Docker Compose 配置
function New-DockerComposeConfig($SelectedServers) {
    Write-LogStep "生成 Docker Compose 配置..."
    
    $composeContent = @"
version: '3.8'

services:
"@
    
    foreach ($serverName in $SelectedServers) {
        $server = $MCPServers[$serverName]
        
        $composeContent += @"

  $serverName-mcp:
    image: $($server.Image)
    container_name: $serverName-mcp
    stdin_open: true
    tty: true
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    mem_limit: 256m
    cpus: 0.5
    networks:
      - mcp-network
    labels:
      - "mcp.server=$serverName"
      - "mcp.type=automated"
"@
        
        if ($server.EnvVars.Count -gt 0) {
            $composeContent += "`n    environment:"
            foreach ($envVar in $server.EnvVars) {
                $composeContent += "`n      - $envVar=`${$envVar}"
            }
        }
    }
    
    $composeContent += @"

networks:
  mcp-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16

volumes:
  mcp-data:
    driver: local
"@
    
    $composeContent | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
    Write-LogSuccess "Docker Compose 配置已生成: docker-compose.yml"
}

# 生成管理腳本
function New-ManagementScripts {
    Write-LogStep "生成管理腳本..."
    
    # PowerShell 管理腳本
    $managerScript = @'
# MCP Docker 管理腳本 (PowerShell)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "update", "clean")]
    [string]$Action,
    
    [string]$Service = ""
)

$ComposeFile = "docker-compose.yml"

switch ($Action) {
    "start" {
        Write-Host "🚀 啟動 MCP 服務器..." -ForegroundColor Green
        docker-compose -f $ComposeFile up -d
    }
    "stop" {
        Write-Host "🛑 停止 MCP 服務器..." -ForegroundColor Yellow
        docker-compose -f $ComposeFile down
    }
    "restart" {
        Write-Host "🔄 重啟 MCP 服務器..." -ForegroundColor Blue
        docker-compose -f $ComposeFile restart
    }
    "status" {
        Write-Host "📊 MCP 服務器狀態：" -ForegroundColor Cyan
        docker-compose -f $ComposeFile ps
    }
    "logs" {
        if ($Service) {
            docker-compose -f $ComposeFile logs -f $Service
        } else {
            docker-compose -f $ComposeFile logs -f
        }
    }
    "update" {
        Write-Host "📥 更新 MCP 映像..." -ForegroundColor Magenta
        docker-compose -f $ComposeFile pull
        docker-compose -f $ComposeFile up -d
    }
    "clean" {
        Write-Host "🧹 清理未使用的 Docker 資源..." -ForegroundColor DarkYellow
        docker system prune -f
        docker image prune -f
    }
}
'@
    
    $managerScript | Out-File -FilePath "mcp-manager.ps1" -Encoding UTF8
    Write-LogSuccess "管理腳本已生成: mcp-manager.ps1"
    
    # 健康檢查腳本
    $healthScript = @'
# MCP 健康檢查腳本 (PowerShell)

Write-Host "🏥 MCP 健康檢查報告" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# 檢查 Docker 狀態
try {
    docker info | Out-Null
    Write-Host "✅ Docker 運行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 未運行" -ForegroundColor Red
    exit 1
}

# 檢查 MCP 容器狀態
Write-Host "`n📦 MCP 容器狀態：" -ForegroundColor Yellow
docker ps --filter "label=mcp.type=automated" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 檢查資源使用
Write-Host "`n📊 資源使用情況：" -ForegroundColor Blue
docker stats --no-stream --filter "label=mcp.type=automated" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 檢查網路連接
Write-Host "`n🌐 網路狀態：" -ForegroundColor Magenta
docker network ls | Where-Object { $_ -match "mcp" }

Write-Host "`n✅ 健康檢查完成" -ForegroundColor Green
'@
    
    $healthScript | Out-File -FilePath "mcp-health-check.ps1" -Encoding UTF8
    Write-LogSuccess "健康檢查腳本已生成: mcp-health-check.ps1"
}

# 顯示安裝摘要
function Show-InstallationSummary($SelectedServers) {
    Write-ColorOutput $Colors.Green "`n🎉=================================="
    Write-ColorOutput $Colors.Green "  MCP Docker 安裝完成！"
    Write-ColorOutput $Colors.Green "==================================`n"
    
    Write-ColorOutput $Colors.Cyan "📋 安裝摘要："
    Write-Output "• 已安裝 MCP 服務器: $($SelectedServers -join ', ')"
    Write-Output "• 已建立 Docker 網路: mcp-network"
    Write-Output "• 已生成配置檔案："
    Write-Output "  - claude_desktop_config.json (Claude Desktop)"
    Write-Output "  - mcp.json (VS Code)"
    Write-Output "  - docker-compose.yml (Docker Compose)"
    Write-Output "  - mcp.env (環境變數範本)"
    Write-Output "• 已生成管理腳本："
    Write-Output "  - mcp-manager.ps1 (服務管理)"
    Write-Output "  - mcp-health-check.ps1 (健康檢查)"
    
    Write-ColorOutput $Colors.Cyan "`n📝 下一步："
    Write-Output "1. 編輯 mcp.env 檔案並填入實際的 API 金鑰"
    Write-Output "2. 將 claude_desktop_config.json 複製到 Claude Desktop 配置目錄"
    Write-Output "   Windows: $env:APPDATA\Claude\"
    Write-Output "3. 重啟 Claude Desktop"
    Write-Output "4. 測試 MCP 功能 (例如詢問「現在幾點？」)"
    
    Write-ColorOutput $Colors.Cyan "`n🛠️ 管理命令："
    Write-Output "• 啟動服務: .\mcp-manager.ps1 start"
    Write-Output "• 檢查狀態: .\mcp-manager.ps1 status"
    Write-Output "• 查看日誌: .\mcp-manager.ps1 logs"
    Write-Output "• 健康檢查: .\mcp-health-check.ps1"
    
    Write-ColorOutput $Colors.Cyan "`n📚 更多資源："
    Write-Output "• Docker MCP 官方文檔: https://docs.docker.com/ai/mcp-catalog-and-toolkit/"
    Write-Output "• MCP 協定規範: https://modelcontextprotocol.io"
    Write-Output "• GitHub 討論區: https://github.com/docker/mcp-servers"
    
    Write-ColorOutput $Colors.Green "`n🎉 安裝完成！開始享受 MCP Docker 的強大功能！`n"
}

# 主執行函數
function Invoke-Main {
    try {
        Show-Banner
        
        if (!$SkipChecks) {
            if (!(Test-Administrator)) {
                Write-LogWarning "建議以管理員權限執行此腳本"
            }
            
            Test-SystemRequirements
            
            if (!(Test-Docker)) {
                exit 1
            }
        }
        
        switch ($Action) {
            "install" {
                $selectedServers = Select-MCPServers
                Get-DockerImages $selectedServers
                New-DockerNetwork
                New-EnvConfig
                New-ClaudeConfig $selectedServers
                New-VSCodeConfig $selectedServers
                New-DockerComposeConfig $selectedServers
                New-ManagementScripts
                Show-InstallationSummary $selectedServers
            }
            "uninstall" {
                Write-LogStep "移除 MCP Docker 環境..."
                
                # 停止並移除容器
                try {
                    docker-compose down 2>$null
                    Write-LogSuccess "MCP 容器已停止"
                } catch {
                    Write-LogWarning "無法停止 MCP 容器"
                }
                
                # 移除網路
                try {
                    docker network rm mcp-network 2>$null
                    Write-LogSuccess "MCP 網路已移除"
                } catch {
                    Write-LogWarning "無法移除 MCP 網路"
                }
                
                Write-LogSuccess "卸載完成"
            }
            default {
                Write-LogError "無效的操作: $Action"
                Write-Output "用法: .\install-mcp-docker.ps1 [-Action install|uninstall] [-SkipChecks] [-Verbose]"
                exit 1
            }
        }
    }
    catch {
        Write-LogError "腳本執行過程中發生錯誤: $($_.Exception.Message)"
        if ($Verbose) {
            Write-Output $_.Exception.StackTrace
        }
        exit 1
    }
}

# 執行主函數
Invoke-Main
