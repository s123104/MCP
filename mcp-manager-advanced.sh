#!/bin/bash
# MCP Docker 綜合管理腳本
# 版本: 2.1
# 提供完整的 MCP 服務器管理功能

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 圖標定義
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
DOCKER="🐳"
GEAR="⚙️"
CHART="📊"
LOG="📝"
HEALTH="🏥"

# 配置檔案
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
CONFIG_DIR="./config"
LOGS_DIR="./logs"
BACKUP_DIR="./backups"

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

# 顯示說明
show_help() {
    cat << EOF
${CYAN}${DOCKER} MCP Docker 管理腳本 v2.1${NC}

${YELLOW}用法:${NC}
  $0 <命令> [選項]

${YELLOW}主要命令:${NC}
  ${GREEN}start${NC}           啟動 MCP 服務器
  ${GREEN}stop${NC}            停止 MCP 服務器
  ${GREEN}restart${NC}         重啟 MCP 服務器
  ${GREEN}status${NC}          顯示服務器狀態
  ${GREEN}logs${NC}            查看服務日誌
  ${GREEN}health${NC}          執行健康檢查
  ${GREEN}update${NC}          更新 Docker 映像
  ${GREEN}backup${NC}          備份配置和資料
  ${GREEN}restore${NC}         還原備份
  ${GREEN}clean${NC}           清理系統資源
  ${GREEN}monitor${NC}         即時監控
  ${GREEN}install${NC}         安裝新的 MCP 服務器
  ${GREEN}remove${NC}          移除 MCP 服務器

${YELLOW}維護命令:${NC}
  ${GREEN}setup${NC}           初始化 MCP 環境
  ${GREEN}config${NC}          配置管理
  ${GREEN}security${NC}        安全檢查
  ${GREEN}performance${NC}     效能分析
  ${GREEN}export${NC}          匯出配置
  ${GREEN}import${NC}          匯入配置

${YELLOW}選項:${NC}
  -f, --file      指定 Docker Compose 檔案
  -e, --env       指定環境檔案
  -v, --verbose   詳細輸出
  -q, --quiet     安靜模式
  -h, --help      顯示此說明

${YELLOW}範例:${NC}
  $0 start                     # 啟動所有服務
  $0 logs github               # 查看 GitHub 服務日誌
  $0 status --verbose          # 詳細狀態資訊
  $0 backup --file backup.tar  # 建立備份
  $0 monitor --interval 5      # 每 5 秒監控一次

${YELLOW}更多資訊:${NC}
  使用 '$0 <命令> --help' 獲取特定命令的說明
EOF
}

# 檢查依賴項
check_dependencies() {
    local deps=("docker" "docker-compose" "jq" "curl")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "缺少依賴項: ${missing[*]}"
        log_info "請安裝缺少的依賴項後重試"
        exit 1
    fi
}

# 檢查 Docker 狀態
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未運行或無法存取"
        log_info "請確保 Docker Desktop 已啟動"
        exit 1
    fi
}

# 載入環境變數
load_env() {
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
        log_info "已載入環境變數檔案: $ENV_FILE"
    else
        log_warning "環境變數檔案不存在: $ENV_FILE"
    fi
}

# 啟動服務
start_services() {
    log_step "啟動 MCP 服務器..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose 檔案不存在: $COMPOSE_FILE"
        exit 1
    fi
    
    docker-compose -f "$COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        log_success "MCP 服務器啟動成功"
        sleep 2
        show_status
    else
        log_error "MCP 服務器啟動失敗"
        exit 1
    fi
}

# 停止服務
stop_services() {
    log_step "停止 MCP 服務器..."
    
    docker-compose -f "$COMPOSE_FILE" down
    
    if [ $? -eq 0 ]; then
        log_success "MCP 服務器已停止"
    else
        log_error "停止服務器時發生錯誤"
        exit 1
    fi
}

