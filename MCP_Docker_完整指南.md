# MCP Docker 完整使用指南

基於最新研究和官方文檔的詳細教學

## 目錄
1. [MCP Docker 概述](#mcp-docker-概述)
2. [Docker Hub MCP 使用方法](#docker-hub-mcp-使用方法)
3. [通信協定和端口配置](#通信協定和端口配置)
4. [安全隔離機制](#安全隔離機制)
5. [最佳實踐指南](#最佳實踐指南)
6. [配置檔案設定](#配置檔案設定)
7. [與傳統 MCP 的差異](#與傳統-mcp-的差異)

## MCP Docker 概述

### 什麼是 MCP Docker

Model Context Protocol (MCP) Docker 是 Docker 官方推出的全新解決方案，將 MCP 服務器容器化，解決了傳統 MCP 部署中的環境衝突、安全隱患和跨平台不一致問題。

**核心特色**：
- **Discovery**: 在 Docker Hub 上的中央化工具目錄
- **Credential Management**: OAuth 2.1 基礎的安全憑證管理
- **Execution**: 在隔離的容器化環境中運行工具
- **Portability**: 跨 Claude、Cursor、VS Code 等平台使用

### Docker MCP Catalog 和 Toolkit

Docker MCP 生態系統包含兩個核心組件：

#### 1. Docker MCP Catalog
- 位於 Docker Hub 的官方 MCP 工具目錄
- 超過 100 個經過驗證的 MCP 服務器
- 包含 Stripe、Elastic、Neo4j 等知名合作夥伴的工具
- 支援版本控制和發布者驗證

#### 2. Docker MCP Toolkit
- Docker Desktop 擴展
- 一鍵啟動 MCP 服務器
- 內建 OAuth 支援和安全憑證儲存
- 動態工具管理和閘道服務器

## Docker Hub MCP 使用方法

### 基本使用流程

#### 方法一：直接 Docker 命令
```bash
# 1. 拉取 MCP 容器映像
docker pull mcp/github

# 2. 運行容器 (STDIO 方式)
docker run -i --rm -e GITHUB_TOKEN=your_token mcp/github

# 3. 運行容器 (SSE 方式)
docker run -p 5008:5008 -e GITHUB_TOKEN=your_token mcp/github --transport sse
```

#### 方法二：使用 Docker Desktop MCP Toolkit
1. 安裝 Docker Desktop MCP Toolkit 擴展
2. 在擴展中搜尋和選擇 MCP 服務器
3. 一鍵啟用和配置
4. 自動處理憑證和連接

#### 方法三：Docker Compose
```yaml
version: '3.8'
services:
  github-mcp:
    image: mcp/github
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    stdin_open: true
    tty: true
    restart: unless-stopped
```

### 熱門 MCP 容器

| 容器名稱 | 用途 | 必要環境變數 |
|---------|------|-------------|
| `mcp/github` | GitHub 儲存庫管理 | `GITHUB_TOKEN` |
| `mcp/puppeteer` | 網頁自動化 | `DOCKER_CONTAINER=true` |
| `mcp/filesystem` | 檔案系統存取 | 無 |
| `mcp/slack` | Slack 整合 | `SLACK_BOT_TOKEN` |
| `mcp/postgres` | PostgreSQL 資料庫 | `POSTGRES_URL` |
| `mcp/stripe` | 支付處理 | `STRIPE_API_KEY` |
| `mcp/time` | 時間工具 | 無 |

## 通信協定和端口配置

### MCP 通信協定

MCP 支援兩種主要的通信方式：

#### 1. STDIO (標準輸入/輸出) - 推薦
- **協定**: JSON-RPC 2.0 over stdin/stdout
- **優點**: 無需網路端口，更安全
- **使用場景**: 本地開發，Claude Desktop 整合
- **命令**: `docker run -i --rm mcp/your-server`

#### 2. SSE (Server-Sent Events)
- **協定**: HTTP + Server-Sent Events
- **端口**: 通常為 5008 (可自定義)
- **優點**: 支援遠端連接
- **使用場景**: 遠端部署，網路服務
- **命令**: `docker run -p 5008:5008 mcp/your-server --transport sse`

### 端口配置範例

```bash
# 自定義端口
docker run -p 8080:8080 mcp/your-server --transport sse --port 8080

# 多個服務的端口分配
docker run -p 5008:5008 --name github-mcp mcp/github --transport sse
docker run -p 5009:5009 --name slack-mcp mcp/slack --transport sse
```

### 是否為 HTTP 協定？

- **STDIO 模式**: 不是 HTTP，使用 JSON-RPC 2.0
- **SSE 模式**: 是的，基於 HTTP 協定
- **WebSocket**: 未來可能支援，目前不是主要協定

## 安全隔離機制

### 為什麼需要容器隔離？

傳統 MCP 服務器直接在主機上運行，存在以下安全風險：
1. **主機檔案存取**: 可能存取敏感系統檔案
2. **環境污染**: 依賴項衝突和版本問題
3. **權限提升**: 可能獲得不必要的系統權限
4. **供應鏈攻擊**: 惡意 MCP 服務器的風險

### Docker 容器隔離機制

#### 1. 程序隔離
```bash
# 容器內程序無法直接存取主機程序
docker run --pid=host mcp/your-server  # 危險做法，避免使用
docker run mcp/your-server              # 安全做法，程序隔離
```

#### 2. 檔案系統隔離
```bash
# 唯讀根檔案系統
docker run --read-only --tmpfs /tmp mcp/github

# 限制檔案存取
docker run -v $(pwd)/data:/workspace:ro mcp/filesystem
```

#### 3. 網路隔離
```bash
# 無網路存取
docker run --network none mcp/time

# 自定義網路
docker network create mcp-network
docker run --network mcp-network mcp/github
```

#### 4. 資源限制
```bash
# 限制記憶體和 CPU
docker run --memory="512m" --cpus="1.0" mcp/puppeteer

# 限制磁碟空間
docker run --storage-opt size=1G mcp/filesystem
```

### 憑證安全管理

Docker MCP Toolkit 提供企業級憑證管理：

- **加密儲存**: 憑證經過加密儲存在 Docker Desktop
- **作用域限制**: 憑證只暴露給指定的容器
- **OAuth 2.1**: 支援現代 OAuth 標準
- **撤銷機制**: 可以隨時撤銷和更新憑證
- **審計日誌**: 記錄憑證使用情況

## 最佳實踐指南

### 1. 容器配置最佳實踐

```bash
# ✅ 推薦的安全配置
docker run \
  --rm \                              # 容器停止後自動刪除
  --read-only \                       # 唯讀根檔案系統
  --tmpfs /tmp \                      # 臨時檔案系統
  --memory="256m" \                   # 記憶體限制
  --cpus="0.5" \                      # CPU 限制
  --user 1000:1000 \                  # 非 root 使用者
  --security-opt no-new-privileges \  # 禁止權限提升
  -e GITHUB_TOKEN \                   # 環境變數
  mcp/github

# ❌ 不安全的配置
docker run --privileged -v /:/host mcp/github  # 避免使用
```

### 2. 環境變數管理

```bash
# ✅ 使用 .env 檔案
echo "GITHUB_TOKEN=your_token" > .env
docker run --env-file .env mcp/github

# ✅ 使用 Docker Secrets (Swarm 模式)
echo "your_token" | docker secret create github_token -
docker service create --secret github_token mcp/github

# ❌ 避免在命令列直接暴露
docker run -e GITHUB_TOKEN=ghp_xxx123 mcp/github  # 可能被記錄
```

### 3. 網路安全配置

```bash
# 建立專用網路
docker network create --driver bridge mcp-net

# 使用網路別名
docker run --network mcp-net --network-alias github mcp/github
docker run --network mcp-net --network-alias slack mcp/slack

# 網路分段隔離
docker network create --subnet=172.20.0.0/16 mcp-internal
```

### 4. 持久化資料管理

```bash
# 使用具名卷
docker volume create mcp-data
docker run -v mcp-data:/data mcp/filesystem

# 綁定掛載 (開發時使用)
docker run -v $(pwd)/workspace:/workspace mcp/filesystem

# 唯讀掛載
docker run -v $(pwd)/config:/config:ro mcp/your-server
```

## 配置檔案設定

### Claude Desktop 配置

**位置**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**基本配置**:
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    },
    "puppeteer": {
      "command": "docker", 
      "args": [
        "run", "-i", "--rm",
        "-e", "DOCKER_CONTAINER=true",
        "mcp/puppeteer"
      ]
    }
  }
}
```

**進階配置 (SSE 模式)**:
```json
{
  "mcpServers": {
    "github-remote": {
      "command": "docker",
      "args": [
        "run", "-d", "-p", "5008:5008",
        "-e", "GITHUB_TOKEN",
        "--name", "github-mcp",
        "mcp/github", "--transport", "sse"
      ],
      "env": {
        "GITHUB_TOKEN": "your_token"
      }
    }
  }
}
```

### VS Code 配置

**位置**: 專案根目錄的 `.vscode/mcp.json`

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github_token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ],
  "servers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
      }
    }
  }
}
```

### Cursor 配置

**位置**: Cursor 設定中的 MCP 區段

```json
{
  "mcp": {
    "servers": {
      "github": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "mcp/github"],
        "env": {
          "GITHUB_TOKEN": "your_token"
        }
      }
    }
  }
}
```

### Docker Compose 配置

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
    networks:
      - mcp-network
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

  slack-mcp:
    image: mcp/slack  
    container_name: slack-mcp
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
    stdin_open: true
    tty: true
    restart: unless-stopped
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  mcp-data:
    driver: local
```

## 與傳統 MCP 的差異

### 您的 GitHub 專案 (s123104/easy-mcp) vs Docker MCP

| 特性 | 傳統 MCP (easy-mcp) | Docker MCP |
|------|---------------------|------------|
| **部署方式** | 需要本地 Node.js/Python 環境 | 只需 Docker 即可運行 |
| **依賴管理** | 手動管理套件和版本衝突 | 容器自動處理所有依賴 |
| **安全隔離** | 直接在主機上運行 | 完全的容器隔離 |
| **跨平台支援** | 需要各平台環境配置 | Docker 統一標準 |
| **配置複雜度** | 需要深入了解 MCP 協定 | 通過 GUI 和預設配置簡化 |
| **擴展性** | 高度可客製化 | 標準化但可擴展 |
| **安全性** | 依賴開發者實作 | 企業級安全保證 |
| **社群支援** | 個人專案維護 | Docker 官方支援 |

### 何時選擇哪種方案？

#### 選擇傳統 MCP (如 easy-mcp) 的情況：
- 需要高度客製化的功能
- 對 MCP 協定有深入了解
- 開發新的 MCP 服務器
- 實驗性或研究項目

#### 選擇 Docker MCP 的情況：
- 生產環境部署
- 追求標準化和一致性
- 需要企業級安全和支援
- 跨團隊協作和工具共享
- 希望簡化運維和管理

## 快速啟動指南

### 1. 準備環境

```bash
# 檢查 Docker 安裝
docker --version
docker info

# 安裝 Docker Desktop MCP Toolkit
# 在 Docker Desktop > Extensions 中搜尋 "MCP Toolkit"
```

### 2. 第一個 MCP 服務器

```bash
# 下載並運行時間服務器
docker pull mcp/time
docker run -i --rm mcp/time

# 在另一個終端測試
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | docker run -i --rm mcp/time
```

### 3. 配置 Claude Desktop

```bash
# 編輯配置檔案
# macOS:
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Windows:
code %APPDATA%/Claude/claude_desktop_config.json

# 加入基本配置後重啟 Claude Desktop
```

### 4. 驗證配置

在 Claude Desktop 中測試：
```
現在幾點？
```

如果看到 MCP 工具被調用，表示配置成功！

## 故障排除

### 常見問題

1. **容器無法啟動**
   ```bash
   docker logs <container_name>
   docker inspect <container_name>
   ```

2. **權限錯誤**
   ```bash
   # 檢查 Docker 權限
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **網路連接問題**
   ```bash
   # 檢查防火牆設定
   docker run --rm -it alpine ping google.com
   ```

4. **憑證問題**
   - 檢查環境變數是否正確設定
   - 驗證 API 金鑰有效性
   - 確認權限範圍

## 相關資源

- **Docker MCP 官方文檔**: https://docs.docker.com/ai/mcp-catalog-and-toolkit/
- **Docker Hub MCP Catalog**: https://hub.docker.com/catalogs/mcp
- **MCP 協定規範**: https://modelcontextprotocol.io
- **Docker Desktop 下載**: https://www.docker.com/products/docker-desktop
- **GitHub 討論區**: https://github.com/docker/mcp-servers
