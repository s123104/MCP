# 🐳 MCP Docker 完整解決方案

[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blue)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基於真實 Docker Hub MCP Catalog 的完整 Model Context Protocol Docker 使用方案，包含自動化安裝、GUI 配置器和生產環境部署指南。

> **新手提示**：建議直接使用內建圖形化工具 `mcp_docker_configurator.py` 完成安裝與配置。以下流程將以 GUI 操作為核心說明。

## 🚀 快速開始

### 📋 系統需求

- **Python**: 3.8+ (推薦 3.10+)
- **Docker**: 20.10+ 或 Docker Desktop
- **作業系統**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **包管理器**: uv (推薦) 或 pip

### 🔧 環境準備

#### 1. 安裝 uv (推薦的 Python 包管理器)

```bash
# Linux/macOS - 使用 curl 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell - 使用 PowerShell 安裝 uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip 安裝
pip install uv

# 驗證安裝
uv --version
```

#### 2. 檢查 Python 版本

```bash
# 檢查 Python 版本
python --version
# 或
python3 --version

# 如果沒有 Python，使用 uv 安裝：
uv python install 3.11  # 安裝 Python 3.11

# 傳統安裝方式：
# Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv
# CentOS/RHEL: sudo yum install python3 python3-pip
# macOS: brew install python3
# Windows: 從 python.org 下載安裝包
```

#### 3. 檢查 Docker 狀態

```bash
# 檢查 Docker 是否安裝並運行
docker --version
docker info

# 如果沒有 Docker：
# Windows/macOS: 下載 Docker Desktop
# Linux: curl -fsSL https://get.docker.com | sh
```

#### 4. 啟動 GUI 配置器

```bash
python mcp_docker_configurator.py
```

啟動後依照介面選擇需要的 MCP 服務器並生成對應的設定檔，完成後即可依指示在本地端執行。

### ⚡ 一鍵自動安裝

#### Linux/macOS 快速安裝

```bash
# 方法 1: 使用 curl 下載並執行安裝腳本 (推薦)
# curl 會從 GitHub 下載安裝腳本並直接執行
curl -fsSL https://raw.githubusercontent.com/s123104/MCP/main/install-mcp-docker.sh | bash

# 方法 2: 手動下載執行
wget https://raw.githubusercontent.com/s123104/MCP/main/install-mcp-docker.sh
chmod +x install-mcp-docker.sh
./install-mcp-docker.sh
```

完成安裝後，執行：

```bash
python mcp_docker_configurator.py
```

即可透過 GUI 選擇並安裝所需服務。

#### Windows PowerShell 快速安裝

```powershell
# 以管理員身份執行 PowerShell
# 方法 1: 直接執行 (推薦)
iwr -useb https://raw.githubusercontent.com/s123104/MCP/main/install-mcp-docker.ps1 | iex

# 方法 2: 下載後執行
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/s123104/MCP/main/install-mcp-docker.ps1" -OutFile "install-mcp-docker.ps1"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install-mcp-docker.ps1
```

完成後在同一個 PowerShell 視窗執行：

```powershell
python mcp_docker_configurator.py
```

透過圖形介面即可完成服務安裝與配置。

### 🛠️ 手動安裝 (推薦開發者)

#### 步驟 1: 下載專案

```bash
# 使用 Git 克隆
git clone https://github.com/s123104/MCP.git
cd MCP

# 或下載 ZIP 檔案
# wget https://github.com/s123104/MCP/archive/main.zip
# unzip main.zip && cd MCP-main
```

#### 步驟 2: 建立虛擬環境 (使用 uv - 推薦)

**使用 uv (推薦 - 更快更現代):**

```bash
# 建立虛擬環境
uv venv mcp-docker-env

# 啟動虛擬環境
# Linux/macOS:
source mcp-docker-env/bin/activate

# Windows Command Prompt:
mcp-docker-env\Scripts\activate.bat

# Windows PowerShell:
mcp-docker-env\Scripts\Activate.ps1

# 確認虛擬環境已啟動 (提示符會顯示 (mcp-docker-env))
which python  # Linux/macOS
where python   # Windows
```

**使用傳統 venv (備選方案):**

```bash
# 建立虛擬環境
python3 -m venv mcp-docker-env

# 啟動虛擬環境
source mcp-docker-env/bin/activate  # Linux/macOS
# mcp-docker-env\Scripts\activate    # Windows

# 確認虛擬環境已啟動
which python
```