# 重啟服務
restart_services() {
    log_step "重啟 MCP 服務器..."
    
    docker-compose -f "$COMPOSE_FILE" restart
    
    if [ $? -eq 0 ]; then
        log_success "MCP 服務器重啟完成"
        sleep 2
        show_status
    else
        log_error "重啟服務器時發生錯誤"
        exit 1
    fi
}

# 顯示狀態
show_status() {
    echo -e "\n${CYAN}${CHART} MCP 服務器狀態${NC}"
    echo "=============================="
    
    # 容器狀態
    docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
    
    # 資源使用情況
    echo -e "\n${CYAN}${CHART} 資源使用情況${NC}"
    echo "=============================="
    docker stats --no-stream --filter "label=mcp.type" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    # 網路資訊
    echo -e "\n${CYAN}${CHART} 網路資訊${NC}"
    echo "=============================="
    docker network ls | grep mcp
}

# 查看日誌
show_logs() {
    local service="$1"
    local follow="${2:-false}"
    
    if [ -z "$service" ]; then
        log_step "顯示所有服務日誌..."
        if [ "$follow" = "true" ]; then
            docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
        else
            docker-compose -f "$COMPOSE_FILE" logs --tail=100
        fi
    else
        log_step "顯示 $service 服務日誌..."
        if [ "$follow" = "true" ]; then
            docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
        else
            docker-compose -f "$COMPOSE_FILE" logs --tail=100 "$service"
        fi
    fi
}

# 健康檢查
health_check() {
    echo -e "\n${CYAN}${HEALTH} MCP 健康檢查報告${NC}"
    echo "=============================="
    
    # Docker 狀態
    if docker info >/dev/null 2>&1; then
        echo -e "${SUCCESS} Docker 運行正常"
    else
        echo -e "${ERROR} Docker 未運行"
        return 1
    fi
    
    # 容器健康狀態
    echo -e "\n${CYAN}容器健康狀態:${NC}"
    local containers=$(docker-compose -f "$COMPOSE_FILE" ps -q)
    
    if [ -z "$containers" ]; then
        echo -e "${WARNING} 沒有運行中的容器"
        return 0
    fi
    
    for container in $containers; do
        local name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/^.\///')
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        local status=$(docker inspect --format='{{.State.Status}}' "$container")
        
        case "$health" in
            "healthy")
                echo -e "${SUCCESS} $name: 健康 ($status)"
                ;;
            "unhealthy")
                echo -e "${ERROR} $name: 不健康 ($status)"
                ;;
            "starting")
                echo -e "${WARNING} $name: 啟動中 ($status)"
                ;;
            *)
                if [ "$status" = "running" ]; then
                    echo -e "${SUCCESS} $name: 運行中 (無健康檢查)"
                else
                    echo -e "${ERROR} $name: $status"
                fi
                ;;
        esac
    done
    
    # 資源使用檢查
    echo -e "\n${CYAN}資源使用檢查:${NC}"
    docker stats --no-stream --filter "label=mcp.type" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | while IFS= read -r line; do
        if [[ "$line" =~ ([0-9]+\.[0-9]+)% ]]; then
            local cpu="${BASH_REMATCH[1]}"
            if (( $(echo "$cpu > 80" | bc -l) )); then
                echo -e "${WARNING} 高 CPU 使用率: $line"
            elif (( $(echo "$cpu > 50" | bc -l) )); then
                echo -e "${INFO} 中等 CPU 使用率: $line"
            else
                echo -e "${SUCCESS} 正常 CPU 使用率: $line"
            fi
        else
            echo "$line"
        fi
    done
    
    # 磁碟空間檢查
    echo -e "\n${CYAN}磁碟空間檢查:${NC}"
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        echo -e "${ERROR} 磁碟空間不足: ${disk_usage}%"
    elif [ "$disk_usage" -gt 80 ]; then
        echo -e "${WARNING} 磁碟空間偏高: ${disk_usage}%"
    else
        echo -e "${SUCCESS} 磁碟空間正常: ${disk_usage}%"
    fi
    
    echo -e "\n${SUCCESS} 健康檢查完成"
}

