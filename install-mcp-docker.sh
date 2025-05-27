#!/bin/bash
# MCP Docker 自動安裝和配置腳本
# 支持 Linux 和 macOS
# 版本: 2.0
# 作者: MCP Docker Configurator

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 圖標定義
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
DOCKER="🐳"
GEAR="⚙️"

# 日誌函數
log_info() {
    echo -e "${BLUE}${INFO} [INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS} [SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} [WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR} [ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}${GEAR} [STEP]${NC} $1"
}

# 顯示橫幅
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
    ███╗   ███╗ ██████╗██████╗     ██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗ 
    ████╗ ████║██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    ██╔████╔██║██║     ██████╔╝    ██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝
    ██║╚██╔╝██║██║     ██╔═══╝     ██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║╚██████╗██║         ██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝     ╚═╝ ╚═════╝╚═╝         ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    
    Model Context Protocol Docker 自動安裝器 v2.0
    支援 Claude Desktop, VS Code, Cursor 自動配置
EOF
    echo -e "${NC}"
}

# 檢測作業系統
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    else
        log_error "不支援的作業系統: $OSTYPE"
        exit 1
    fi
    
    log_info "檢測到作業系統: $DISTRO ($OS)"
}

# 檢查依賴項
check_dependencies() {
    log_step "檢查系統依賴項..."
    
    local deps=("docker" "curl" "jq")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少必要依賴項: ${missing_deps[*]}"
        log_info "請先安裝缺少的依賴項："
        
        if [[ "$OS" == "macos" ]]; then
            echo "  brew install ${missing_deps[*]}"
        elif [[ "$OS" == "linux" ]]; then
            echo "  sudo apt-get install ${missing_deps[*]} (Ubuntu/Debian)"
            echo "  sudo yum install ${missing_deps[*]} (CentOS/RHEL)"
        fi
        exit 1
    fi
    
    log_success "所有依賴項已安裝"
}

# 檢查 Docker 狀態
check_docker() {
    log_step "檢查 Docker 狀態..."
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未運行或無法存取"
        log_info "請確保 Docker Desktop 已啟動並正在運行"
        
        if [[ "$OS" == "macos" ]]; then
            log_info "macOS: 請從應用程式資料夾啟動 Docker Desktop"
        elif [[ "$OS" == "linux" ]]; then
            log_info "Linux: 請執行 'sudo systemctl start docker'"
        fi
        exit 1
    fi
    
    # 獲取 Docker 版本資訊
    local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    log_success "Docker 運行正常 (版本: $docker_version)"
}

# MCP 服務器列表 (基於真實 Docker Hub 資料)
declare -A MCP_SERVERS=(
    ["github"]="mcp/github:GitHub API 工具和儲存庫管理:10000+"
    ["puppeteer"]="mcp/puppeteer:瀏覽器自動化和網頁抓取:10000+"
    ["time"]="mcp/time:時間和時區轉換功能:10000+"
    ["postgres"]="mcp/postgres:PostgreSQL 唯讀存取:10000+"
    ["playwright"]="mcp/playwright:Playwright 網頁自動化:5000+"
    ["sentry"]="mcp/sentry:Sentry.io 錯誤追蹤整合:1700+"
    ["filesystem"]="mcp/filesystem:本地檔案系統存取:1000+"
    ["sqlite"]="mcp/sqlite:SQLite 資料庫操作:1000+"
    ["slack"]="mcp/slack:Slack 工作區整合:800+"
    ["brave-search"]="mcp/brave-search:Brave 搜尋引擎 API:500+"
)