#### 步驟 3: 安裝 Python 依賴

**使用 uv (推薦):**

```bash
# 使用 uv 安裝依賴 (比 pip 快 10-100 倍)
uv pip install -r requirements.txt

# 或手動安裝核心依賴
uv pip install PyYAML requests docker

# 驗證安裝
python -c "import tkinter, yaml, requests, docker; print('所有依賴安裝成功！')"
```

**使用 pip (備選方案):**

```bash
# 確保 pip 是最新版本
python -m pip install --upgrade pip

# 安裝必要依賴
pip install -r requirements.txt

# 驗證安裝
python -c "import tkinter, yaml, requests, docker; print('所有依賴安裝成功！')"
```

#### 步驟 4: 執行安裝腳本

**Linux/macOS:**

```bash
# 給予執行權限
chmod +x install-mcp-docker.sh

# 執行安裝腳本
./install-mcp-docker.sh

# 或直接使用 bash
bash install-mcp-docker.sh
```

**Windows:**

```powershell
# PowerShell 執行
.\install-mcp-docker.ps1

# 或使用 Command Prompt
powershell -ExecutionPolicy Bypass -File install-mcp-docker.ps1
```

#### 步驟 5: 啟動 GUI 配置器

```bash
# 確保在虛擬環境中
# Linux/macOS: source mcp-docker-env/bin/activate
# Windows: mcp-docker-env\Scripts\activate

# 啟動進階 GUI 配置器 (推薦)
python mcp_docker_configurator.py

# 或啟動基礎安裝器
python mcp_installer_gui.py
```

### 🎯 MCP 服務選擇指南

#### 📋 服務分類和推薦

**🔥 熱門必備服務 (推薦新手):**

- `filesystem` - 檔案系統操作
- `github` - GitHub 整合
- `time` - 時間和日期工具
- `fetch` - 網路請求工具

**💾 資料庫服務:**

- `postgres` - PostgreSQL 資料庫
- `sqlite` - SQLite 輕量資料庫
- `memory` - 記憶體儲存

**🌐 網路和自動化:**

- `puppeteer` - 瀏覽器自動化
- `playwright` - 網頁測試
- `brave-search` - 搜尋引擎

**🛠️ 開發工具:**

- `git` - Git 版本控制
- `sequential-thinking` - 思維鏈工具
- `everything` - 多功能工具集

#### 🎮 互動式服務選擇

啟動 GUI 配置器後，您可以：

1. **瀏覽服務目錄** - 查看所有可用的 115+ MCP 服務
2. **分類篩選** - 按功能分類選擇服務
3. **搜尋功能** - 快速找到特定服務
4. **批量選擇** - 一次選擇多個相關服務
5. **預設組合** - 使用推薦的服務組合

```bash
# 啟動互動式配置器
python mcp_docker_configurator.py

# 在 GUI 中：
# 1. 選擇「❶ 選擇服務器」分頁
# 2. 使用分類下拉選單篩選
# 3. 雙擊服務名稱進行選擇
# 4. 配置環境變數 (如 API 金鑰)
# 5. 生成配置檔案
```

#### 📂 Filesystem 服務正確安裝

若選擇 `filesystem` 服務，建議使用以下安全化命令掛載需要存取的目錄，避免不必要的權限暴露:

```bash
 docker run -d 
  --name secure-mcp-filesystem 
  --read-only 
  --tmpfs /tmp:rw,noexec,nosuid,size=100m 
  --tmpfs /var/run:rw,noexec,nosuid,size=50m
  --security-opt no-new-privileges:true
  --security-opt seccomp=./config/seccomp-profiles/filesystem.json
  --security-opt apparmor=mcp-filesystem-profile
  --cap-drop ALL
  --cap-add CHOWN
  --cap-add DAC_OVERRIDE
  --user 1000:1000 
  --memory 256m 
  --cpus 0.5 
  --network none 
  -v "/path/to/allowed/dir:/workspace:ro,Z" 
  -e ALLOWED_PATHS="/workspace" 
  mcp/filesystem
```
上述指令會將 `/path/to/allowed/dir` 以唯讀模式掛載到容器的 `/workspace`，並限制容器資源及權限.

