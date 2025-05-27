#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Docker 安裝器 GUI
簡化 MCP 服務器的選擇和配置過程
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import subprocess
import os
import webbrowser
from datetime import datetime
import platform

class MCPInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Docker 安裝器 - Model Context Protocol 服務器管理")
        self.root.geometry("1200x800")
        
        # 設定樣式
        style = ttk.Style()
        style.theme_use('clam')
        
        # MCP 服務器列表 - 基於真實的 Docker Hub mcp/ 命名空間
        self.mcp_servers = {
            # 開發工具
            "github": {
                "description": "GitHub 儲存庫管理、檔案操作和 API 整合",
                "category": "開發工具",
                "image": "mcp/github",
                "env_vars": ["GITHUB_TOKEN"],
                "ports": [],
                "required": False
            },
            "docker": {
                "description": "Docker 容器、映像、卷和網路管理",
                "category": "開發工具", 
                "image": "mcp/docker",
                "env_vars": ["DOCKER_HOST"],
                "ports": [],
                "required": False
            },
            "filesystem": {
                "description": "本地檔案系統存取和管理",
                "category": "開發工具",
                "image": "mcp/filesystem",
                "env_vars": [],
                "ports": [],
                "required": False
            },
            "git": {
                "description": "Git 版本控制操作",
                "category": "開發工具",
                "image": "mcp/git",
                "env_vars": [],
                "ports": [],
                "required": False
            },
            # 雲端服務
            "aws": {
                "description": "Amazon Web Services 整合",
                "category": "雲端服務",
                "image": "mcp/aws",
                "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"],
                "ports": [],
                "required": False
            },
            "azure": {
                "description": "Microsoft Azure 服務整合",
                "category": "雲端服務",
                "image": "mcp/azure",
                "env_vars": ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"],
                "ports": [],
                "required": False
            },
            "gcp": {
                "description": "Google Cloud Platform 整合",
                "category": "雲端服務",
                "image": "mcp/gcp",
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS"],
                "ports": [],
                "required": False
            },
            # 資料庫
            "postgres": {
                "description": "PostgreSQL 資料庫操作",
                "category": "資料庫",
                "image": "mcp/postgres",
                "env_vars": ["POSTGRES_URL"],
                "ports": ["5432"],
                "required": False
            },
            "mongodb": {
                "description": "MongoDB 資料庫操作",
                "category": "資料庫",
                "image": "mcp/mongodb",
                "env_vars": ["MONGODB_URL"],
                "ports": ["27017"],
                "required": False
            },
            # API 服務
            "slack": {
                "description": "Slack 工作區整合",
                "category": "API 服務",
                "image": "mcp/slack",
                "env_vars": ["SLACK_BOT_TOKEN"],
                "ports": [],
                "required": False
            },
            "stripe": {
                "description": "Stripe 支付處理",
                "category": "API 服務",
                "image": "mcp/stripe",
                "env_vars": ["STRIPE_API_KEY"],
                "ports": [],
                "required": False
            },
            "openai": {
                "description": "OpenAI API 整合",
                "category": "API 服務",
                "image": "mcp/openai",
                "env_vars": ["OPENAI_API_KEY"],
                "ports": [],
                "required": False
            },
            # 網路工具
            "puppeteer": {
                "description": "網頁自動化和截圖",
                "category": "網路工具",
                "image": "mcp/puppeteer",
                "env_vars": ["DOCKER_CONTAINER"],
                "ports": [],
                "required": False
            },
            "brave-search": {
                "description": "Brave 搜尋引擎 API",
                "category": "網路工具",
                "image": "mcp/brave-search",
                "env_vars": ["BRAVE_API_KEY"],
                "ports": [],
                "required": False
            },
            # 基礎工具
            "time": {
                "description": "時間和時區工具",
                "category": "基礎工具",
                "image": "mcp/time",
                "env_vars": [],
                "ports": [],
                "required": False
            },
            "weather": {
                "description": "天氣資訊查詢",
                "category": "基礎工具",
                "image": "mcp/weather",
                "env_vars": ["WEATHER_API_KEY"],
                "ports": [],
                "required": False
            }
        }
        
        self.selected_servers = {}
        self.env_entries = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # 建立主要框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(main_frame, text="MCP Docker 服務器安裝器", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 建立 Notebook（分頁）
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 分頁 1: 服務器選擇
        self.create_server_selection_tab(notebook)
        
        # 分頁 2: 環境變數配置
        self.create_env_config_tab(notebook)
        
        # 分頁 3: 配置生成
        self.create_config_generation_tab(notebook)
        
        # 分頁 4: 安裝指南
        self.create_installation_guide_tab(notebook)
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="檢查 Docker", 
                  command=self.check_docker).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="生成配置", 
                  command=self.generate_configs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="安裝選定服務器", 
                  command=self.install_servers).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除所有", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="說明", 
                  command=self.show_help).pack(side=tk.LEFT, padx=5)
        
        # 狀態列
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_server_selection_tab(self, parent):
        """建立服務器選擇分頁"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="服務器選擇")
        
        # 篩選框架
        filter_frame = ttk.LabelFrame(frame, text="篩選選項", padding="5")
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="分類:").grid(row=0, column=0, padx=5)
        categories = ["全部"] + list(set(server["category"] for server in self.mcp_servers.values()))
        self.category_var = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                     values=categories, state="readonly")
        category_combo.grid(row=0, column=1, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_servers)
        
        # 搜尋框
        ttk.Label(filter_frame, text="搜尋:").grid(row=0, column=2, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=5)
        search_entry.bind('<KeyRelease>', self.filter_servers)
        
        # 服務器列表框架
        list_frame = ttk.LabelFrame(frame, text="可用的 MCP 服務器", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 建立 Treeview
        columns = ('選擇', '名稱', '分類', '描述', '映像')
        self.server_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題
        self.server_tree.heading('選擇', text='選擇')
        self.server_tree.heading('名稱', text='名稱')
        self.server_tree.heading('分類', text='分類')
        self.server_tree.heading('描述', text='描述')
        self.server_tree.heading('映像', text='Docker 映像')
        
        # 設定欄位寬度
        self.server_tree.column('選擇', width=50)
        self.server_tree.column('名稱', width=100)
        self.server_tree.column('分類', width=100)
        self.server_tree.column('描述', width=300)
        self.server_tree.column('映像', width=200)
        
        # 加入捲軸
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        self.server_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 綁定點擊事件
        self.server_tree.bind('<Double-1>', self.toggle_server_selection)
        self.server_tree.bind('<Button-1>', self.on_server_click)
        
        # 填充服務器列表
        self.populate_server_list()
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def create_env_config_tab(self, parent):
        """建立環境變數配置分頁"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="環境變數配置")
        
        # 說明
        info_label = ttk.Label(frame, text="為選定的服務器配置必要的環境變數:")
        info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 建立捲動區域
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.env_frame = ttk.Frame(canvas)
        
        self.env_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.env_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
    def create_config_generation_tab(self, parent):
        """建立配置生成分頁"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="配置生成")
        
        # 配置類型選擇
        config_type_frame = ttk.LabelFrame(frame, text="配置類型", padding="5")
        config_type_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_type = tk.StringVar(value="claude")
        ttk.Radiobutton(config_type_frame, text="Claude Desktop", 
                       variable=self.config_type, value="claude").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(config_type_frame, text="VS Code", 
                       variable=self.config_type, value="vscode").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(config_type_frame, text="Docker Compose", 
                       variable=self.config_type, value="compose").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(config_type_frame, text="Shell 腳本", 
                       variable=self.config_type, value="shell").grid(row=0, column=3, padx=5)
        
        # 按鈕
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="生成配置", 
                  command=self.generate_configs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="儲存配置", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="複製到剪貼簿", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        # 配置顯示區域
        config_label = ttk.Label(frame, text="生成的配置:")
        config_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.config_text = scrolledtext.ScrolledText(frame, height=20, width=80)
        self.config_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
    def create_installation_guide_tab(self, parent):
        """建立安裝指南分頁"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="安裝指南")
        
        # 指南內容
        guide_text = scrolledtext.ScrolledText(frame, height=25, width=90, wrap=tk.WORD)
        guide_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 加入安裝指南內容
        guide_content = """
MCP Docker 安裝指南

1. 準備工作
   • 確保已安裝 Docker Desktop
   • 確保 Docker 服務正在運行
   • 準備必要的 API 金鑰和環境變數

2. 使用本工具的步驟
   a) 在「服務器選擇」分頁中選擇需要的 MCP 服務器
   b) 在「環境變數配置」分頁中設定必要的環境變數
   c) 在「配置生成」分頁中選擇配置類型並生成配置
   d) 將生成的配置複製或儲存到對應位置

3. Claude Desktop 配置位置
   • macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   • Windows: %APPDATA%/Claude/claude_desktop_config.json
   • Linux: ~/.config/Claude/claude_desktop_config.json

4. VS Code 配置
   • 在專案根目錄建立 .vscode/mcp.json 檔案
   • 將生成的配置內容貼上
   • 重新啟動 VS Code

5. Docker Compose 使用
   • 將生成的 docker-compose.yml 儲存到專案目錄
   • 執行: docker-compose up -d

6. 常用 Docker 指令
   • 查看運行中的容器: docker ps
   • 停止容器: docker stop <container_name>
   • 查看日誌: docker logs <container_name>
   • 清理未使用的映像: docker image prune

7. 故障排除
   • 檢查 Docker 狀態: docker info
   • 檢查容器狀態: docker ps -a
   • 查看容器日誌: docker logs <container_name>
   • 測試網路連接: docker run --rm -it alpine ping google.com

8. 安全建議
   • 使用環境變數而非硬編碼敏感資訊
   • 定期更新 Docker 映像
   • 限制容器資源使用
   • 使用非 root 使用者運行容器

9. 效能最佳化
   • 使用 .dockerignore 減少映像大小
   • 啟用 Docker BuildKit
   • 使用多階段構建
   • 配置適當的資源限制

10. 相關資源
    • MCP 官方文檔: https://modelcontextprotocol.io
    • Docker Hub MCP: https://hub.docker.com/u/mcp
    • Docker 官方文檔: https://docs.docker.com
        """
        
        guide_text.insert(tk.INSERT, guide_content)
        guide_text.config(state=tk.DISABLED)
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
    def populate_server_list(self):
        """填充服務器列表"""
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
            
        category_filter = self.category_var.get() if hasattr(self, 'category_var') else "全部"
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        
        for name, info in self.mcp_servers.items():
            # 應用篩選
            if category_filter != "全部" and info["category"] != category_filter:
                continue
            if search_term and search_term not in name.lower() and search_term not in info["description"].lower():
                continue
                
            # 檢查是否已選擇
            selected = "✓" if name in self.selected_servers else ""
            
            self.server_tree.insert("", tk.END, iid=name, values=(
                selected, name, info["category"], info["description"], info["image"]
            ))
            
    def filter_servers(self, event=None):
        """篩選服務器列表"""
        self.populate_server_list()
        
    def toggle_server_selection(self, event):
        """切換服務器選擇狀態"""
        item = self.server_tree.selection()[0]
        if item in self.selected_servers:
            del self.selected_servers[item]
        else:
            self.selected_servers[item] = self.mcp_servers[item]
        
        self.populate_server_list()
        self.update_env_config()
        
    def on_server_click(self, event):
        """處理服務器點擊事件"""
        region = self.server_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.server_tree.identify_column(event.x, event.y)
            if column == "#1":  # 選擇欄位
                item = self.server_tree.identify_row(event.y)
                if item:
                    self.toggle_server_selection(event)
                    
    def update_env_config(self):
        """更新環境變數配置介面"""
        # 清除現有的環境變數輸入框
        for widget in self.env_frame.winfo_children():
            widget.destroy()
        
        self.env_entries.clear()
        
        row = 0
        for server_name, server_info in self.selected_servers.items():
            if server_info["env_vars"]:
                # 服務器標題
                server_label = ttk.Label(self.env_frame, text=f"{server_name} ({server_info['image']})", 
                                       font=('TkDefaultFont', 10, 'bold'))
                server_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
                row += 1
                
                # 環境變數輸入框
                for env_var in server_info["env_vars"]:
                    ttk.Label(self.env_frame, text=f"{env_var}:").grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
                    
                    entry = ttk.Entry(self.env_frame, width=50)
                    entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
                    
                    self.env_entries[f"{server_name}.{env_var}"] = entry
                    row += 1
                    
        if not self.selected_servers:
            no_selection_label = ttk.Label(self.env_frame, text="請先在「服務器選擇」分頁中選擇 MCP 服務器")
            no_selection_label.grid(row=0, column=0, columnspan=2, pady=20)
            
    def generate_configs(self):
        """生成配置檔案"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先選擇至少一個 MCP 服務器")
            return
            
        config_type = self.config_type.get()
        
        if config_type == "claude":
            config = self.generate_claude_config()
        elif config_type == "vscode":
            config = self.generate_vscode_config()
        elif config_type == "compose":
            config = self.generate_compose_config()
        elif config_type == "shell":
            config = self.generate_shell_config()
        else:
            config = "未知的配置類型"
            
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.INSERT, config)
        
        self.status_var.set(f"已生成 {config_type} 配置")
        
    def generate_claude_config(self):
        """生成 Claude Desktop 配置"""
        config = {
            "mcpServers": {}
        }
        
        for server_name, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            # 加入環境變數
            env_vars = {}
            for env_var in server_info["env_vars"]:
                key = f"{server_name}.{env_var}"
                if key in self.env_entries:
                    value = self.env_entries[key].get()
                    if value:
                        server_config["args"].extend(["-e", env_var])
                        env_vars[env_var] = value
                        
            # 加入映像名稱
            server_config["args"].append(server_info["image"])
            
            if env_vars:
                server_config["env"] = env_vars
                
            config["mcpServers"][server_name] = server_config
            
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_vscode_config(self):
        """生成 VS Code 配置"""
        inputs = []
        servers = {}
        
        # 收集所有需要的輸入
        for server_name, server_info in self.selected_servers.items():
            for env_var in server_info["env_vars"]:
                input_id = f"{server_name}_{env_var.lower()}"
                inputs.append({
                    "type": "promptString",
                    "id": input_id,
                    "description": f"{server_name} {env_var}",
                    "password": "token" in env_var.lower() or "key" in env_var.lower()
                })
                
        # 生成服務器配置
        for server_name, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            env_vars = {}
            for env_var in server_info["env_vars"]:
                input_id = f"{server_name}_{env_var.lower()}"
                server_config["args"].extend(["-e", env_var])
                env_vars[env_var] = f"${{input:{input_id}}}"
                
            server_config["args"].append(server_info["image"])
            
            if env_vars:
                server_config["env"] = env_vars
                
            servers[server_name] = server_config
            
        config = {
            "inputs": inputs,
            "servers": servers
        }
        
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_compose_config(self):
        """生成 Docker Compose 配置"""
        config = {
            "version": "3.8",
            "services": {}
        }
        
        for server_name, server_info in self.selected_servers.items():
            service_config = {
                "image": server_info["image"],
                "stdin_open": True,
                "tty": True,
                "restart": "unless-stopped"
            }
            
            # 加入環境變數
            env_vars = []
            for env_var in server_info["env_vars"]:
                key = f"{server_name}.{env_var}"
                if key in self.env_entries:
                    value = self.env_entries[key].get()
                    if value:
                        env_vars.append(f"{env_var}={value}")
                    else:
                        env_vars.append(f"{env_var}=${{{env_var}}}")
                else:
                    env_vars.append(f"{env_var}=${{{env_var}}}")
                        
            if env_vars:
                service_config["environment"] = env_vars
                
            # 加入端口映射
            if server_info["ports"]:
                service_config["ports"] = [f"{port}:{port}" for port in server_info["ports"]]
                
            config["services"][f"{server_name}-mcp"] = service_config
            
        # 使用 YAML 格式輸出
        try:
            import yaml
            return yaml.dump(config, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # 如果沒有 PyYAML，使用簡單的字串格式
            yaml_str = "version: '3.8'\nservices:\n"
            for service_name, service_config in config["services"].items():
                yaml_str += f"  {service_name}:\n"
                yaml_str += f"    image: {service_config['image']}\n"
                yaml_str += f"    stdin_open: {service_config['stdin_open']}\n"
                yaml_str += f"    tty: {service_config['tty']}\n"
                yaml_str += f"    restart: {service_config['restart']}\n"
                if "environment" in service_config:
                    yaml_str += "    environment:\n"
                    for env in service_config["environment"]:
                        yaml_str += f"      - {env}\n"
                if "ports" in service_config:
                    yaml_str += "    ports:\n"
                    for port in service_config["ports"]:
                        yaml_str += f"      - '{port}'\n"
                yaml_str += "\n"
            return yaml_str
        
    def generate_shell_config(self):
        """生成 Shell 腳本配置"""
        script = "#!/bin/bash\n"
        script += "# MCP Docker 服務器啟動腳本\n"
        script += f"# 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        script += "# 檢查 Docker 是否運行\n"
        script += "if ! docker info >/dev/null 2>&1; then\n"
        script += "    echo \"錯誤: Docker 未運行或無法存取\"\n"
        script += "    exit 1\n"
        script += "fi\n\n"
        
        script += "# 設定環境變數\n"
        for server_name, server_info in self.selected_servers.items():
            for env_var in server_info["env_vars"]:
                key = f"{server_name}.{env_var}"
                if key in self.env_entries:
                    value = self.env_entries[key].get()
                    if value:
                        script += f'export {env_var}="{value}"\n'
                    else:
                        script += f'# export {env_var}="your_value_here"\n'
        script += "\n"
        
        script += "# 啟動 MCP 服務器\n"
        for server_name, server_info in self.selected_servers.items():
            script += f"# 啟動 {server_name}\n"
            cmd = f"docker run -d --name {server_name}-mcp"
            
            # 加入環境變數
            for env_var in server_info["env_vars"]:
                cmd += f" -e {env_var}"
                
            # 加入端口映射
            for port in server_info["ports"]:
                cmd += f" -p {port}:{port}"
                
            cmd += f" {server_info['image']}"
            script += cmd + "\n"
            script += f'echo "{server_name} MCP 服務器已啟動"\n\n'
            
        script += "echo \"所有 MCP 服務器已啟動\"\n"
        script += "echo \"使用 'docker ps' 查看運行狀態\"\n"
        
        return script
        
    def save_config(self):
        """儲存配置到檔案"""
        config_type = self.config_type.get()
        
        # 設定檔案類型和副檔名
        file_types = {
            "claude": ("Claude 配置檔案", "*.json"),
            "vscode": ("VS Code 配置檔案", "*.json"),
            "compose": ("Docker Compose 檔案", "*.yml"),
            "shell": ("Shell 腳本", "*.sh")
        }
        
        default_names = {
            "claude": "claude_desktop_config.json",
            "vscode": "mcp.json",
            "compose": "docker-compose.yml",
            "shell": "start_mcp_servers.sh"
        }
        
        file_type = file_types.get(config_type, ("文字檔案", "*.txt"))
        default_name = default_names.get(config_type, "config.txt")
        
        filename = filedialog.asksaveasfilename(
            defaultextension=file_type[1][1:],
            filetypes=[file_type, ("所有檔案", "*.*")],
            initialname=default_name
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.config_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"配置已儲存到: {filename}")
                self.status_var.set(f"配置已儲存到: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存檔案時發生錯誤:\n{str(e)}")
                
    def copy_to_clipboard(self):
        """複製配置到剪貼簿"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.config_text.get(1.0, tk.END))
        messagebox.showinfo("成功", "配置已複製到剪貼簿")
        self.status_var.set("配置已複製到剪貼簿")
        
    def check_docker(self):
        """檢查 Docker 狀態"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                
                # 檢查 Docker 是否運行
                result2 = subprocess.run(["docker", "info"], 
                                       capture_output=True, text=True, timeout=10)
                if result2.returncode == 0:
                    messagebox.showinfo("Docker 狀態", f"Docker 正常運行\n{version}")
                    self.status_var.set("Docker 正常運行")
                else:
                    messagebox.showwarning("Docker 狀態", 
                                         f"Docker 已安裝但未運行\n{version}\n\n請啟動 Docker Desktop")
                    self.status_var.set("Docker 未運行")
            else:
                messagebox.showerror("Docker 狀態", "Docker 未安裝或無法存取")
                self.status_var.set("Docker 未安裝")
        except subprocess.TimeoutExpired:
            messagebox.showerror("錯誤", "檢查 Docker 狀態超時")
            self.status_var.set("檢查 Docker 超時")
        except FileNotFoundError:
            messagebox.showerror("錯誤", "找不到 Docker 指令\n請確認 Docker 已安裝並加入到 PATH")
            self.status_var.set("找不到 Docker")
        except Exception as e:
            messagebox.showerror("錯誤", f"檢查 Docker 時發生錯誤:\n{str(e)}")
            self.status_var.set("檢查 Docker 錯誤")
            
    def install_servers(self):
        """安裝選定的服務器"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先選擇至少一個 MCP 服務器")
            return
            
        # 確認安裝
        server_list = "\n".join([f"• {name} ({info['image']})" 
                                for name, info in self.selected_servers.items()])
        
        if not messagebox.askyesno("確認安裝", 
                                  f"即將拉取以下 Docker 映像:\n\n{server_list}\n\n是否繼續?"):
            return
            
        # 建立進度視窗
        progress_window = tk.Toplevel(self.root)
        progress_window.title("安裝進度")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = ttk.Label(progress_window, text="準備安裝...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='determinate', 
                                     maximum=len(self.selected_servers))
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        log_text = scrolledtext.ScrolledText(progress_window, height=8, width=50)
        log_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        def install_worker():
            """在背景執行安裝作業"""
            success_count = 0
            
            for i, (name, info) in enumerate(self.selected_servers.items()):
                progress_label.config(text=f"正在安裝 {name}...")
                log_text.insert(tk.END, f"拉取 {info['image']}...\n")
                log_text.see(tk.END)
                progress_window.update()
                
                try:
                    result = subprocess.run(
                        ["docker", "pull", info['image']], 
                        capture_output=True, text=True, timeout=300
                    )
                    
                    if result.returncode == 0:
                        log_text.insert(tk.END, f"✓ {name} 安裝成功\n")
                        success_count += 1
                    else:
                        log_text.insert(tk.END, f"✗ {name} 安裝失敗: {result.stderr}\n")
                        
                except subprocess.TimeoutExpired:
                    log_text.insert(tk.END, f"✗ {name} 安裝超時\n")
                except Exception as e:
                    log_text.insert(tk.END, f"✗ {name} 安裝錯誤: {str(e)}\n")
                    
                progress_bar['value'] = i + 1
                log_text.see(tk.END)
                progress_window.update()
                
            # 完成
            progress_label.config(text=f"安裝完成! 成功: {success_count}/{len(self.selected_servers)}")
            
            close_button = ttk.Button(progress_window, text="關閉", 
                                    command=progress_window.destroy)
            close_button.pack(pady=10)
            
            self.status_var.set(f"安裝完成: {success_count}/{len(self.selected_servers)} 成功")
            
        # 在主執行緒中執行安裝（簡化版本）
        self.root.after(100, install_worker)
        
    def clear_all(self):
        """清除所有選擇"""
        if messagebox.askyesno("確認清除", "是否清除所有選擇和配置?"):
            self.selected_servers.clear()
            self.env_entries.clear()
            self.config_text.delete(1.0, tk.END)
            self.populate_server_list()
            self.update_env_config()
            self.status_var.set("所有選擇已清除")
            
    def show_help(self):
        """顯示說明視窗"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用說明")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
MCP Docker 安裝器使用說明

這個工具幫助您輕鬆選擇和配置 Model Context Protocol (MCP) 服務器。

主要功能:
1. 瀏覽和選擇可用的 MCP 服務器
2. 配置必要的環境變數
3. 生成各種格式的配置檔案
4. 自動安裝 Docker 映像

使用步驟:
1. 服務器選擇分頁:
   - 瀏覽可用的 MCP 服務器
   - 使用分類和搜尋功能篩選
   - 雙擊或點擊選擇欄位來選擇服務器

2. 環境變數配置分頁:
   - 為選定的服務器輸入必要的環境變數
   - 例如: API 金鑰、資料庫連接字串等

3. 配置生成分頁:
   - 選擇配置類型 (Claude Desktop, VS Code, Docker Compose, Shell 腳本)
   - 點擊「生成配置」按鈕
   - 複製或儲存生成的配置

4. 安裝指南分頁:
   - 查看詳細的安裝和使用說明

提示:
• 確保 Docker Desktop 已安裝並運行
• 準備好必要的 API 金鑰和憑證
• 建議先閱讀安裝指南分頁的內容
• 可以同時選擇多個服務器

如需更多幫助，請參考:
• MCP 官方文檔: https://modelcontextprotocol.io
• Docker 官方文檔: https://docs.docker.com
"""
        
        help_text.insert(tk.INSERT, help_content)
        help_text.config(state=tk.DISABLED)

def main():
    """主函數"""    
    root = tk.Tk()
    app = MCPInstallerGUI(root)
    
    # 設定視窗圖示（如果有的話）
    try:
        # root.iconbitmap('icon.ico')  # 取消註解並提供圖示檔案
        pass
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
