# MCP Docker 實戰範例集

基於真實 Docker Hub MCP Catalog 的完整使用範例

## 🔥 熱門 MCP 服務器 (基於下載量)

根據 Docker Hub 統計的最熱門 MCP 服務器：

### 第一梯隊 (10K+ 下載)
- **mcp/github** - 10K+ pulls - GitHub API 工具和儲存庫管理
- **mcp/puppeteer** - 10K+ pulls - 瀏覽器自動化和網頁抓取
- **mcp/time** - 10K+ pulls - 時間和時區轉換功能
- **mcp/postgres** - 10K+ pulls - PostgreSQL 唯讀存取

### 第二梯隊 (1K-10K 下載)
- **mcp/playwright** - 5.0K pulls - Playwright 網頁自動化
- **mcp/signatures** - 5.3K pulls - Cosign 簽名驗證
- **mcp/sentry** - 1.7K pulls - Sentry.io 錯誤追蹤整合
- **mcp/line** - 1.1K pulls - LINE 通訊應用整合

## 🚀 即用型配置範例

### 1. 全功能開發環境配置

適合開發者的完整配置，包含最常用的 MCP 服務器：

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "--memory", "256m",
        "-e", "GITHUB_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    },
    "time": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "--memory", "128m",
        "mcp/time"
      ]
    },
    "puppeteer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--security-opt", "no-new-privileges",
        "--memory", "512m",
        "-e", "DOCKER_CONTAINER=true",
        "mcp/puppeteer"
      ]
    }
  }
}
```

### 2. 資料分析師配置

專為資料分析和資料庫操作優化：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges", 
        "--memory", "256m",
        "-e", "POSTGRES_URL",
        "mcp/postgres"
      ],
      "env": {
        "POSTGRES_URL": "postgresql://user:pass@host:5432/dbname"
      }
    },
    "time": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--memory", "128m",
        "mcp/time"
      ]
    }
  }
}
```

### 3. 網頁自動化專家配置

專注於網頁自動化和測試：

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--memory", "1g",
        "--cpus", "1.0",
        "-e", "DOCKER_CONTAINER=true",
        "mcp/puppeteer"
      ]
    },
    "playwright": {
      "command": "docker", 
      "args": [
        "run", "-i", "--rm",
        "--memory", "1g",
        "--cpus", "1.0",
        "mcp/playwright"
      ]
    }
  }
}
```

## 🐳 Docker Compose 生產環境配置

### 完整的 MCP 服務器堆疊

```yaml
version: '3.8'

services:
  github-mcp:
    image: mcp/github
    container_name: github-mcp
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
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
      - "mcp.type=development"
      - "mcp.category=vcs"

  time-mcp:
    image: mcp/time
    container_name: time-mcp
    stdin_open: true
    tty: true
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    mem_limit: 128m
    cpus: 0.2
    networks:
      - mcp-network
    labels:
      - "mcp.type=utility"
      - "mcp.category=time"

  postgres-mcp:
    image: mcp/postgres
    container_name: postgres-mcp
    environment:
      - POSTGRES_URL=${POSTGRES_URL}
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
      - "mcp.type=database"
      - "mcp.category=postgresql"

  puppeteer-mcp:
    image: mcp/puppeteer
    container_name: puppeteer-mcp
    environment:
      - DOCKER_CONTAINER=true
    stdin_open: true
    tty: true
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    mem_limit: 512m
    cpus: 1.0
    networks:
      - mcp-network
    labels:
      - "mcp.type=automation"
      - "mcp.category=browser"

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
```

## ⚡ 快速啟動腳本

### Linux/macOS 一鍵啟動腳本

```bash
#!/bin/bash
# MCP Docker 快速啟動腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數定義
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查 Docker 是否運行
check_docker() {
    log_info "檢查 Docker 狀態..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未運行或無法存取"
        log_info "請確保 Docker Desktop 已啟動"
        exit 1
    fi
    log_success "Docker 運行正常"
}