# 選擇 MCP 服務器
select_mcp_servers() {
    log_step "選擇要安裝的 MCP 服務器..."
    
    echo -e "\n${CYAN}可用的 MCP 服務器：${NC}"
    echo "=================================="
    
    local i=1
    local server_keys=()
    for server in "${!MCP_SERVERS[@]}"; do
        IFS=':' read -ra info <<< "${MCP_SERVERS[$server]}"
        local image="${info[0]}"
        local description="${info[1]}"
        local downloads="${info[2]}"
        
        printf "%2d) %-15s - %s (下載量: %s)\n" "$i" "$server" "$description" "$downloads"
        server_keys+=("$server")
        ((i++))
    done
    
    echo -e "\n輸入選項 (用空格分隔多個選項，例如: 1 2 3)："
    echo "或輸入 'all' 安裝所有服務器："
    read -r selection
    
    SELECTED_SERVERS=()
    if [[ "$selection" == "all" ]]; then
        SELECTED_SERVERS=("${server_keys[@]}")
    else
        for num in $selection; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#server_keys[@]}" ]; then
                SELECTED_SERVERS+=("${server_keys[$((num-1))]}")
            fi
        done
    fi
    
    if [ ${#SELECTED_SERVERS[@]} -eq 0 ]; then
        log_warning "未選擇任何服務器，將安裝基本服務器 (github, time, puppeteer)"
        SELECTED_SERVERS=("github" "time" "puppeteer")
    fi
    
    log_info "已選擇服務器: ${SELECTED_SERVERS[*]}"
}

# 拉取 Docker 映像
pull_docker_images() {
    log_step "拉取選定的 MCP Docker 映像..."
    
    local failed_images=()
    
    for server in "${SELECTED_SERVERS[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            IFS=':' read -ra info <<< "${MCP_SERVERS[$server]}"
            local image="${info[0]}"
            
            log_info "拉取 $image..."
            
            if docker pull "$image" >/dev/null 2>&1; then
                log_success "✓ $image 拉取成功"
            else
                log_error "✗ $image 拉取失敗"
                failed_images+=("$image")
            fi
        fi
    done
    
    if [ ${#failed_images[@]} -ne 0 ]; then
        log_warning "以下映像拉取失敗: ${failed_images[*]}"
        log_info "請檢查網路連接或映像名稱是否正確"
    fi
}

# 建立 Docker 網路
create_docker_network() {
    log_step "建立 MCP 專用 Docker 網路..."
    
    if docker network create mcp-network \
        --driver bridge \
        --subnet=172.20.0.0/16 \
        --opt com.docker.network.bridge.name=mcp0 >/dev/null 2>&1; then
        log_success "MCP 網路建立成功"
    else
        log_warning "MCP 網路已存在或建立失敗"
    fi
}

# 生成環境變數配置
generate_env_config() {
    log_step "配置環境變數..."
    
    # 建立 .env 檔案範本
    cat > mcp.env << 'EOF'
# MCP Docker 環境變數配置
# 請根據需要填入實際的 API 金鑰和配置

# GitHub 整合
GITHUB_TOKEN=your_github_personal_access_token_here

# PostgreSQL 資料庫 (如果需要)
POSTGRES_URL=postgresql://username:password@host:5432/database

# Slack 整合 (如果需要)
SLACK_BOT_TOKEN=your_slack_bot_token_here

# Brave Search API (如果需要)
BRAVE_API_KEY=your_brave_search_api_key_here

# Sentry 整合 (如果需要)
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ORG=your_sentry_org
SENTRY_PROJECT=your_sentry_project

# 其他配置
DOCKER_CONTAINER=true
EOF
    
    log_success "環境變數範本已建立: mcp.env"
    log_info "請編輯 mcp.env 檔案並填入實際的 API 金鑰"
}

# 生成 Claude Desktop 配置
generate_claude_config() {
    log_step "生成 Claude Desktop 配置..."
    
    # 確定配置檔案路徑
    if [[ "$OS" == "macos" ]]; then
        CONFIG_DIR="$HOME/Library/Application Support/Claude"
    elif [[ "$OS" == "linux" ]]; then
        CONFIG_DIR="$HOME/.config/Claude"
    fi
    
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    
    # 建立配置目錄
    mkdir -p "$CONFIG_DIR"
    
    # 生成配置內容
    cat > claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
EOF

    local first=true
    for server in "${SELECTED_SERVERS[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            IFS=':' read -ra info <<< "${MCP_SERVERS[$server]}"
            local image="${info[0]}"
            
            if [ "$first" = false ]; then
                echo "," >> claude_desktop_config.json
            fi
            first=false
            
            # 根據不同服務器生成不同配置
            case "$server" in
                "github")
                    cat >> claude_desktop_config.json << EOF
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "--memory", "256m",
        "-e", "GITHUB_TOKEN",
        "$image"
      ],
      "env": {
        "GITHUB_TOKEN": "填入您的 GitHub Token"
      }
    }
EOF
                    ;;
                "time")
                    cat >> claude_desktop_config.json << EOF
    "time": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges", 
        "--memory", "128m",
        "$image"
      ]
    }
EOF
                    ;;
                "puppeteer")
                    cat >> claude_desktop_config.json << EOF
    "puppeteer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--security-opt", "no-new-privileges",
        "--memory", "512m",
        "-e", "DOCKER_CONTAINER=true",
        "$image"
      ]
    }
EOF
                    ;;
                "postgres")
                    cat >> claude_desktop_config.json << EOF
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "--memory", "256m", 
        "-e", "POSTGRES_URL",
        "$image"
      ],
      "env": {
        "POSTGRES_URL": "填入您的 PostgreSQL 連接字串"
      }
    }
EOF
                    ;;
                *)
                    # 通用配置
                    cat >> claude_desktop_config.json << EOF
    "$server": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "--memory", "256m",
        "$image"
      ]
    }
