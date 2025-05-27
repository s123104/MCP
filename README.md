# 🐳 MCP Docker 完整解決方案

[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blue)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基於真實 Docker Hub MCP Catalog 的完整 Model Context Protocol Docker 使用方案，包含自動化安裝、GUI 配置器和生產環境部署指南。

## 🚀 快速開始

### 一鍵自動安裝

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/mcp-docker/main/install-mcp-docker.sh | bash
```

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/your-repo/mcp-docker/main/install-mcp-docker.ps1 | iex
```

### 手動安裝

1. **下載專案**
   ```bash
   git clone https://github.com/your-repo/mcp-docker.git
   cd mcp-docker
   ```

2. **執行安裝腳本**
   ```bash
   # Linux/macOS
   chmod +x install-mcp-docker.sh
   ./install-mcp-docker.sh
   
   # Windows
   .\install-mcp-docker.ps1
   ```

3. **啟動 GUI 配置器**
   ```bash
   python mcp_docker_configurator.py
   ```

## 📁 專案結構

```
MCP/
├── 📚 文檔指南
│   ├── MCP_Docker_完整指南.md          # 完整使用指南和最佳實踐
│   ├── MCP_Docker_完整使用指南.md      # 詳細配置說明
│   └── MCP_Docker_實戰範例.md          # 真實場景使用範例
│
├── 🛠️ 安裝工具
│   ├── install-mcp-docker.sh          # Linux/macOS 自動安裝腳本
│   └── install-mcp-docker.ps1         # Windows PowerShell 安裝腳本
│
├── 🖥️ GUI 工具
│   ├── mcp_docker_configurator.py     # 進階 GUI 配置器 (推薦)
│   └── mcp_installer_gui.py           # 基礎 GUI 安裝器
│
└── 📄 README.md                       # 專案說明 (本檔案)
```

## 🎯 主要特色

### ✨ 完整生態支援
- **115+ 官方 MCP 服務器** - 基於真實 Docker Hub Catalog
- **多平台配置** - Claude Desktop、VS Code、Cursor、Docker Compose
- **自動化部署** - 一鍵安裝和配置所有組件
- **GUI 配置器** - 直觀的圖形化配置界面

### 🔒 企業級安全
- **容器隔離** - 完全沙箱化運行環境
- **權限控制** - 最小權限原則和安全配置
- **憑證管理** - 加密儲存和作用域限制
- **網路隔離** - 專用網路和防火牆配置

### 🚀 生產就緒
- **健康檢查** - 自動監控和故障檢測
- **資源限制** - CPU、記憶體和磁碟控制
- **日誌管理** - 結構化日誌和監控
- **高可用性** - 重啟策略和故障轉移

## 🔥 熱門 MCP 服務器

基於 Docker Hub 下載量統計的最受歡迎服務器：

