# 🚀 MCP Docker 快速開始指南

這是一個 5 分鐘的快速上手指南，讓您立即開始使用 MCP Docker。

## 🎯 目標

在 5 分鐘內：
- ✅ 安裝和配置 MCP Docker 環境
- ✅ 啟動基本的 MCP 服務器
- ✅ 在 Claude Desktop 中測試 MCP 功能

## 📋 前置需求

- ✅ Docker Desktop 已安裝並運行
- ✅ 系統支援 bash 腳本 (Linux/macOS) 或 PowerShell (Windows)
- ✅ 具備基本的命令列操作能力

## ⚡ 超快速安裝 (1 分鐘)

### 選項 1: 一鍵自動安裝

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/mcp-docker/main/install-mcp-docker.sh | bash
```

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/your-repo/mcp-docker/main/install-mcp-docker.ps1 | iex
```

### 選項 2: 手動克隆安裝

```bash
# 1. 克隆專案
git clone https://github.com/your-repo/mcp-docker.git
cd mcp-docker

# 2. 執行安裝腳本
chmod +x install-mcp-docker.sh
./install-mcp-docker.sh

# Windows 用戶使用 PowerShell
# .\install-mcp-docker.ps1
```

## 🔧 基礎配置 (2 分鐘)

### 1. 設定環境變數

複製範例檔案並編輯：
```bash
cp .env.example .env
nano .env  # 或使用您喜歡的編輯器
```

**最基本的配置 (僅需填入一項):**
```bash
# GitHub 整合 (推薦 - 功能最豐富)
GITHUB_TOKEN=your_github_token_here
```

**如何獲得 GitHub Token:**
1. 訪問 https://github.com/settings/tokens
2. 點擊 "Generate new token (classic)"
3. 選擇權限: `repo`, `read:org`, `read:user`
4. 複製生成的 token 到 `.env` 檔案

### 2. 啟動基礎服務

```bash
# 使用管理腳本啟動
./mcp-manager-advanced.sh start

# 或直接使用 Docker Compose
docker-compose up -d
```

### 3. 驗證服務狀態

```bash
# 檢查服務狀態
./mcp-manager-advanced.sh status

# 檢查健康狀況
./mcp-manager-advanced.sh health
```

## 🤖 Claude Desktop 設定 (2 分鐘)

### 1. 找到配置檔案位置

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. 應用配置

複製生成的配置檔案：
```bash
# 配置檔案已在安裝過程中生成
cp claude_desktop_config.json "$HOME/Library/Application Support/Claude/"  # macOS
cp claude_desktop_config.json "$APPDATA/Claude/"  # Windows
```

或者手動複製以下基礎配置：
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

### 3. 重啟 Claude Desktop

完全關閉並重新啟動 Claude Desktop 應用程式。

## 🧪 測試 MCP 功能 (30 秒)

在 Claude Desktop 中嘗試以下測試：

### 1. 測試時間功能
```
現在幾點？
```

### 2. 測試 GitHub 功能 (如果已配置)
```
幫我查看我的 GitHub 儲存庫列表
```

### 3. 測試複合功能
```
幫我檢查我最新的 GitHub 提交是什麼時候？
```

如果看到 Claude 調用 MCP 工具並返回結果，恭喜您已成功設定！

## 🔍 故障排除

### 問題 1: Docker 容器無法啟動
```bash
# 檢查 Docker 狀態
docker info

# 檢查容器日誌
docker logs github-mcp
```

### 問題 2: Claude Desktop 無法識別 MCP
1. 檢查配置檔案語法：
   ```bash
   cat claude_desktop_config.json | jq .
   ```
2. 確認配置檔案路徑正確
3. 完全重啟 Claude Desktop

### 問題 3: GitHub Token 無效
1. 檢查 token 權限是否足夠
2. 確認 token 未過期
3. 重新生成 token

## 🚀 下一步進階功能

現在您已經有了基本的 MCP Docker 環境，可以探索更多功能：

### 1. 添加更多服務器
```bash
# 使用 GUI 配置器
python mcp_docker_configurator.py

# 或編輯 docker-compose.yml 添加更多服務
```

### 2. 啟用監控和日誌
```bash
# 啟動生產環境 (包含監控)
docker-compose -f docker-compose.prod.yml up -d

# 訪問 Grafana 儀表板
open http://localhost:3000
```

### 3. 探索進階功能
- 查看 [完整使用指南](MCP_Docker_完整指南.md)
- 瀏覽 [實戰範例](MCP_Docker_實戰範例.md)
- 使用 [GUI 配置器](mcp_docker_configurator.py)

## 📚 快速參考

### 常用命令
```bash
# 啟動服務
./mcp-manager-advanced.sh start

# 檢查狀態
./mcp-manager-advanced.sh status

# 查看日誌
./mcp-manager-advanced.sh logs

# 停止服務
./mcp-manager-advanced.sh stop

# 健康檢查
./mcp-manager-advanced.sh health

# 更新映像
./mcp-manager-advanced.sh update
```

### 配置檔案位置
- 環境變數: `.env`
- Docker Compose: `docker-compose.yml`
- Claude Desktop: 見上述平台特定路徑
- VS Code: `.vscode/mcp.json`

### 重要連結
- [MCP 官方文檔](https://modelcontextprotocol.io)
- [Docker Hub MCP Catalog](https://hub.docker.com/catalogs/mcp)
- [Claude Desktop](https://claude.ai/desktop)

## 🎉 完成！

您現在擁有一個完全運行的 MCP Docker 環境！

**🎯 達成成就:**
- ✅ MCP Docker 環境已設置
- ✅ 基礎服務器正在運行
- ✅ Claude Desktop 已連接
- ✅ MCP 功能測試通過

**🚀 接下來可以:**
- 探索更多 MCP 服務器
- 自定義配置和安全設定
- 部署到生產環境
- 與團隊分享配置

如果遇到任何問題，請查看詳細的故障排除指南或在 GitHub 提出 issue。

---

**💡 小提示:** 將此專案加入書籤，並定期運行 `./mcp-manager-advanced.sh update` 以獲得最新的 MCP 服務器功能！