# 更新映像
update_images() {
    log_step "更新 MCP Docker 映像..."
    
    # 拉取最新映像
    docker-compose -f "$COMPOSE_FILE" pull
    
    if [ $? -eq 0 ]; then
        log_success "映像更新完成"
        
        # 詢問是否重啟服務
        read -p "是否重啟服務以使用新映像？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            restart_services
        fi
    else
        log_error "映像更新失敗"
        exit 1
    fi
}

# 備份配置和資料
backup_data() {
    local backup_name="${1:-mcp-backup-$(date +%Y%m%d_%H%M%S)}"
    local backup_path="$BACKUP_DIR/$backup_name.tar.gz"
    
    log_step "建立備份: $backup_name"
    
    # 建立備份目錄
    mkdir -p "$BACKUP_DIR"
    
    # 停止服務 (可選)
    read -p "是否停止服務以確保資料一致性？ (y/N): " -n 1 -r
    echo
    local stop_services=false
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_services=true
        stop_services
    fi
    
    # 建立備份
    tar -czf "$backup_path" \
        --exclude="$BACKUP_DIR" \
        --exclude="./logs/*" \
        --exclude="./.git" \
        .
    
    if [ $? -eq 0 ]; then
        log_success "備份建立成功: $backup_path"
        
        # 顯示備份資訊
        local size=$(du -h "$backup_path" | cut -f1)
        echo "備份大小: $size"
        echo "備份路徑: $backup_path"
    else
        log_error "備份建立失敗"
        exit 1
    fi
    
    # 重新啟動服務
    if [ "$stop_services" = true ]; then
        start_services
    fi
}

# 還原備份
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "請指定備份檔案"
        echo "可用的備份檔案:"
        ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "沒有找到備份檔案"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "備份檔案不存在: $backup_file"
        exit 1
    fi
    
    log_warning "還原備份將覆蓋現有配置"
    read -p "確定要繼續嗎？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "取消還原操作"
        exit 0
    fi
    
    log_step "還原備份: $backup_file"
    
    # 停止服務
    stop_services
    
    # 還原檔案
    tar -xzf "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "備份還原成功"
        
        # 重新啟動服務
        start_services
    else
        log_error "備份還原失敗"
        exit 1
    fi
}

# 清理系統資源
clean_system() {
    log_step "清理 Docker 系統資源..."
    
    echo "將清理以下資源:"
    echo "- 未使用的容器"
    echo "- 未使用的映像"
    echo "- 未使用的網路"
    echo "- 未使用的卷"
    echo ""
    
    read -p "確定要繼續嗎？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "取消清理操作"
        exit 0
    fi
    
    # 系統清理
    docker system prune -f
    docker image prune -f
    docker volume prune -f
    docker network prune -f
    
    log_success "系統清理完成"
    
    # 顯示清理後的統計
    echo -e "\n${CYAN}清理後的系統資源:${NC}"
    docker system df
}

# 即時監控
monitor_services() {
    local interval="${1:-5}"
    
    log_info "開始即時監控 (每 $interval 秒更新一次，按 Ctrl+C 退出)"
    
    while true; do
        clear
        echo -e "${CYAN}${CHART} MCP 服務器即時監控${NC} - $(date)"
        echo "========================================"
        
        # 容器狀態
        docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}"
        
        echo ""
        
        # 資源使用
        docker stats --no-stream --filter "label=mcp.type" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        
        sleep "$interval"
    done
}

# 效能分析
performance_analysis() {
    echo -e "\n${CYAN}${CHART} MCP 效能分析報告${NC}"
    echo "=============================="
    
    # 容器效能統計
    echo -e "\n${CYAN}容器效能統計:${NC}"
    docker stats --no-stream --filter "label=mcp.type" --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    # 映像大小分析
    echo -e "\n${CYAN}映像大小分析:${NC}"
    docker images --filter "reference=mcp/*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    
    # 網路分析
    echo -e "\n${CYAN}網路分析:${NC}"
    docker network ls | grep mcp
    
    # 卷使用分析
    echo -e "\n${CYAN}卷使用分析:${NC}"
    docker volume ls | grep mcp || echo "沒有 MCP 相關的卷"
    
    # 系統資源總覽
    echo -e "\n${CYAN}系統資源總覽:${NC}"
    docker system df
}