若使用 SSE/HTTP 部署，請將 `ALLOWED_PATHS` 環境變數設定為 `/workspace`，並依照 GUI 生成的 `docker-compose.yml` 配置對外暴露埠口。

完成配置後即可在本地或遠端安全地存取檔案。

#### 🛡️ 啟用 User Namespace 隔離

啟用 user namespace 可將容器內的 root 使用者映射到宿主機的非特權帳號。專案中
已提供 `config/docker/daemon.json` 範例設定，並需建立對應的 `subuid` 及
`subgid`：

```bash
sudo cp config/docker/daemon.json /etc/docker/daemon.json
echo 'mcpuser:100000:65536' | sudo tee /etc/subuid /etc/subgid
sudo systemctl restart docker
```

建立好 user namespace 後，建議以 Docker Volume 儲存工作目錄並設定正確的 UID/GID：

```bash
docker volume create \
  --driver local \
  --opt type=none \
  --opt o=bind,uid=100000,gid=100000 \
  --opt device=/var/lib/mcp/workspace \
  mcp-workspace
```

### 🔄 日常使用指令

#### 啟動/停止虛擬環境

```bash
# 啟動虛擬環境
# Linux/macOS:
source mcp-docker-env/bin/activate

# Windows Command Prompt:
mcp-docker-env\Scripts\activate.bat

# Windows PowerShell:
mcp-docker-env\Scripts\Activate.ps1

# 停用虛擬環境 (所有系統)
deactivate
```

#### 更新專案

```bash
# 進入專案目錄並啟動虛擬環境
cd MCP
source mcp-docker-env/bin/activate  # Linux/macOS
# mcp-docker-env\Scripts\activate    # Windows

# 更新程式碼
git pull origin main

# 更新依賴 (使用 uv)
uv pip install -r requirements.txt --upgrade

# 或使用 pip
pip install -r requirements.txt --upgrade

# 重新啟動配置器
python mcp_docker_configurator.py
```

### 🧪 快速測試指南

#### 環境測試

```bash
# 1. 測試 Python 環境
python --version
python -c "print('Python 環境正常')"

# 2. 測試虛擬環境
echo $VIRTUAL_ENV  # Linux/macOS (應顯示虛擬環境路徑)
echo %VIRTUAL_ENV%  # Windows

# 3. 測試依賴安裝
python -c "
import sys
try:
    import tkinter, yaml, requests, docker
    print('✅ 所有核心依賴已安裝')
except ImportError as e:
    print(f'❌ 缺少依賴: {e}')
    sys.exit(1)
"

# 4. 測試 Docker 連接
docker --version
docker run --rm hello-world

# 5. 測試 GUI 功能
python -c "
import tkinter as tk
try:
    root = tk.Tk()
    root.withdraw()  # 隱藏視窗
    root.destroy()
    print('✅ GUI 功能正常')
except Exception as e:
    print(f'❌ GUI 測試失敗: {e}')
"
```

#### 配置器功能測試

```bash
# 啟動配置器進行功能測試
python mcp_docker_configurator.py

# 測試步驟：
# 1. 檢查服務器列表是否載入
# 2. 選擇一個簡單的服務 (如 'time')
# 3. 生成 Claude Desktop 配置
# 4. 檢查配置預覽是否正確
# 5. 測試儲存配置功能
```

#### 一鍵完整測試腳本

```bash
# 建立測試腳本
cat > test_mcp_setup.sh << 'EOF'
#!/bin/bash
echo "🧪 開始 MCP Docker 環境測試..."

# 測試 Python
echo "1️⃣ 測試 Python 環境..."
python --version || { echo "❌ Python 未安裝"; exit 1; }

# 測試虛擬環境
echo "2️⃣ 測試虛擬環境..."
if [[ "$VIRTUAL_ENV" ]]; then
    echo "✅ 虛擬環境已啟動: $VIRTUAL_ENV"
else
    echo "⚠️ 虛擬環境未啟動，請執行: source mcp-docker-env/bin/activate"
fi

# 測試依賴
echo "3️⃣ 測試 Python 依賴..."
python -c "import tkinter, yaml, requests, docker; print('✅ 所有依賴正常')" || {
    echo "❌ 依賴測試失敗，請執行: uv pip install -r requirements.txt"
    exit 1
}

# 測試 Docker
echo "4️⃣ 測試 Docker..."
docker --version || { echo "❌ Docker 未安裝"; exit 1; }
docker info > /dev/null 2>&1 || { echo "❌ Docker 未運行"; exit 1; }

# 測試配置器
echo "5️⃣ 測試配置器..."
python -c "
import mcp_docker_configurator
print('✅ 配置器模組載入成功')
" || { echo "❌ 配置器測試失敗"; exit 1; }

echo "🎉 所有測試通過！可以開始使用 MCP Docker 配置器"
EOF

chmod +x test_mcp_setup.sh
./test_mcp_setup.sh
```