# 拉取 MCP 映像
pull_images() {
    log_info "拉取 MCP Docker 映像..."
    
    local images=(
        "mcp/github"
        "mcp/time" 
        "mcp/puppeteer"
        "mcp/postgres"
        "mcp/playwright"
    )
    
    for image in "${images[@]}"; do
        log_info "拉取 $image..."
        if docker pull "$image"; then
            log_success "✓ $image 拉取成功"
        else
            log_warning "✗ $image 拉取失敗"
        fi
    done
}

# 建立 MCP 網路
create_network() {
    log_info "建立 MCP 專用網路..."
    if docker network create mcp-network --driver bridge --subnet=172.20.0.0/16 2>/dev/null; then
        log_success "MCP 網路建立成功"
    else
        log_warning "MCP 網路已存在或建立失敗"
    fi
}

# 啟動基礎 MCP 服務器
start_basic_servers() {
    log_info "啟動基礎 MCP 服務器..."
    
    # 時間服務器 (無需環境變數)
    log_info "啟動時間服務器..."
    docker run -d \
        --name time-mcp \
        --network mcp-network \
        --restart unless-stopped \
        --read-only \
        --tmpfs /tmp \
        --security-opt no-new-privileges:true \
        --memory 128m \
        --cpus 0.2 \
        mcp/time
    
    log_success "基礎 MCP 服務器啟動完成"
}