# 安全檢查
security_check() {
    echo -e "\n${CYAN}🔒 MCP 安全檢查報告${NC}"
    echo "=============================="
    
    local issues=0
    
    # 檢查容器權限
    echo -e "\n${CYAN}容器權限檢查:${NC}"
    local containers=$(docker-compose -f "$COMPOSE_FILE" ps -q)
    
    for container in $containers; do
        local name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/^.\///')
        local privileged=$(docker inspect --format='{{.HostConfig.Privileged}}' "$container")
        local readonly=$(docker inspect --format='{{.HostConfig.ReadonlyRootfs}}' "$container")
        local user=$(docker inspect --format='{{.Config.User}}' "$container")
        
        if [ "$privileged" = "true" ]; then
            echo -e "${ERROR} $name: 以特權模式運行 (安全風險)"
            ((issues++))
        else
            echo -e "${SUCCESS} $name: 非特權模式"
        fi
        
        if [ "$readonly" = "true" ]; then
            echo -e "${SUCCESS} $name: 唯讀根檔案系統"
        else
            echo -e "${WARNING} $name: 可寫根檔案系統"
            ((issues++))
        fi
        
        if [ -n "$user" ] && [ "$user" != "0" ] && [ "$user" != "root" ]; then
            echo -e "${SUCCESS} $name: 使用非 root 使用者 ($user)"
        else
            echo -e "${WARNING} $name: 使用 root 使用者"
            ((issues++))
        fi
    done
    
    # 檢查環境變數
    echo -e "\n${CYAN}環境變數安全檢查:${NC}"
    if [ -f "$ENV_FILE" ]; then
        local perms=$(stat -c "%a" "$ENV_FILE")
        if [ "$perms" = "600" ]; then
            echo -e "${SUCCESS} $ENV_FILE: 權限設定正確 ($perms)"
        else
            echo -e "${WARNING} $ENV_FILE: 權限過於寬鬆 ($perms)，建議設定為 600"
            ((issues++))
        fi
    fi
    
    # 檢查網路配置
    echo -e "\n${CYAN}網路安全檢查:${NC}"
    local networks=$(docker network ls --filter "name=mcp" --format "{{.Name}}")
    for network in $networks; do
        local driver=$(docker network inspect "$network" --format "{{.Driver}}")
        local internal=$(docker network inspect "$network" --format "{{.Internal}}")
        
        echo -e "${INFO} 網路: $network (驅動: $driver, 內部: $internal)"
    done
    
    # 總結
    echo -e "\n${CYAN}安全檢查總結:${NC}"
    if [ $issues -eq 0 ]; then
        echo -e "${SUCCESS} 沒有發現重大安全問題"
    else
        echo -e "${WARNING} 發現 $issues 個安全問題，建議修復"
    fi
}

# 主函數
main() {
    local command="$1"
    shift
    
    # 檢查基本依賴
    check_dependencies
    check_docker
    load_env
    
    case "$command" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$1" "$2"
            ;;
        "health")
            health_check
            ;;
        "update") 
            update_images
            ;;
        "backup")
            backup_data "$1"
            ;;
        "restore")
            restore_backup "$1"
            ;;
        "clean")
            clean_system
            ;;
        "monitor")
            monitor_services "$1"
            ;;
        "performance")
            performance_analysis
            ;;
        "security")
            security_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 錯誤處理
trap 'log_error "腳本執行時發生錯誤"; exit 1' ERR

# 執行主函數
if [ $# -eq 0 ]; then
    show_help
else
    main "$@"
fi
