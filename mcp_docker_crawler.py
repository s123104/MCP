#!/usr/bin/env python3
"""
MCP Docker Hub 爬蟲 - 自動抓取最新的 MCP 服務器
支援分析安全配置、最佳實踐和下載量
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import logging
import os

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MCPServerInfo:
    """MCP 服務器資訊數據類"""
    name: str
    image: str
    description: str
    category: str
    tags: List[str]
    downloads: str
    last_updated: str
    security_level: str
    best_practices: Dict[str, any]
    environment_vars: Dict[str, str]
    volumes: List[str]
    ports: List[str]
    official: bool
    docker_required: bool
    reference_url: str
    popularity: str
    use_cases: List[str]

class MCPDockerCrawler:
    """MCP Docker Hub 爬蟲類"""
    
    def __init__(self):
        self.base_url = "https://hub.docker.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.servers = {}
        
    def fetch_mcp_user_repositories(self) -> List[Dict]:
        """抓取 MCP 用戶的所有倉庫"""
        try:
            url = f"{self.base_url}/v2/repositories/mcp/"
            params = {
                'page_size': 100,
                'ordering': 'last_updated'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            repositories = data.get('results', [])
            
            logger.info(f"找到 {len(repositories)} 個 MCP 倉庫")
            return repositories
            
        except Exception as e:
            logger.error(f"抓取 MCP 倉庫失敗: {e}")
            return []
    
    def get_repository_details(self, repo_name: str) -> Optional[Dict]:
        """獲取特定倉庫的詳細資訊"""
        try:
            url = f"{self.base_url}/v2/repositories/mcp/{repo_name}/"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"獲取倉庫 {repo_name} 詳細資訊失敗: {e}")
            return None
    
    def get_repository_tags(self, repo_name: str) -> List[str]:
        """獲取倉庫的標籤列表"""
        try:
            url = f"{self.base_url}/v2/repositories/mcp/{repo_name}/tags/"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            tags = [tag['name'] for tag in data.get('results', [])]
            return tags
            
        except Exception as e:
            logger.error(f"獲取倉庫 {repo_name} 標籤失敗: {e}")
            return []
    
    def classify_server_category(self, name: str, description: str) -> str:
        """根據名稱和描述分類服務器"""
        name_lower = name.lower()
        desc_lower = description.lower()
        
        if any(keyword in name_lower or keyword in desc_lower for keyword in ['filesystem', 'file', 'git']):
            return "檔案系統"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['postgres', 'sqlite', 'database', 'db']):
            return "數據庫"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['github', 'slack', 'google', 'drive', 'sentry']):
            return "API整合"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['fetch', 'puppeteer', 'web', 'http']):
            return "網路"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['memory', 'knowledge', 'graph']):
            return "記憶"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['search', 'brave']):
            return "搜尋"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['time', 'date']):
            return "工具"
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['monitor', 'sentry', 'log']):
            return "監控"
        else:
            return "其他"
    
    def determine_security_level(self, name: str, description: str) -> str:
        """根據服務器類型確定安全級別"""
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # 高安全級別
        if any(keyword in name_lower or keyword in desc_lower for keyword in ['postgres', 'database', 'github', 'slack', 'gdrive', 'sentry']):
            return "high"
        
        # 中等安全級別
        elif any(keyword in name_lower or keyword in desc_lower for keyword in ['filesystem', 'fetch', 'git', 'memory']):
            return "medium"
        
        # 低安全級別
        else:
            return "low"
    
    def determine_docker_requirement(self, name: str, security_level: str) -> bool:
        """判斷是否必須使用 Docker"""
        name_lower = name.lower()
        
        # 不需要 Docker 的服務
        if any(keyword in name_lower for keyword in ['time', 'everything', 'sqlite']) and security_level == "low":
            return False
        
        return True
    
    def generate_best_practices(self, name: str, security_level: str, docker_required: bool) -> Dict:
        """生成最佳實踐配置"""
        base_practices = {
            "read_only": True,
            "memory_limit": "256m",
            "cpu_limit": "0.5",
            "network_mode": "none",
            "user": "nobody",
            "security_opt": ["no-new-privileges:true"],
            "cap_drop": ["ALL"]
        }
        
        name_lower = name.lower()
        
        # 根據服務類型調整配置
        if 'filesystem' in name_lower or 'git' in name_lower:
            base_practices.update({
                "read_only": False,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "cap_add": ["CHOWN", "DAC_OVERRIDE"]
            })
        
        elif 'postgres' in name_lower or 'database' in name_lower:
            base_practices.update({
                "read_only": False,
                "memory_limit": "1g",
                "cpu_limit": "2.0",
                "network_mode": "bridge",
                "user": "postgres"
            })
        
        elif 'memory' in name_lower:
            base_practices.update({
                "read_only": False,
                "memory_limit": "1g",
                "cpu_limit": "1.0"
            })
        
        elif any(keyword in name_lower for keyword in ['github', 'slack', 'fetch']):
            base_practices.update({
                "network_mode": "bridge",
                "memory_limit": "512m",
                "cpu_limit": "1.0"
            })
        
        return base_practices
    
    def generate_environment_vars(self, name: str) -> Dict[str, str]:
        """生成環境變數範例"""
        name_lower = name.lower()
        
        if 'filesystem' in name_lower:
            return {
                "ALLOWED_PATHS": "/workspace:/data:/home/user/projects",
                "MAX_FILE_SIZE": "100MB",
                "LOG_LEVEL": "INFO",
                "READ_WRITE_MODE": "true"
            }
        elif 'github' in name_lower:
            return {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here",
                "GITHUB_API_VERSION": "2022-11-28"
            }
        elif 'postgres' in name_lower:
            return {
                "DATABASE_URI": "postgresql://user:password@host:5432/dbname",
                "PG_STATEMENT_TIMEOUT": "30000",
                "MAX_CONNECTIONS": "10"
            }
        elif 'slack' in name_lower:
            return {
                "SLACK_BOT_TOKEN": "xoxb-your-token",
                "SLACK_SIGNING_SECRET": "your_signing_secret"
            }
        elif 'fetch' in name_lower:
            return {
                "USER_AGENT": "MCP-Fetch/1.0",
                "TIMEOUT": "30s",
                "MAX_REDIRECTS": "5"
            }
        elif 'time' in name_lower:
            return {
                "DEFAULT_TIMEZONE": "Asia/Taipei",
                "TIME_FORMAT": "ISO8601"
            }
        elif 'memory' in name_lower:
            return {
                "MEMORY_DB_PATH": "/data/memory.db",
                "MAX_MEMORY_SIZE": "1GB"
            }
        else:
            return {
                "LOG_LEVEL": "INFO"
            }
    
    def generate_volumes(self, name: str) -> List[str]:
        """生成 volumes 配置"""
        name_lower = name.lower()
        
        if 'filesystem' in name_lower:
            return [
                "./workspace:/workspace",
                "./data:/data",
                "~/projects:/home/user/projects"
            ]
        elif 'git' in name_lower:
            return [
                "./.git:/workspace/.git",
                "./:/workspace"
            ]
        elif 'sqlite' in name_lower:
            return ["./data:/data"]
        elif 'memory' in name_lower:
            return ["./memory:/data"]
        else:
            return []
    
    def generate_use_cases(self, name: str, description: str) -> List[str]:
        """生成使用案例"""
        name_lower = name.lower()
        desc_lower = description.lower()
        
        if 'filesystem' in name_lower:
            return ["程式碼編輯", "文檔管理", "項目開發", "檔案搜尋", "自動化腳本"]
        elif 'github' in name_lower:
            return ["代碼管理", "問題追蹤", "拉取請求", "自動化 CI/CD", "代碼審查"]
        elif 'postgres' in name_lower:
            return ["數據分析", "數據庫管理", "查詢最佳化", "報表生成", "數據探索"]
        elif 'fetch' in name_lower:
            return ["API 測試", "數據抓取", "網頁內容檢索", "監控服務", "外部整合"]
        elif 'slack' in name_lower:
            return ["團隊溝通", "工作流程自動化", "通知發送", "狀態更新", "會議安排"]
        elif 'time' in name_lower:
            return ["時間計算", "時區轉換", "排程計劃", "時間記錄", "工作時間追蹤"]
        elif 'memory' in name_lower:
            return ["知識管理", "上下文記憶", "資訊檢索", "學習輔助", "個人助理"]
        elif 'git' in name_lower:
            return ["版本控制", "代碼提交", "分支管理", "合併衝突解決", "歷史追蹤"]
        elif 'search' in name_lower or 'brave' in name_lower:
            return ["隱私搜尋", "研究", "內容發現", "事實檢查", "競品分析"]
        elif 'sentry' in name_lower:
            return ["錯誤監控", "性能分析", "問題追蹤", "警報管理", "應用健康監控"]
        else:
            return ["多用途工具", "開發輔助", "自動化", "測試", "學習"]
    
    def determine_popularity(self, downloads: int) -> str:
        """根據下載量確定熱門程度"""
        if downloads > 100000:
            return "極高"
        elif downloads > 10000:
            return "高"
        elif downloads > 1000:
            return "中等"
        else:
            return "低"
    
    def parse_repository(self, repo_data: Dict) -> Optional[MCPServerInfo]:
        """解析倉庫資料"""
        try:
            name = repo_data['name']
            description = repo_data.get('description', '').strip()
            if not description:
                description = f"{name} MCP 服務器"
            
            # 獲取詳細資訊
            details = self.get_repository_details(name)
            downloads = details.get('pull_count', 0) if details else 0
            last_updated = repo_data.get('last_updated', '')
            
            # 分類和安全性分析
            category = self.classify_server_category(name, description)
            security_level = self.determine_security_level(name, description)
            docker_required = self.determine_docker_requirement(name, security_level)
            popularity = self.determine_popularity(downloads)
            
            # 生成配置
            best_practices = self.generate_best_practices(name, security_level, docker_required)
            environment_vars = self.generate_environment_vars(name)
            volumes = self.generate_volumes(name)
            use_cases = self.generate_use_cases(name, description)
            
            # 建立伺服器資訊
            server_info = MCPServerInfo(
                name=name.title(),
                image=f"mcp/{name}",
                description=description,
                category=category,
                tags=self.get_repository_tags(name),
                downloads=str(downloads),
                last_updated=last_updated,
                security_level=security_level,
                best_practices=best_practices,
                environment_vars=environment_vars,
                volumes=volumes,
                ports=[],
                official=True,
                docker_required=docker_required,
                reference_url=f"https://github.com/modelcontextprotocol/servers/tree/main/src/{name}",
                popularity=popularity,
                use_cases=use_cases
            )
            
            return server_info
            
        except Exception as e:
            logger.error(f"解析倉庫 {repo_data.get('name', 'unknown')} 失敗: {e}")
            return None
    
    def crawl_all_servers(self) -> Dict:
        """爬取所有 MCP 服務器"""
        logger.info("開始爬取 MCP Docker Hub 倉庫...")
        
        # 獲取所有倉庫
        repositories = self.fetch_mcp_user_repositories()
        
        servers = {}
        for repo in repositories:
            server_info = self.parse_repository(repo)
            if server_info:
                servers[server_info.name.lower()] = {
                    "id": server_info.name.lower(),
                    "name": server_info.name,
                    "description": server_info.description,
                    "category": server_info.category,
                    "image": server_info.image,
                    "environment_vars": server_info.environment_vars,
                    "volumes": server_info.volumes,
                    "security_level": server_info.security_level,
                    "docker_required": server_info.docker_required,
                    "best_practices": server_info.best_practices,
                    "default_ports": server_info.ports,
                    "official": server_info.official,
                    "reference_url": server_info.reference_url,
                    "popularity": server_info.popularity,
                    "use_cases": server_info.use_cases
                }
                logger.info(f"成功解析: {server_info.name}")
        
        logger.info(f"總共找到 {len(servers)} 個 MCP 服務器")
        return servers
    
    def update_catalog(self, output_file: str = "mcp_catalog.json"):
        """更新目錄檔案"""
        try:
            # 載入現有目錄
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    catalog = json.load(f)
            else:
                catalog = {
                    "version": "2.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_servers": 0,
                    "description": "MCP 服務器目錄 - 包含最佳實踐安全配置和 Docker 最佳化設定",
                    "security_notice": "所有 MCP 服務器都應該在隔離的 Docker 環境中運行以增強安全性",
                    "servers": {}
                }
            
            # 爬取新的服務器資訊
            new_servers = self.crawl_all_servers()
            
            # 合併新舊資料
            catalog["servers"].update(new_servers)
            catalog["total_servers"] = len(catalog["servers"])
            catalog["last_updated"] = datetime.now().isoformat()
            
            # 儲存更新的目錄
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            logger.info(f"目錄已更新: {output_file}")
            logger.info(f"總計 {catalog['total_servers']} 個服務器")
            
        except Exception as e:
            logger.error(f"更新目錄失敗: {e}")

def main():
    """主函數"""
    crawler = MCPDockerCrawler()
    crawler.update_catalog()

if __name__ == "__main__":
    main() 