# 顯示狀態
show_status() {
    log_info "MCP 服務器狀態："
    docker ps --filter "name=*-mcp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# 顯示使用說明
show_usage() {
    cat << EOF

🎉 MCP Docker 環境設定完成！

下一步：
1. 配置 Claude Desktop：
   編輯 ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
   或 %APPDATA%/Claude/claude_desktop_config.json (Windows)

2. 基本配置範例：
   {
     "mcpServers": {
       "time": {
         "command": "docker",
         "args": ["exec", "-i", "time-mcp", "/app/server"]
       }
     }
   }

3. 測試 MCP 功能：
   在 Claude Desktop 中詢問：「現在幾點？」

4. 查看日誌：
   docker logs time-mcp

5. 停止服務：
   docker stop time-mcp

更多範例請參考：https://docs.docker.com/ai/mcp-catalog-and-toolkit/

EOF
}

# 主執行邏輯
main() {
    echo "🐳 MCP Docker 快速設定工具"
    echo "==============================="
    
    check_docker
    pull_images
    create_network
    start_basic_servers
    show_status
    show_usage
}

# 錯誤處理
trap 'log_error "腳本執行失敗"; exit 1' ERR

# 執行主函數
main "$@"
```

### Windows PowerShell 腳本

```powershell
# MCP Docker 快速啟動腳本 (Windows)

param(
    [string]$Action = "start"
)

# 顏色函數
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info($message) {
    Write-ColorOutput Blue "[INFO] $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "[SUCCESS] $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "[WARNING] $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "[ERROR] $message"
}

# 檢查 Docker
function Test-Docker {
    Write-Info "檢查 Docker 狀態..."
    try {
        docker info | Out-Null
        Write-Success "Docker 運行正常"
        return $true
    }
    catch {
        Write-Error "Docker 未運行或無法存取"
        Write-Info "請確保 Docker Desktop 已啟動"
        return $false
    }
}

# 拉取映像
function Get-MCPImages {
    Write-Info "拉取 MCP Docker 映像..."
    
    $images = @(
        "mcp/github",
        "mcp/time",
        "mcp/puppeteer", 
        "mcp/postgres"
    )
    
    foreach ($image in $images) {
        Write-Info "拉取 $image..."
        try {
            docker pull $image
            Write-Success "✓ $image 拉取成功"
        }
        catch {
            Write-Warning "✗ $image 拉取失敗"
        }
    }
}

# 啟動服務
function Start-MCPServers {
    Write-Info "啟動 MCP 服務器..."
    
    # 建立網路
    try {
        docker network create mcp-network --driver bridge 2>$null
        Write-Success "MCP 網路建立成功"
    }
    catch {
        Write-Warning "MCP 網路已存在"
    }
    
    # 啟動時間服務器
    try {
        docker run -d `
            --name time-mcp `
            --network mcp-network `
            --restart unless-stopped `
            --read-only `
            --security-opt no-new-privileges:true `
            --memory 128m `
            mcp/time
        Write-Success "時間服務器啟動成功"
    }
    catch {
        Write-Warning "時間服務器啟動失敗或已存在"
    }
}

# 顯示狀態
function Show-MCPStatus {
    Write-Info "MCP 服務器狀態："
    docker ps --filter "name=*-mcp" --format "table {{.Names}}\t{{.Status}}"
}

# 主邏輯
if (-not (Test-Docker)) {
    exit 1
}

switch ($Action) {
    "start" {
        Get-MCPImages
        Start-MCPServers
        Show-MCPStatus
        
        Write-Success "MCP Docker 環境設定完成！"
        Write-Info "配置檔案位置：$env:APPDATA\Claude\claude_desktop_config.json"
    }
    "stop" {
        Write-Info "停止 MCP 服務器..."
        docker stop $(docker ps -q --filter "name=*-mcp")
        Write-Success "MCP 服務器已停止"
    }
    "status" {
        Show-MCPStatus
    }
    default {
        Write-Info "用法: .\start-mcp.ps1 [-Action start|stop|status]"
    }
}
```

## 🛠️ 故障排除指南

### 常見問題解決方案

#### 1. 容器啟動失敗
```bash
# 檢查容器狀態
docker ps -a --filter "name=*-mcp"

# 查看容器日誌
docker logs container-name

# 檢查映像是否存在
docker images mcp/*
```

#### 2. 網路連接問題
```bash
# 檢查 MCP 網路
docker network ls | grep mcp

# 檢查容器網路配置
docker inspect container-name | grep -A 10 NetworkSettings
```

#### 3. 記憶體不足
```bash
# 檢查容器資源使用
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 調整記憶體限制
docker update --memory 512m container-name
```

## 📊 效能調優建議

### 1. 資源配置
- **時間服務器**: 128MB RAM, 0.2 CPU
- **GitHub 服務器**: 256MB RAM, 0.5 CPU  
- **Puppeteer 服務器**: 512MB-1GB RAM, 1.0 CPU
- **資料庫服務器**: 256MB-512MB RAM, 0.5 CPU

### 2. 網路最佳化
```bash
# 使用自定義網路提升效能
docker network create mcp-network \
  --driver bridge \
  --opt com.docker.network.bridge.name=mcp0 \
  --opt com.docker.network.driver.mtu=1500
```

### 3. 儲存最佳化
```bash
# 使用卷提升 I/O 效能
docker volume create mcp-cache
docker run -v mcp-cache:/app/cache mcp/your-server
```

## 🔐 安全最佳實踐

### 1. 容器安全配置
```bash
# 完整安全配置範例
docker run -d \
  --name secure-mcp \
  --read-only \
  --tmpfs /tmp \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=default \
  --cap-drop ALL \
  --user 1000:1000 \
  --memory 256m \
  --cpus 0.5 \
  --network mcp-network \
  mcp/your-server
```

### 2. 機密資料管理
```bash
# 使用 Docker Secrets (Swarm 模式)
echo "your-api-key" | docker secret create github-token -
docker service create \
  --secret github-token \
  --name github-mcp \
  mcp/github

# 使用環境檔案
echo "GITHUB_TOKEN=your-token" > .env
docker run --env-file .env mcp/github
```

### 3. 網路隔離
```bash
# 建立隔離網路
docker network create \
  --driver bridge \
  --internal \
  mcp-internal

# 僅允許特定通信
docker run --network mcp-internal mcp/your-server
```

這個實戰範例集提供了基於真實 Docker Hub 資料的完整 MCP Docker 使用方案，涵蓋從基礎配置到生產環境部署的所有場景。