### 🚨 故障排除

#### Python 相關問題

```bash
# 如果 python3 命令不存在，嘗試：
python --version  # 檢查是否為 Python 3.x

# Ubuntu/Debian 安裝 Python 3
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk

# CentOS/RHEL 安裝 Python 3
sudo yum install python3 python3-pip python3-tkinter

# macOS 使用 Homebrew
brew install python3 python-tk

# 使用 uv 安裝 Python (推薦)
uv python install 3.11
```

#### uv 相關問題

```bash
# 如果 uv 安裝失敗，嘗試：
# 1. 使用 pip 安裝
pip install uv

# 2. 檢查 PATH 設定
echo $PATH | grep -q ".cargo/bin" || echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# 3. 重新載入 shell 配置
source ~/.bashrc  # Linux/macOS
# 重新開啟 PowerShell  # Windows

# 4. 驗證 uv 安裝
uv --version
```

#### 虛擬環境問題

```bash
# 如果 uv venv 建立失敗
uv python install 3.11  # 確保有 Python
uv venv mcp-docker-env --python 3.11

# 如果傳統 venv 建立失敗
python3 -m pip install --user virtualenv
python3 -m virtualenv mcp-docker-env

# Windows 執行策略問題
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 重新建立虛擬環境
rm -rf mcp-docker-env  # Linux/macOS
# rmdir /s mcp-docker-env  # Windows
uv venv mcp-docker-env
```

#### Docker 相關問題

```bash
# 檢查 Docker 服務狀態
sudo systemctl status docker  # Linux
# Docker Desktop 狀態檢查 (Windows/macOS)

# 重啟 Docker 服務
sudo systemctl restart docker  # Linux

# 檢查 Docker 權限
sudo usermod -aG docker $USER  # Linux
# 重新登入或執行: newgrp docker

# Windows Docker Desktop 問題
# 1. 確保 WSL2 已啟用
# 2. 檢查 Hyper-V 設定
# 3. 重啟 Docker Desktop
```

#### GUI 相關問題

```bash
# Linux 如果缺少 tkinter
sudo apt install python3-tk  # Ubuntu/Debian
sudo yum install tkinter      # CentOS/RHEL

# macOS 如果 tkinter 有問題
brew install python-tk

# Windows 如果 GUI 無法啟動
# 重新安裝 Python (確保勾選 tcl/tk 選項)
# 或使用 uv 重新安裝：
uv python install 3.11

# 測試 tkinter 是否正常
python -c "import tkinter; print('tkinter 正常')"
```

#### 網路和下載問題

```bash
# 如果 curl 下載失敗
# 1. 檢查網路連接
ping github.com

# 2. 使用代理 (如果需要)
export https_proxy=http://proxy.example.com:8080
curl -fsSL https://raw.githubusercontent.com/s123104/MCP/main/install-mcp-docker.sh

# 3. 手動下載
wget https://github.com/s123104/MCP/archive/main.zip
unzip main.zip

# 4. 使用 Git 克隆 (如果 curl 不可用)
git clone https://github.com/s123104/MCP.git
```

### 📱 快速驗證安裝

執行以下命令驗證安裝是否成功：

```bash
# 1. 檢查 Python 環境
python --version
uv --version  # 如果使用 uv

# 2. 檢查依賴
python -c "import tkinter, yaml, requests, docker; print('✅ 所有依賴正常')"

# 3. 檢查 Docker
docker --version
docker run --rm hello-world

# 4. 測試配置器
python -c "
try:
    import mcp_docker_configurator
    print('✅ 配置器模組正常')
except ImportError as e:
    print(f'❌ 配置器問題: {e}')
"

# 5. 啟動配置器
python mcp_docker_configurator.py
```

如果所有步驟都成功執行，您就可以開始使用 MCP Docker 配置器了！

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

