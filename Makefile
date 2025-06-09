# MCP Docker 專案 Makefile
# 簡化常用操作的便捷工具

# 顏色定義
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color
BOLD := \033[1m

# 專案配置
PROJECT_NAME := mcp-docker
DOCKER_COMPOSE_DEV := docker-compose.dev.yml
DOCKER_COMPOSE_PROD := docker-compose.prod.yml
DOCKER_COMPOSE_TEST := docker-compose.test.yml
ENV_FILE := .env

# 預設目標
.DEFAULT_GOAL := help

## 🎯 主要操作
.PHONY: help install start stop restart status logs clean

help: ## 顯示此說明訊息
	@echo "$(BOLD)$(BLUE)🐳 MCP Docker 專案管理$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(YELLOW)📋 可用命令：$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-18s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)💡 範例：$(NC)"
	@echo "  make install          # 安裝和設置環境"
	@echo "  make dev              # 啟動開發環境"
	@echo "  make prod             # 啟動生產環境"
	@echo "  make logs service=github  # 查看特定服務日誌"

##@ 🚀 環境管理

install: ## 安裝 MCP Docker 環境
	@echo "$(BLUE)🚀 開始安裝 MCP Docker 環境...$(NC)"
	@chmod +x install-mcp-docker.sh
	@./install-mcp-docker.sh
	@echo "$(GREEN)✅ 安裝完成！$(NC)"

setup: ## 初始化專案環境
	@echo "$(BLUE)⚙️ 初始化專案環境...$(NC)"
	@cp -n .env.example .env || echo "$(YELLOW)⚠️ .env 檔案已存在$(NC)"
	@mkdir -p logs backups config/nginx config/prometheus
	@chmod +x *.sh
	@echo "$(GREEN)✅ 環境初始化完成！$(NC)"

check: ## 檢查系統需求和配置
	@echo "$(BLUE)🔍 檢查系統環境...$(NC)"
	@./mcp-manager-advanced.sh health
	@echo "$(GREEN)✅ 系統檢查完成！$(NC)"

##@ 🐳 Docker 操作

dev: setup ## 啟動開發環境
	@echo "$(BLUE)🔧 啟動開發環境...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_DEV) up -d
	@echo "$(GREEN)✅ 開發環境已啟動！$(NC)"
	@$(MAKE) status

prod: setup ## 啟動生產環境
	@echo "$(BLUE)🚀 啟動生產環境...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_PROD) up -d
	@echo "$(GREEN)✅ 生產環境已啟動！$(NC)"
	@$(MAKE) status

test: setup ## 啟動測試環境
	@echo "$(BLUE)🧪 啟動測試環境...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_TEST) up -d
	@echo "$(GREEN)✅ 測試環境已啟動！$(NC)"
	@$(MAKE) status

start: ## 啟動預設環境 (開發)
	@$(MAKE) dev

stop: ## 停止所有服務
	@echo "$(YELLOW)🛑 停止所有服務...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_DEV) down 2>/dev/null || true
	@docker-compose -f $(DOCKER_COMPOSE_PROD) down 2>/dev/null || true
	@docker-compose -f $(DOCKER_COMPOSE_TEST) down 2>/dev/null || true
	@echo "$(GREEN)✅ 所有服務已停止！$(NC)"

restart: stop start ## 重啟服務

##@ 📊 監控和日誌

status: ## 顯示服務狀態
	@echo "$(BLUE)📊 服務狀態：$(NC)"
	@./mcp-manager-advanced.sh status

logs: ## 查看服務日誌 (使用: make logs service=服務名)
	@if [ -n "$(service)" ]; then \
		echo "$(BLUE)📝 $(service) 服務日誌：$(NC)"; \
		./mcp-manager-advanced.sh logs $(service); \
	else \
		echo "$(BLUE)📝 所有服務日誌：$(NC)"; \
		./mcp-manager-advanced.sh logs; \
	fi

monitor: ## 即時監控服務
	@echo "$(BLUE)📊 啟動即時監控...$(NC)"
	@./mcp-manager-advanced.sh monitor

health: ## 執行健康檢查
	@echo "$(BLUE)🏥 執行健康檢查...$(NC)"
	@./mcp-manager-advanced.sh health

##@ 🔧 維護操作

update: ## 更新 Docker 映像
	@echo "$(BLUE)📥 更新 Docker 映像...$(NC)"
	@./mcp-manager-advanced.sh update
	@echo "$(GREEN)✅ 映像更新完成！$(NC)"

backup: ## 建立備份
	@echo "$(BLUE)💾 建立系統備份...$(NC)"
	@./mcp-manager-advanced.sh backup
	@echo "$(GREEN)✅ 備份完成！$(NC)"

restore: ## 還原備份 (使用: make restore file=備份檔案)
	@if [ -n "$(file)" ]; then \
		echo "$(BLUE)🔄 還原備份: $(file)$(NC)"; \
		./mcp-manager-advanced.sh restore $(file); \
	else \
		echo "$(RED)❌ 請指定備份檔案: make restore file=檔案路徑$(NC)"; \
		exit 1; \
	fi

clean: ## 清理系統資源
	@echo "$(YELLOW)🧹 清理系統資源...$(NC)"
	@./mcp-manager-advanced.sh clean
	@echo "$(GREEN)✅ 清理完成！$(NC)"

deep-clean: stop clean ## 深度清理 (停止服務 + 清理資源)
	@echo "$(YELLOW)🔥 執行深度清理...$(NC)"
	@docker system prune -af --volumes
	@docker network prune -f
	@echo "$(GREEN)✅ 深度清理完成！$(NC)"

##@ 🔒 安全和效能

security: ## 執行安全檢查
	@echo "$(BLUE)🔒 執行安全檢查...$(NC)"
	@./mcp-manager-advanced.sh security

performance: ## 效能分析
	@echo "$(BLUE)📈 執行效能分析...$(NC)"
	@./mcp-manager-advanced.sh performance

##@ 🛠️ 開發工具

gui: ## 啟動 GUI 配置器
	@echo "$(BLUE)🖥️ 啟動 GUI 配置器...$(NC)"
	@python3 mcp_docker_configurator.py

shell: ## 進入指定容器 shell (使用: make shell service=服務名)
	@if [ -n "$(service)" ]; then \
		echo "$(BLUE)🐚 進入 $(service) 容器...$(NC)"; \
		docker-compose exec $(service) /bin/sh; \
	else \
		echo "$(RED)❌ 請指定服務名: make shell service=服務名$(NC)"; \
		exit 1; \
	fi

config-check: ## 檢查配置檔案語法
	@echo "$(BLUE)📋 檢查配置檔案...$(NC)"
	@if [ -f "claude_desktop_config.json" ]; then \
		echo "檢查 Claude Desktop 配置..."; \
		cat claude_desktop_config.json | jq . > /dev/null && echo "$(GREEN)✅ Claude Desktop 配置正確$(NC)" || echo "$(RED)❌ Claude Desktop 配置有誤$(NC)"; \
	fi
	@if [ -f "examples/vscode_mcp.json" ]; then \
		echo "檢查 VS Code 配置..."; \
		cat examples/vscode_mcp.json | jq . > /dev/null && echo "$(GREEN)✅ VS Code 配置正確$(NC)" || echo "$(RED)❌ VS Code 配置有誤$(NC)"; \
	fi
	@docker-compose -f $(DOCKER_COMPOSE_DEV) config > /dev/null && echo "$(GREEN)✅ Docker Compose 開發配置正確$(NC)" || echo "$(RED)❌ Docker Compose 開發配置有誤$(NC)"

##@ 🧪 測試

test-basic: ## 執行基本功能測試
	@echo "$(BLUE)🧪 執行基本功能測試...$(NC)"
	@echo "測試 Docker 環境..."
	@docker --version
	@docker-compose --version
	@echo "測試 MCP 服務器連接..."
	@docker run --rm mcp/time echo "$(GREEN)✅ MCP Time 服務器正常$(NC)"
	@echo "$(GREEN)✅ 基本測試完成！$(NC)"

test-integration: ## 執行整合測試
	@echo "$(BLUE)🔄 執行整合測試...$(NC)"
	@$(MAKE) test
	@sleep 10
	@docker-compose -f $(DOCKER_COMPOSE_TEST) exec -T test-runner npm test || true
	@$(MAKE) stop

##@ 📦 打包和部署

build: ## 建構自定義映像
	@echo "$(BLUE)🔨 建構自定義映像...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_DEV) build
	@echo "$(GREEN)✅ 映像建構完成！$(NC)"

push: ## 推送映像到 registry
	@echo "$(BLUE)📤 推送映像到 registry...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_PROD) push
	@echo "$(GREEN)✅ 映像推送完成！$(NC)"

deploy: ## 部署到生產環境
	@echo "$(BLUE)🚀 部署到生產環境...$(NC)"
	@$(MAKE) prod
	@echo "$(GREEN)✅ 部署完成！$(NC)"

##@ ℹ️ 資訊

version: ## 顯示版本資訊
	@echo "$(BOLD)$(BLUE)MCP Docker 專案資訊$(NC)"
	@echo "=============================="
	@echo "專案版本: v2.0"
	@echo "Docker 版本: $$(docker --version)"
	@echo "Docker Compose 版本: $$(docker-compose --version)"
	@echo "Python 版本: $$(python3 --version 2>/dev/null || echo '未安裝')"
	@echo "系統資訊: $$(uname -s) $$(uname -m)"

env: ## 顯示環境變數
	@echo "$(BLUE)🌐 環境變數設定：$(NC)"
	@if [ -f "$(ENV_FILE)" ]; then \
		echo "環境檔案: $(ENV_FILE)"; \
		grep -E '^[A-Z_]+=.*' $(ENV_FILE) | head -10 | sed 's/=.*/=***/' || echo "無有效環境變數"; \
	else \
		echo "$(YELLOW)⚠️ 環境檔案不存在: $(ENV_FILE)$(NC)"; \
	fi

ports: ## 顯示使用的端口
	@echo "$(BLUE)🔌 端口使用情況：$(NC)"
	@echo "開發環境端口："
	@docker-compose -f $(DOCKER_COMPOSE_DEV) ps --format "table {{.Name}}\t{{.Ports}}" 2>/dev/null || echo "開發環境未運行"
	@echo ""
	@echo "生產環境端口："
	@docker-compose -f $(DOCKER_COMPOSE_PROD) ps --format "table {{.Name}}\t{{.Ports}}" 2>/dev/null || echo "生產環境未運行"

##@ 🆘 說明和文檔

docs: ## 開啟文檔
	@echo "$(BLUE)📚 可用文檔：$(NC)"
	@echo "  README.md                    - 專案概述"
	@echo "  QUICKSTART.md               - 快速開始指南"
	@echo "  MCP_Docker_完整指南.md      - 完整使用指南"
	@echo "  MCP_Docker_實戰範例.md      - 實戰範例"
	@echo "  PROJECT_SUMMARY.md          - 專案總結"

links: ## 顯示相關連結
	@echo "$(BLUE)🔗 相關資源連結：$(NC)"
	@echo "  MCP 官方文檔: https://modelcontextprotocol.io"
	@echo "  Docker Hub MCP: https://hub.docker.com/catalogs/mcp"
	@echo "  Docker 官方文檔: https://docs.docker.com/ai/mcp-catalog-and-toolkit/"
	@echo "  Claude Desktop: https://claude.ai/desktop"
	@echo "  GitHub 專案: https://github.com/s123104/mcp-docker"

##@ 🔧 進階操作

reset: ## 重置專案到初始狀態
	@echo "$(RED)⚠️ 這將刪除所有容器、卷和配置！$(NC)"
	@read -p "確定要繼續嗎？ (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(YELLOW)🔄 重置專案...$(NC)"; \
		$(MAKE) stop; \
		docker-compose -f $(DOCKER_COMPOSE_DEV) down -v --remove-orphans; \
		docker-compose -f $(DOCKER_COMPOSE_PROD) down -v --remove-orphans; \
		docker-compose -f $(DOCKER_COMPOSE_TEST) down -v --remove-orphans; \
		rm -f .env claude_desktop_config.json; \
		echo "$(GREEN)✅ 專案已重置！$(NC)"; \
	else \
		echo "$(BLUE)取消重置操作$(NC)"; \
	fi

emergency-stop: ## 緊急停止所有相關容器
	@echo "$(RED)🚨 緊急停止所有 MCP 相關容器...$(NC)"
	@docker stop $$(docker ps -q --filter "label=mcp.type") 2>/dev/null || echo "沒有運行的 MCP 容器"
	@docker rm $$(docker ps -aq --filter "label=mcp.type") 2>/dev/null || echo "沒有 MCP 容器需要清理"
	@echo "$(GREEN)✅ 緊急停止完成！$(NC)"

# 檢查依賴項的輔助函數
check-deps:
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)❌ Docker 未安裝$(NC)"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "$(RED)❌ Docker Compose 未安裝$(NC)"; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "$(RED)❌ Docker 未運行$(NC)"; exit 1; }

# 所有需要 Docker 的命令都依賴此檢查
start dev prod test status logs monitor health update backup clean: check-deps

# 特殊目標（不對應檔案）
.PHONY: install setup check dev prod test start stop restart status logs monitor health update backup restore clean deep-clean security performance gui shell config-check test-basic test-integration build push deploy version env ports docs links reset emergency-stop check-deps