EOF
                    ;;
            esac
        fi
    done

    cat >> claude_desktop_config.json << 'EOF'
  }
}
EOF

    log_success "Claude Desktop 配置已生成: claude_desktop_config.json"
    
    # 備份現有配置（如果存在）
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "現有配置已備份"
    fi
    
    log_info "配置檔案位置: $CONFIG_FILE"
    log_warning "請記得填入實際的 API 金鑰後重啟 Claude Desktop"
}

# 生成 VS Code 配置
generate_vscode_config() {
    log_step "生成 VS Code MCP 配置..."
    
    cat > mcp.json << 'EOF'
{
  "inputs": [
EOF

    # 生成輸入提示
    local first=true
    for server in "${SELECTED_SERVERS[@]}"; do
        case "$server" in
            "github")
                if [ "$first" = false ]; then
                    echo "," >> mcp.json
                fi
                first=false
                cat >> mcp.json << 'EOF'
    {
      "type": "promptString",
      "id": "github_token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
EOF
                ;;
            "postgres")
                if [ "$first" = false ]; then
                    echo "," >> mcp.json
                fi
                first=false
                cat >> mcp.json << 'EOF'
    {
      "type": "promptString", 
      "id": "postgres_url",
      "description": "PostgreSQL Connection URL",
      "password": true
    }
EOF
                ;;
        esac
    done

    cat >> mcp.json << 'EOF'
  ],
  "servers": {
EOF

    # 生成服務器配置
    first=true
    for server in "${SELECTED_SERVERS[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            IFS=':' read -ra info <<< "${MCP_SERVERS[$server]}"
            local image="${info[0]}"
            
            if [ "$first" = false ]; then
                echo "," >> mcp.json
            fi
            first=false
            
            case "$server" in
                "github")
                    cat >> mcp.json << EOF
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "-e", "GITHUB_TOKEN",
        "$image"
      ],
      "env": {
        "GITHUB_TOKEN": "\${input:github_token}"
      }
    }
EOF
                    ;;
                "postgres")
                    cat >> mcp.json << EOF
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "-e", "POSTGRES_URL", 
        "$image"
      ],
      "env": {
        "POSTGRES_URL": "\${input:postgres_url}"
      }
    }
EOF
                    ;;
                *)
                    cat >> mcp.json << EOF
    "$server": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only",
        "--security-opt", "no-new-privileges",
        "$image"
      ]
    }
EOF
                    ;;
            esac
        fi
    done

    cat >> mcp.json << 'EOF'
  }
}
EOF

    log_success "VS Code MCP 配置已生成: mcp.json"
    log_info "請將此檔案複製到您的 VS Code 專案的 .vscode/ 目錄中"
}

# 生成 Docker Compose 配置
generate_docker_compose() {
    log_step "生成 Docker Compose 配置..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
EOF

    for server in "${SELECTED_SERVERS[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            IFS=':' read -ra info <<< "${MCP_SERVERS[$server]}"
            local image="${info[0]}"
            
            cat >> docker-compose.yml << EOF

  ${server}-mcp:
    image: $image
    container_name: ${server}-mcp
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
      - "mcp.server=$server"
      - "mcp.type=automated"
EOF

            # 添加環境變數（如果需要）
            case "$server" in
                "github")
                    cat >> docker-compose.yml << 'EOF'
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
EOF
                    ;;
                "postgres")
                    cat >> docker-compose.yml << 'EOF'
    environment:
      - POSTGRES_URL=${POSTGRES_URL}
EOF
                    ;;
                "puppeteer")
                    cat >> docker-compose.yml << 'EOF'
    environment:
      - DOCKER_CONTAINER=true
EOF
                    ;;
            esac
        fi
    done

    cat >> docker-compose.yml << 'EOF'

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
EOF

    log_success "Docker Compose 配置已生成: docker-compose.yml"
}

# 生成管理腳本
generate_management_scripts() {
    log_step "生成管理腳本..."
    
    # MCP 管理腳本
    cat > mcp-manager.sh << 'EOF'
#!/bin/bash
# MCP Docker 管理腳本

COMPOSE_FILE="docker-compose.yml"

case "$1" in
    start)
        echo "🚀 啟動 MCP 服務器..."
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    stop)
        echo "🛑 停止 MCP 服務器..."
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    restart)
        echo "🔄 重啟 MCP 服務器..."
        docker-compose -f "$COMPOSE_FILE" restart
        ;;
    status)
        echo "📊 MCP 服務器狀態："
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    logs)
        if [ -z "$2" ]; then
            docker-compose -f "$COMPOSE_FILE" logs -f
        else
            docker-compose -f "$COMPOSE_FILE" logs -f "$2"
        fi
        ;;
    update)
        echo "📥 更新 MCP 映像..."
        docker-compose -f "$COMPOSE_FILE" pull
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    clean)
        echo "🧹 清理未使用的 Docker 資源..."
        docker system prune -f
        docker image prune -f
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs [service]|update|clean}"
        echo ""
        echo "命令說明："
        echo "  start   - 啟動所有 MCP 服務器"
        echo "  stop    - 停止所有 MCP 服務器"
        echo "  restart - 重啟所有 MCP 服務器"
        echo "  status  - 顯示服務器狀態"
        echo "  logs    - 顯示日誌 (可指定服務名稱)"
        echo "  update  - 更新映像並重啟"
        echo "  clean   - 清理未使用的 Docker 資源"
        exit 1
        ;;