| 服務器                                                    | 下載量 | 描述            | 用途               |
| --------------------------------------------------------- | ------ | --------------- | ------------------ |
| [mcp/github](https://hub.docker.com/r/mcp/github)         | 10K+   | GitHub API 工具 | 代碼管理、PR 操作  |
| [mcp/puppeteer](https://hub.docker.com/r/mcp/puppeteer)   | 10K+   | 瀏覽器自動化    | 網頁抓取、截圖     |
| [mcp/time](https://hub.docker.com/r/mcp/time)             | 10K+   | 時間工具        | 時區轉換、日期計算 |
| [mcp/postgres](https://hub.docker.com/r/mcp/postgres)     | 10K+   | PostgreSQL      | 資料庫查詢、分析   |
| [mcp/playwright](https://hub.docker.com/r/mcp/playwright) | 5K+    | 網頁測試        | E2E 測試、自動化   |

## 📖 使用指南

### 基礎配置範例

**Claude Desktop 配置** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--security-opt",
        "no-new-privileges",
        "-e",
        "GITHUB_TOKEN",
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
version: "3.8"
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

#### docker-compose.yml 安全範例

```yaml
version: "3.8"
services:
  filesystem:
    image: mcp/filesystem
    read_only: true
    security_opt:
      - no-new-privileges:true
      - seccomp:./config/seccomp-profiles/filesystem.json
      - apparmor:mcp-filesystem-profile
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
    user: "1000:1000"
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=100m
    volumes:
      - type: bind
        source: ./data/allowed
        target: /workspace
        read_only: true
        bind:
          propagation: rprivate
    environment:
      - ALLOWED_PATHS=/workspace
    networks:
      - mcp-backend

networks:
  mcp-frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
    driver_opts:
      com.docker.network.bridge.enable_icc: "false"
  mcp-backend:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/24
  mcp-data:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.22.0.0/24
```

#### 環境變數安全管理

```yaml
secrets:
  github_token:
    external: true

services:
  github:
    image: mcp/github
    secrets:
      - github_token
    environment:
      - GITHUB_TOKEN_FILE=/run/secrets/github_token
```

#### 密鑰初始化與輪換

使用 `scripts/init_secrets.sh` 建立 Docker secrets：

```bash
export GITHUB_TOKEN=your_token
export POSTGRES_URL=postgresql://user:pass@db:5432/dbname
export GRAFANA_PASSWORD=your_password
./scripts/init_secrets.sh
```

定期執行 `scripts/rotate_secrets.sh` 以輪換 GitHub Token：

```bash
export NEW_GITHUB_TOKEN=new_token_value
scripts/rotate_secrets.sh
```

#### 網路隔離與監控

```yaml
falco:
  image: falcosecurity/falco:latest
  privileged: true
  volumes:
    - /var/run/docker.sock:/host/var/run/docker.sock
    - /proc:/host/proc:ro
    - /boot:/host/boot:ro
    - /lib/modules:/host/lib/modules:ro
```

#### SSE/HTTP 模式設定

若需透過 SSE 或 HTTP 方式存取 MCP 服務，可在 GUI 生成的 `docker-compose.yml` 中調整 `ports` 與 `command` 參數。例如：

```yaml
services:
  filesystem:
    image: mcp/filesystem
    environment:
      - ALLOWED_PATHS=/workspace
    ports:
      - "8080:80"  # 對外提供 HTTP 介面
```

於瀏覽器或客戶端即可透過 `http://localhost:8080` 連接服務。

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

### 安全監控環境

```bash
# 部署安全監控與合規檢查
docker-compose -f docker-compose.security.yml up -d
```

啟動後可執行 `scripts/compliance_check.sh` 產生完整的合規性報告。

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

我們歡迎社群貢獻！請參考 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. **Fork 專案** - 建立您的功能分支
2. **提交變更** - 遵循 commit 訊息規範
3. **測試驗證** - 確保所有測試通過
4. **發起 PR** - 詳細描述變更內容

### 開發環境設定

```bash
# 設定開發環境
git clone https://github.com/s123104/mcp-docker.git
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

- **問題回報**: [GitHub Issues](https://github.com/s123104/mcp-docker/issues)
- **功能建議**: [GitHub Discussions](https://github.com/s123104/mcp-docker/discussions)
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