| 服務器 | 下載量 | 描述 | 用途 |
|--------|--------|------|------|
| [mcp/github](https://hub.docker.com/r/mcp/github) | 10K+ | GitHub API 工具 | 代碼管理、PR 操作 |
| [mcp/puppeteer](https://hub.docker.com/r/mcp/puppeteer) | 10K+ | 瀏覽器自動化 | 網頁抓取、截圖 |
| [mcp/time](https://hub.docker.com/r/mcp/time) | 10K+ | 時間工具 | 時區轉換、日期計算 |
| [mcp/postgres](https://hub.docker.com/r/mcp/postgres) | 10K+ | PostgreSQL | 資料庫查詢、分析 |
| [mcp/playwright](https://hub.docker.com/r/mcp/playwright) | 5K+ | 網頁測試 | E2E 測試、自動化 |

## 📖 使用指南

### 基礎配置範例

**Claude Desktop 配置** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--security-opt", "no-new-privileges",
        "-e", "GITHUB_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    },
    "time": {
      "command": "docker", 
      "args": ["run", "-i", "--rm", "mcp/time"]
    }
  }
}
```

**Docker Compose 配置** (`docker-compose.yml`):
```yaml
version: '3.8'
services:
  github-mcp:
    image: mcp/github
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    security_opt:
      - no-new-privileges:true
    read_only: true
    mem_limit: 256m
    
  time-mcp:
    image: mcp/time
    read_only: true
    mem_limit: 128m
```

### GUI 配置器使用

1. **啟動配置器**
   ```bash
   python mcp_docker_configurator.py
   ```

2. **選擇服務器** - 在「服務器選擇」分頁選擇需要的 MCP 服務器

3. **配置環境變數** - 填入 API 金鑰和認證資訊

4. **選擇平台** - 選擇 Claude Desktop、VS Code 或 Cursor

5. **生成配置** - 一鍵生成所有平台的配置檔案

6. **自動安裝** - 可選自動下載和安裝 Docker 映像

## 🛠️ 進階功能

### 自動化腳本

安裝腳本提供完整的自動化功能：

- ✅ **系統檢查** - Docker、依賴項、權限驗證
- ✅ **映像管理** - 自動拉取、更新、清理
- ✅ **網路配置** - 專用網路和安全設定
- ✅ **配置生成** - 多平台配置檔案
- ✅ **健康監控** - 狀態檢查和日誌管理

### 管理命令

```bash
# 啟動所有服務
./mcp-manager.sh start

# 檢查服務狀態
./mcp-manager.sh status

# 查看服務日誌
./mcp-manager.sh logs [service_name]

# 更新所有映像
./mcp-manager.sh update

# 健康檢查
./mcp-health-check.sh
```

### 安全最佳實踐

```bash
# 完整安全配置範例
docker run -d \
  --name secure-mcp \
  --read-only \
  --tmpfs /tmp \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --user 1000:1000 \
  --memory 256m \
  --cpus 0.5 \
  --network mcp-network \
  mcp/your-server
```

## 🔧 配置檔案位置

### Claude Desktop
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### VS Code
- **專案配置**: `.vscode/mcp.json`
- **全域配置**: VS Code 設定 > MCP 區段

### Cursor
- **配置位置**: Cursor 設定 > MCP 整合區域

## 🚀 部署方案

### 開發環境
```bash
# 基礎開發設定
docker-compose -f docker-compose.dev.yml up -d
```

### 測試環境
```bash
# 包含測試工具的完整環境
docker-compose -f docker-compose.test.yml up -d
```

### 生產環境
```bash
# 高可用性和監控配置
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 效能監控

### 資源使用統計
```bash
# 查看容器資源使用
docker stats --filter "label=mcp.type=automated"

# 查看網路流量
docker exec -it mcp-monitor iftop

# 查看磁碟使用
docker system df
```

### 日誌分析
```bash
# 結構化日誌查詢
docker logs mcp-server | jq '.level="info"'

# 錯誤日誌監控
docker logs mcp-server | grep ERROR

# 效能指標收集
docker logs mcp-server | grep -E "(response_time|cpu_usage)"
```

## 🔍 故障排除

### 常見問題

#### Docker 相關
```bash
# 檢查 Docker 狀態
docker info

# 重啟 Docker 服務 (Linux)
sudo systemctl restart docker

# 清理 Docker 資源
docker system prune -f
```

#### 配置相關
```bash
# 驗證 JSON 配置語法
cat claude_desktop_config.json | jq .

# 檢查環境變數
printenv | grep -E "(GITHUB|SLACK|POSTGRES)"

# 測試網路連接
docker run --rm -it alpine ping google.com
```

#### 容器相關
```bash
# 查看容器日誌
docker logs container-name

# 進入容器調試
docker exec -it container-name /bin/sh

# 檢查容器狀態
docker inspect container-name
```

## 🤝 貢獻指南

我們歡迎社群貢獻！請參考以下指南：

1. **Fork 專案** - 建立您的功能分支
2. **提交變更** - 遵循 commit 訊息規範
3. **測試驗證** - 確保所有測試通過
4. **發起 PR** - 詳細描述變更內容

### 開發環境設定

```bash
# 設定開發環境
git clone https://github.com/your-repo/mcp-docker.git
cd mcp-docker

# 安裝依賴項
pip install -r requirements.txt

# 運行測試
python -m pytest tests/

# 啟動開發模式
python mcp_docker_configurator.py --dev
```

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🔗 相關資源

### 官方文檔
- [Model Context Protocol 規範](https://modelcontextprotocol.io)
- [Docker MCP Catalog](https://hub.docker.com/catalogs/mcp)
- [Docker MCP 官方文檔](https://docs.docker.com/ai/mcp-catalog-and-toolkit/)

### 社群資源
- [MCP GitHub 討論區](https://github.com/docker/mcp-servers)
- [Docker 官方部落格](https://www.docker.com/blog/introducing-docker-mcp-catalog-and-toolkit/)
- [Anthropic Claude 文檔](https://docs.anthropic.com/claude/docs)

### 開發工具
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code MCP 擴展](https://marketplace.visualstudio.com/items?itemName=mcp)

## 📞 支援與回饋

- **問題回報**: [GitHub Issues](https://github.com/your-repo/mcp-docker/issues)
- **功能建議**: [GitHub Discussions](https://github.com/your-repo/mcp-docker/discussions)
- **技術支援**: [Discord 社群](https://discord.gg/mcp-docker)

## 🎉 致謝

特別感謝以下專案和團隊：

- [Anthropic](https://anthropic.com) - MCP 協定設計和實作
- [Docker](https://docker.com) - 容器化平台和 MCP Toolkit
- [社群貢獻者](CONTRIBUTORS.md) - 所有參與開發的開發者們

---

<div align="center">

**🚀 開始使用 MCP Docker，讓 AI 代理更強大！**

[立即安裝](#快速開始) • [查看範例](MCP_Docker_實戰範例.md) • [完整指南](MCP_Docker_完整指南.md)

</div>