esac
EOF

    chmod +x mcp-manager.sh
    log_success "管理腳本已生成: mcp-manager.sh"
    
    # 健康檢查腳本
    cat > mcp-health-check.sh << 'EOF'
#!/bin/bash
# MCP 健康檢查腳本

echo "🏥 MCP 健康檢查報告"
echo "===================="

# 檢查 Docker 狀態
if docker info >/dev/null 2>&1; then
    echo "✅ Docker 運行正常"
else
    echo "❌ Docker 未運行"
    exit 1
fi

# 檢查 MCP 容器狀態
echo -e "\n📦 MCP 容器狀態："
docker ps --filter "label=mcp.type=automated" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 檢查資源使用
echo -e "\n📊 資源使用情況："
docker stats --no-stream --filter "label=mcp.type=automated" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 檢查網路連接
echo -e "\n🌐 網路狀態："
docker network ls | grep mcp

echo -e "\n✅ 健康檢查完成"
EOF

    chmod +x mcp-health-check.sh
    log_success "健康檢查腳本已生成: mcp-health-check.sh"
}

# 顯示安裝摘要
show_installation_summary() {
    echo -e "\n${GREEN}${SUCCESS}=================================="
    echo -e "  MCP Docker 安裝完成！"
    echo -e "==================================${NC}\n"
    
    echo -e "${CYAN}📋 安裝摘要：${NC}"
    echo "• 已安裝 MCP 服務器: ${SELECTED_SERVERS[*]}"
    echo "• 已建立 Docker 網路: mcp-network"
    echo "• 已生成配置檔案："
    echo "  - claude_desktop_config.json (Claude Desktop)"
    echo "  - mcp.json (VS Code)" 
    echo "  - docker-compose.yml (Docker Compose)"
    echo "  - mcp.env (環境變數範本)"
    echo "• 已生成管理腳本："
    echo "  - mcp-manager.sh (服務管理)"
    echo "  - mcp-health-check.sh (健康檢查)"
    
    echo -e "\n${CYAN}📝 下一步：${NC}"
    echo "1. 編輯 mcp.env 檔案並填入實際的 API 金鑰"
    echo "2. 將 claude_desktop_config.json 複製到 Claude Desktop 配置目錄"
    
    if [[ "$OS" == "macos" ]]; then
        echo "   macOS: ~/Library/Application Support/Claude/"
    elif [[ "$OS" == "linux" ]]; then
        echo "   Linux: ~/.config/Claude/"
    fi
    
    echo "3. 重啟 Claude Desktop"
    echo "4. 測試 MCP 功能 (例如詢問「現在幾點？」)"
    
    echo -e "\n${CYAN}🛠️ 管理命令：${NC}"
    echo "• 啟動服務: ./mcp-manager.sh start"
    echo "• 檢查狀態: ./mcp-manager.sh status"
    echo "• 查看日誌: ./mcp-manager.sh logs"
    echo "• 健康檢查: ./mcp-health-check.sh"
    
    echo -e "\n${CYAN}📚 更多資源：${NC}"
    echo "• Docker MCP 官方文檔: https://docs.docker.com/ai/mcp-catalog-and-toolkit/"
    echo "• MCP 協定規範: https://modelcontextprotocol.io"
    echo "• GitHub 討論區: https://github.com/docker/mcp-servers"
    
    echo -e "\n${GREEN}🎉 安裝完成！開始享受 MCP Docker 的強大功能！${NC}\n"
}

# 主執行函數
main() {
    show_banner
    detect_os
    check_dependencies
    check_docker
    select_mcp_servers
    pull_docker_images
    create_docker_network
    generate_env_config
    generate_claude_config
    generate_vscode_config
    generate_docker_compose
    generate_management_scripts
    show_installation_summary
}

# 錯誤處理
trap 'log_error "腳本執行過程中發生錯誤"; exit 1' ERR

# 執行主函數
main "$@"
