#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Docker 配置器 - 進階版
自動生成 Claude Desktop, VS Code, Cursor 配置檔案
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import subprocess
import os
import webbrowser
from datetime import datetime
import platform
import yaml

class MCPDockerConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Docker 配置器 - 自動生成多平台配置")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # 設定現代化樣式
        self.setup_styles()
        
        # 官方 MCP Docker 服務器列表 (基於最新 Docker Hub mcp/ 命名空間)
        self.mcp_servers = {
            # 開發工具類
            "github": {
                "name": "GitHub",
                "description": "GitHub 儲存庫管理、檔案操作和 API 整合",
                "category": "開發工具",
                "image": "mcp/github",
                "env_vars": ["GITHUB_TOKEN"],
                "ports": [],
                "transport": ["stdio", "sse"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github"
            },
            "docker": {
                "name": "Docker", 
                "description": "Docker 容器、映像、卷和網路管理",
                "category": "開發工具",
                "image": "mcp/docker",
                "env_vars": ["DOCKER_HOST"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/QuantGeekDev/docker-mcp"
            },
            "filesystem": {
                "name": "Filesystem",
                "description": "本地檔案系統安全存取和管理",
                "category": "開發工具",
                "image": "mcp/filesystem",
                "env_vars": [],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem"
            },
            "git": {
                "name": "Git",
                "description": "Git 版本控制操作和儲存庫管理",
                "category": "開發工具",
                "image": "mcp/git", 
                "env_vars": [],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/git"
            },
            
            # 雲端服務類
            "aws": {
                "name": "AWS",
                "description": "Amazon Web Services 完整整合",
                "category": "雲端服務",
                "image": "mcp/aws",
                "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"],
                "ports": [],
                "transport": ["stdio", "sse"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/aws-kb-retrieval"
            },
            "azure": {
                "name": "Azure",
                "description": "Microsoft Azure 服務完整整合",
                "category": "雲端服務", 
                "image": "mcp/azure",
                "env_vars": ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"],
                "ports": [],
                "transport": ["stdio", "sse"],
                "official": True,
                "url": "https://github.com/Azure/azure-mcp"
            },
            "gcp": {
                "name": "Google Cloud",
                "description": "Google Cloud Platform 服務整合",
                "category": "雲端服務",
                "image": "mcp/gcp",
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://cloud.google.com/docs"
            },
            
            # 資料庫類
            "postgres": {
                "name": "PostgreSQL",
                "description": "PostgreSQL 資料庫查詢和管理",
                "category": "資料庫",
                "image": "mcp/postgres",
                "env_vars": ["POSTGRES_URL"],
                "ports": ["5432"],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres"
            },
            "mysql": {
                "name": "MySQL",
                "description": "MySQL 資料庫操作和查詢",
                "category": "資料庫",
                "image": "mcp/mysql", 
                "env_vars": ["MYSQL_URL"],
                "ports": ["3306"],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers"
            },
            "mongodb": {
                "name": "MongoDB",
                "description": "MongoDB NoSQL 資料庫操作",
                "category": "資料庫",
                "image": "mcp/mongodb",
                "env_vars": ["MONGODB_URL"],
                "ports": ["27017"],
                "transport": ["stdio"],
                "official": True,
                "url": "https://www.mongodb.com/docs"
            },
            
            # API 服務類
            "slack": {
                "name": "Slack",
                "description": "Slack 工作區訊息和頻道管理",
                "category": "API 服務",
                "image": "mcp/slack",
                "env_vars": ["SLACK_BOT_TOKEN"],
                "ports": [],
                "transport": ["stdio", "sse"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack"
            },
            "stripe": {
                "name": "Stripe",
                "description": "Stripe 支付處理和訂閱管理",
                "category": "API 服務",
                "image": "mcp/stripe",
                "env_vars": ["STRIPE_API_KEY"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://stripe.com/docs/api"
            },
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI API 整合和模型呼叫",
                "category": "API 服務",
                "image": "mcp/openai",
                "env_vars": ["OPENAI_API_KEY"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://platform.openai.com/docs"
            },
            
            # 網路工具類
            "puppeteer": {
                "name": "Puppeteer",
                "description": "網頁自動化、截圖和抓取",
                "category": "網路工具",
                "image": "mcp/puppeteer",
                "env_vars": ["DOCKER_CONTAINER"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer"
            },
            "brave-search": {
                "name": "Brave Search",
                "description": "Brave 搜尋引擎 API 整合",
                "category": "網路工具",
                "image": "mcp/brave-search",
                "env_vars": ["BRAVE_API_KEY"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
            },
            
            # 基礎工具類
            "time": {
                "name": "Time",
                "description": "時間查詢、時區轉換和日期工具",
                "category": "基礎工具",
                "image": "mcp/time",
                "env_vars": [],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/time"
            },
            "weather": {
                "name": "Weather",
                "description": "天氣資訊查詢和預報",
                "category": "基礎工具",
                "image": "mcp/weather",
                "env_vars": ["WEATHER_API_KEY"],
                "ports": [],
                "transport": ["stdio"],
                "official": True,
                "url": "https://openweathermap.org/api"
            }
        }
        
        self.selected_servers = {}
        self.env_entries = {}
        self.transport_vars = {}
        
        self.create_widgets()
        
    def setup_styles(self):
        """設定現代化 UI 樣式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定義樣式
        style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Helvetica', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Helvetica', 10), foreground='#27ae60')
        style.configure('Warning.TLabel', font=('Helvetica', 10), foreground='#e67e22')
        style.configure('Error.TLabel', font=('Helvetica', 10), foreground='#e74c3c')
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題區域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🐳 MCP Docker 配置器", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="自動生成 Claude Desktop、VS Code、Cursor 配置檔案", style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 建立 Notebook
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # 各個分頁
        self.create_server_selection_tab()
        self.create_config_tab() 
        self.create_advanced_tab()
        self.create_help_tab()
        
        # 底部按鈕區域
        self.create_bottom_buttons(main_frame)
        
        # 狀態列
        self.create_status_bar(main_frame)
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_server_selection_tab(self):
        """服務器選擇分頁"""
        frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(frame, text="📦 服務器選擇")
        
        # 篩選區域
        filter_frame = ttk.LabelFrame(frame, text="🔍 篩選和搜尋", padding="10")
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 分類篩選
        ttk.Label(filter_frame, text="分類:", style='Header.TLabel').grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        categories = ["全部"] + sorted(list(set(server["category"] for server in self.mcp_servers.values())))
        self.category_var = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                     values=categories, state="readonly", width=15)
        category_combo.grid(row=0, column=1, padx=(0, 20))
        category_combo.bind('<<ComboboxSelected>>', self.filter_servers)
        
        # 搜尋框
        ttk.Label(filter_frame, text="搜尋:", style='Header.TLabel').grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.grid(row=0, column=3, padx=(0, 20))
        search_entry.bind('<KeyRelease>', self.filter_servers)
        
        # 全選/取消全選按鈕
        ttk.Button(filter_frame, text="全選", command=self.select_all).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(filter_frame, text="清除", command=self.clear_selection).grid(row=0, column=5)
        
        # 服務器列表
        list_frame = ttk.LabelFrame(frame, text="📋 可用的 MCP 服務器", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Treeview 設定
        columns = ('選擇', '名稱', '分類', '描述', '映像', '官方')
        self.server_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # 欄位設定
        self.server_tree.heading('選擇', text='✓')
        self.server_tree.heading('名稱', text='名稱')
        self.server_tree.heading('分類', text='分類')
        self.server_tree.heading('描述', text='描述')
        self.server_tree.heading('映像', text='Docker 映像')
        self.server_tree.heading('官方', text='官方')
        
        self.server_tree.column('選擇', width=40, anchor=tk.CENTER)
        self.server_tree.column('名稱', width=100)
        self.server_tree.column('分類', width=100)
        self.server_tree.column('描述', width=300)
        self.server_tree.column('映像', width=150)
        self.server_tree.column('官方', width=60, anchor=tk.CENTER)
        
        # 捲軸
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.server_tree.xview)
        self.server_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.server_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 事件綁定
        self.server_tree.bind('<Double-1>', self.toggle_server_selection)
        self.server_tree.bind('<Button-1>', self.on_server_click)
        self.server_tree.bind('<Button-3>', self.show_server_context_menu)  # 右鍵選單
        
        # 環境變數配置區域
        env_frame = ttk.LabelFrame(frame, text="⚙️ 環境變數配置", padding="10")
        env_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 環境變數捲動區域
        canvas = tk.Canvas(env_frame, height=200)
        env_scrollbar = ttk.Scrollbar(env_frame, orient="vertical", command=canvas.yview)
        self.env_scroll_frame = ttk.Frame(canvas)
        
        self.env_scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.env_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=env_scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        env_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 填充初始資料
        self.populate_server_list()
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        env_frame.columnconfigure(0, weight=1)
        
    def create_config_tab(self):
        """配置生成分頁"""
        frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(frame, text="⚙️ 配置生成")
        
        # 平台選擇
        platform_frame = ttk.LabelFrame(frame, text="🎯 目標平台", padding="10")
        platform_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.platform_vars = {}
        platforms = [
            ("claude", "Claude Desktop", "🤖"),
            ("vscode", "VS Code", "📝"), 
            ("cursor", "Cursor", "📋"),
            ("compose", "Docker Compose", "🐳")
        ]
        
        for i, (key, name, icon) in enumerate(platforms):
            var = tk.BooleanVar(value=True if key == "claude" else False)
            self.platform_vars[key] = var
            ttk.Checkbutton(platform_frame, text=f"{icon} {name}", 
                           variable=var, command=self.update_config_preview).grid(
                           row=0, column=i, padx=15, sticky=tk.W)
        
        # 傳輸協定選擇
        transport_frame = ttk.LabelFrame(frame, text="🔌 傳輸協定", padding="10")
        transport_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.default_transport = tk.StringVar(value="stdio")
        ttk.Radiobutton(transport_frame, text="📥 STDIO (推薦)", 
                       variable=self.default_transport, value="stdio").grid(row=0, column=0, padx=15)
        ttk.Radiobutton(transport_frame, text="🌐 SSE (遠端)", 
                       variable=self.default_transport, value="sse").grid(row=0, column=1, padx=15)
        
        # 安全選項
        security_frame = ttk.LabelFrame(frame, text="🔒 安全選項", padding="10")
        security_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.security_vars = {}
        security_options = [
            ("read_only", "唯讀根檔案系統"),
            ("no_privileges", "禁止權限提升"),
            ("memory_limit", "限制記憶體使用"),
            ("network_isolation", "網路隔離")
        ]
        
        for i, (key, text) in enumerate(security_options):
            var = tk.BooleanVar(value=True)
            self.security_vars[key] = var
            ttk.Checkbutton(security_frame, text=text, variable=var).grid(
                row=i//2, column=i%2, padx=15, pady=5, sticky=tk.W)
        
        # 生成按鈕
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="🚀 生成所有配置", 
                  command=self.generate_all_configs).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="💾 儲存配置", 
                  command=self.save_all_configs).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="📋 複製到剪貼簿", 
                  command=self.copy_configs).pack(side=tk.LEFT, padx=10)
        
        # 配置預覽區域
        preview_frame = ttk.LabelFrame(frame, text="👀 配置預覽", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 分頁預覽
        self.config_notebook = ttk.Notebook(preview_frame)
        self.config_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.config_texts = {}
        for key, name, _ in platforms:
            text_frame = ttk.Frame(self.config_notebook)
            self.config_notebook.add(text_frame, text=name)
            
            text_widget = scrolledtext.ScrolledText(text_frame, height=15, width=80, 
                                                   font=('Consolas', 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.config_texts[key] = text_widget
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
    def create_advanced_tab(self):
        """進階設定分頁"""
        frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(frame, text="🔧 進階設定")
        
        # Docker 設定
        docker_frame = ttk.LabelFrame(frame, text="🐳 Docker 設定", padding="10")
        docker_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(docker_frame, text="基礎映像:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.base_image_var = tk.StringVar(value="docker.io")
        base_image_entry = ttk.Entry(docker_frame, textvariable=self.base_image_var, width=30)
        base_image_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(docker_frame, text="網路模式:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.network_var = tk.StringVar(value="bridge")
        network_combo = ttk.Combobox(docker_frame, textvariable=self.network_var, 
                                   values=["bridge", "host", "none", "custom"], width=15)
        network_combo.grid(row=0, column=3, sticky=tk.W)
        
        # 資源限制
        resource_frame = ttk.LabelFrame(frame, text="📊 資源限制", padding="10")
        resource_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(resource_frame, text="記憶體限制:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.memory_var = tk.StringVar(value="512m")
        memory_entry = ttk.Entry(resource_frame, textvariable=self.memory_var, width=10)
        memory_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(resource_frame, text="CPU 限制:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.cpu_var = tk.StringVar(value="1.0")
        cpu_entry = ttk.Entry(resource_frame, textvariable=self.cpu_var, width=10)
        cpu_entry.grid(row=0, column=3, sticky=tk.W)
        
        # 卷掛載
        volume_frame = ttk.LabelFrame(frame, text="💾 卷掛載", padding="10")
        volume_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 卷掛載列表
        self.volume_tree = ttk.Treeview(volume_frame, columns=('host', 'container', 'mode'), 
                                       show='headings', height=6)
        self.volume_tree.heading('host', text='主機路徑')
        self.volume_tree.heading('container', text='容器路徑')
        self.volume_tree.heading('mode', text='模式')
        
        self.volume_tree.column('host', width=200)
        self.volume_tree.column('container', width=200)
        self.volume_tree.column('mode', width=100)
        
        self.volume_tree.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 卷掛載控制按鈕
        ttk.Button(volume_frame, text="➕ 添加卷", command=self.add_volume).grid(row=1, column=0, padx=5)
        ttk.Button(volume_frame, text="➖ 移除卷", command=self.remove_volume).grid(row=1, column=1, padx=5)
        ttk.Button(volume_frame, text="📁 瀏覽", command=self.browse_volume).grid(row=1, column=2, padx=5)
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        volume_frame.columnconfigure(0, weight=1)
        volume_frame.rowconfigure(0, weight=1)
        
    def create_help_tab(self):
        """說明和文檔分頁"""
        frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(frame, text="📚 使用說明")
        
        # 快速入門
        quick_frame = ttk.LabelFrame(frame, text="🚀 快速入門", padding="10")
        quick_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        quick_steps = [
            "1. 在「服務器選擇」分頁選擇需要的 MCP 服務器",
            "2. 配置必要的環境變數 (API 金鑰等)",
            "3. 在「配置生成」分頁選擇目標平台",
            "4. 點擊「生成所有配置」按鈕",
            "5. 將配置複製到對應的配置檔案位置"
        ]
        
        for i, step in enumerate(quick_steps):
            ttk.Label(quick_frame, text=step, style='Info.TLabel').grid(
                row=i, column=0, sticky=tk.W, pady=2)
        
        # 配置位置
        location_frame = ttk.LabelFrame(frame, text="📍 配置檔案位置", padding="10")
        location_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        locations = [
            ("Claude Desktop (macOS)", "~/Library/Application Support/Claude/claude_desktop_config.json"),
            ("Claude Desktop (Windows)", "%APPDATA%/Claude/claude_desktop_config.json"),
            ("VS Code", ".vscode/mcp.json"),
            ("Cursor", "Cursor 設定 > MCP 區段"),
            ("Docker Compose", "docker-compose.yml")
        ]
        
        for i, (platform, path) in enumerate(locations):
            ttk.Label(location_frame, text=f"{platform}:", style='Header.TLabel').grid(
                row=i, column=0, sticky=tk.W, padx=(0, 10))
            ttk.Label(location_frame, text=path, style='Info.TLabel').grid(
                row=i, column=1, sticky=tk.W)
        
        # 常見問題
        faq_frame = ttk.LabelFrame(frame, text="❓ 常見問題", padding="10")
        faq_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        faq_text = scrolledtext.ScrolledText(faq_frame, height=12, wrap=tk.WORD)
        faq_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        faq_content = """
Q: 為什麼推薦使用 Docker MCP 而不是傳統 MCP？
A: Docker MCP 提供更好的安全隔離、更簡單的部署和更一致的運行環境。

Q: STDIO 和 SSE 傳輸協定有什麼差別？
A: STDIO 適用於本地使用，更安全且無需網路端口；SSE 適用於遠端連接，基於 HTTP 協定。

Q: 如何獲得 API 金鑰？
A: 請訪問對應服務的官方網站申請 API 金鑰，如 GitHub、Slack、OpenAI 等。

Q: 容器無法啟動怎麼辦？
A: 檢查 Docker 是否運行、環境變數是否正確設定、端口是否被占用。

Q: 如何更新 MCP 服務器？
A: 使用 docker pull 命令更新映像，然後重新啟動容器。

Q: 安全性如何保證？
A: Docker 容器提供程序隔離、檔案系統隔離、網路隔離和資源限制等多層安全保護。
        """
        
        faq_text.insert(tk.INSERT, faq_content.strip())
        faq_text.config(state=tk.DISABLED)
        
        # 相關連結
        links_frame = ttk.LabelFrame(frame, text="🔗 相關資源", padding="10")
        links_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        links = [
            ("Docker MCP 官方文檔", "https://docs.docker.com/ai/mcp-catalog-and-toolkit/"),
            ("Docker Hub MCP Catalog", "https://hub.docker.com/catalogs/mcp"),
            ("MCP 協定規範", "https://modelcontextprotocol.io"),
            ("GitHub 討論區", "https://github.com/docker/mcp-servers")
        ]
        
        for i, (text, url) in enumerate(links):
            link_button = ttk.Button(links_frame, text=f"🌐 {text}", 
                                   command=lambda u=url: webbrowser.open(u))
            link_button.grid(row=i//2, column=i%2, padx=10, pady=5, sticky=tk.W)
        
        # 配置網格權重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        faq_frame.columnconfigure(0, weight=1)
        faq_frame.rowconfigure(0, weight=1)
        
    def create_bottom_buttons(self, parent):
        """底部按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=3, pady=15)
        
        # 左側按鈕
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="🔍 檢查 Docker", 
                  command=self.check_docker_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="📥 安裝選定服務器", 
                  command=self.install_selected_servers).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="🧹 清除所有選擇", 
                  command=self.clear_all_selections).pack(side=tk.LEFT, padx=5)
        
        # 右側按鈕
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="💾 匯出設定", 
                  command=self.export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="📁 匯入設定", 
                  command=self.import_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="❓ 說明", 
                  command=self.show_detailed_help).pack(side=tk.LEFT, padx=5)
        
    def create_status_bar(self, parent):
        """狀態列"""
        self.status_var = tk.StringVar()
        self.status_var.set("就緒 - 選擇 MCP 服務器開始配置")
        
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W, padding="5")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 右側資訊
        info_label = ttk.Label(status_frame, text="MCP Docker Configurator v2.0", 
                             style='Info.TLabel')
        info_label.pack(side=tk.RIGHT, padx=(10, 0))
        
    # 核心功能方法
    def populate_server_list(self):
        """填充服務器列表"""
        # 清除現有項目
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
            
        # 應用篩選
        category_filter = self.category_var.get() if hasattr(self, 'category_var') else "全部"
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        
        for server_id, info in self.mcp_servers.items():
            # 分類篩選
            if category_filter != "全部" and info["category"] != category_filter:
                continue
                
            # 搜尋篩選  
            if search_term and not any(search_term in text.lower() for text in [
                server_id, info["name"], info["description"], info["category"]]):
                continue
                
            # 檢查是否已選擇
            selected = "✓" if server_id in self.selected_servers else ""
            official = "✓" if info.get("official", False) else ""
            
            # 插入項目
            item_id = self.server_tree.insert("", tk.END, iid=server_id, values=(
                selected, info["name"], info["category"], 
                info["description"], info["image"], official
            ))
            
            # 設定顏色 (官方服務器用不同顏色)
            if info.get("official", False):
                self.server_tree.set(item_id, "官方", "🔥")
                
    def filter_servers(self, event=None):
        """篩選服務器列表"""
        self.populate_server_list()
        
    def toggle_server_selection(self, event):
        """切換服務器選擇狀態"""
        selection = self.server_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        if item_id in self.selected_servers:
            del self.selected_servers[item_id]
            self.status_var.set(f"已取消選擇 {self.mcp_servers[item_id]['name']}")
        else:
            self.selected_servers[item_id] = self.mcp_servers[item_id].copy()
            self.status_var.set(f"已選擇 {self.mcp_servers[item_id]['name']}")
            
        self.populate_server_list()
        self.update_env_config()
        self.update_config_preview()
                
    def on_server_click(self, event):
        """處理服務器點擊事件"""
        region = self.server_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.server_tree.identify_column(event.x, event.y)
            if column == "#1":  # 選擇欄位
                self.toggle_server_selection(event)
                
    def show_server_context_menu(self, event):
        """顯示服務器右鍵選單"""
        item = self.server_tree.identify_row(event.y)
        if not item:
            return
            
        context_menu = tk.Menu(self.root, tearoff=0)
        server_info = self.mcp_servers[item]
        
        context_menu.add_command(label=f"📋 複製映像名稱", 
                               command=lambda: self.copy_to_clipboard(server_info["image"]))
        context_menu.add_command(label=f"🌐 開啟文檔", 
                               command=lambda: webbrowser.open(server_info["url"]))
        context_menu.add_separator()
        
        if item in self.selected_servers:
            context_menu.add_command(label="❌ 取消選擇", 
                                   command=lambda: self.toggle_selection(item))
        else:
            context_menu.add_command(label="✅ 選擇", 
                                   command=lambda: self.toggle_selection(item))
            
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def toggle_selection(self, item_id):
        """切換單個服務器選擇狀態"""
        if item_id in self.selected_servers:
            del self.selected_servers[item_id]
        else:
            self.selected_servers[item_id] = self.mcp_servers[item_id].copy()
        self.populate_server_list()
        self.update_env_config()
        self.update_config_preview()
        
    def select_all(self):
        """全選可見的服務器"""
        visible_servers = []
        for child in self.server_tree.get_children():
            visible_servers.append(child)
            
        for server_id in visible_servers:
            if server_id not in self.selected_servers:
                self.selected_servers[server_id] = self.mcp_servers[server_id].copy()
                
        self.populate_server_list()
        self.update_env_config()
        self.update_config_preview()
        self.status_var.set(f"已選擇 {len(visible_servers)} 個服務器")
        
    def clear_selection(self):
        """清除所有選擇"""
        self.selected_servers.clear()
        self.populate_server_list()
        self.update_env_config()
        self.update_config_preview()
        self.status_var.set("已清除所有選擇")
        
    def update_env_config(self):
        """更新環境變數配置界面"""
        # 清除現有組件
        for widget in self.env_scroll_frame.winfo_children():
            widget.destroy()
            
        self.env_entries.clear()
        self.transport_vars.clear()
        
        if not self.selected_servers:
            ttk.Label(self.env_scroll_frame, text="請先選擇 MCP 服務器", 
                     style='Info.TLabel').grid(row=0, column=0, pady=20)
            return
            
        row = 0
        for server_id, server_info in self.selected_servers.items():
            # 服務器標題
            server_frame = ttk.LabelFrame(self.env_scroll_frame, 
                                        text=f"{server_info['name']} ({server_info['image']})", 
                                        padding="10")
            server_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
            
            # 傳輸協定選擇 (如果支援多種)
            if len(server_info["transport"]) > 1:
                ttk.Label(server_frame, text="傳輸協定:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
                transport_var = tk.StringVar(value=server_info["transport"][0])
                self.transport_vars[server_id] = transport_var
                
                for i, transport in enumerate(server_info["transport"]):
                    ttk.Radiobutton(server_frame, text=transport.upper(), 
                                  variable=transport_var, value=transport).grid(
                                  row=0, column=i+1, padx=10)
            
            # 環境變數輸入
            env_row = 1
            for env_var in server_info["env_vars"]:
                ttk.Label(server_frame, text=f"{env_var}:", style='Header.TLabel').grid(
                    row=env_row, column=0, sticky=tk.W, pady=5)
                    
                entry = ttk.Entry(server_frame, width=50, show="*" if "token" in env_var.lower() or "key" in env_var.lower() else None)
                entry.grid(row=env_row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
                
                self.env_entries[f"{server_id}.{env_var}"] = entry
                env_row += 1
                
            server_frame.columnconfigure(1, weight=1)
            row += 1
            
        self.env_scroll_frame.columnconfigure(0, weight=1)
        
    def update_config_preview(self):
        """更新配置預覽"""
        if not hasattr(self, 'config_texts'):
            return
            
        # 清除所有預覽
        for platform, text_widget in self.config_texts.items():
            text_widget.delete(1.0, tk.END)
            
        if not self.selected_servers:
            for text_widget in self.config_texts.values():
                text_widget.insert(tk.INSERT, "請先選擇 MCP 服務器...")
            return
            
        # 生成各平台配置
        configs = self.generate_all_platform_configs()
        
        for platform, config in configs.items():
            if platform in self.config_texts:
                self.config_texts[platform].delete(1.0, tk.END)
                self.config_texts[platform].insert(tk.INSERT, config)
                
    def generate_all_platform_configs(self):
        """生成所有平台的配置"""
        configs = {}
        
        if self.platform_vars.get("claude", tk.BooleanVar()).get():
            configs["claude"] = self.generate_claude_config()
        if self.platform_vars.get("vscode", tk.BooleanVar()).get():
            configs["vscode"] = self.generate_vscode_config()
        if self.platform_vars.get("cursor", tk.BooleanVar()).get():
            configs["cursor"] = self.generate_cursor_config()
        if self.platform_vars.get("compose", tk.BooleanVar()).get():
            configs["compose"] = self.generate_docker_compose_config()
            
        return configs
        
    def generate_claude_config(self):
        """生成 Claude Desktop 配置"""
        config = {"mcpServers": {}}
        
        for server_id, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            # 安全選項
            if self.security_vars.get("read_only", tk.BooleanVar(value=True)).get():
                server_config["args"].extend(["--read-only"])
            if self.security_vars.get("no_privileges", tk.BooleanVar(value=True)).get():
                server_config["args"].extend(["--security-opt", "no-new-privileges"])
            if self.security_vars.get("memory_limit", tk.BooleanVar(value=True)).get():
                server_config["args"].extend(["--memory", self.memory_var.get()])
                
            # 環境變數
            env_vars = {}
            for env_var in server_info["env_vars"]:
                key = f"{server_id}.{env_var}"
                if key in self.env_entries:
                    value = self.env_entries[key].get()
                    if value:
                        server_config["args"].extend(["-e", env_var])
                        env_vars[env_var] = value
                        
            # 傳輸協定處理
            transport = self.transport_vars.get(server_id, tk.StringVar(value="stdio")).get()
            if transport == "sse":
                default_port = 5008
                server_config["args"].extend(["-p", f"{default_port}:{default_port}"])
                server_config["args"].append(server_info["image"])
                server_config["args"].extend(["--transport", "sse"])
            else:
                server_config["args"].append(server_info["image"])
                
            if env_vars:
                server_config["env"] = env_vars
                
            config["mcpServers"][server_id] = server_config
            
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_vscode_config(self):
        """生成 VS Code 配置"""
        inputs = []
        servers = {}
        
        # 收集所有環境變數輸入
        for server_id, server_info in self.selected_servers.items():
            for env_var in server_info["env_vars"]:
                input_id = f"{server_id}_{env_var.lower()}"
                inputs.append({
                    "type": "promptString",
                    "id": input_id,
                    "description": f"{server_info['name']} {env_var}",
                    "password": "token" in env_var.lower() or "key" in env_var.lower()
                })
                
        # 生成服務器配置
        for server_id, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            # 安全選項
            if self.security_vars.get("read_only", tk.BooleanVar(value=True)).get():
                server_config["args"].extend(["--read-only"])
                
            env_vars = {}
            for env_var in server_info["env_vars"]:
                input_id = f"{server_id}_{env_var.lower()}"
                server_config["args"].extend(["-e", env_var])
                env_vars[env_var] = f"${{input:{input_id}}}"
                
            server_config["args"].append(server_info["image"])
            
            if env_vars:
                server_config["env"] = env_vars
                
            servers[server_id] = server_config
            
        config = {
            "inputs": inputs,
            "servers": servers
        }
        
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_cursor_config(self):
        """生成 Cursor 配置"""
        config = {"mcp": {"servers": {}}}
        
        for server_id, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            # 環境變數處理
            env_vars = {}
            for env_var in server_info["env_vars"]:
                key = f"{server_id}.{env_var}"
                if key in self.env_entries:
                    value = self.env_entries[key].get()
                    if value:
                        env_vars[env_var] = value
                    else:
                        env_vars[env_var] = f"<YOUR_{env_var}_HERE>"
                        
            server_config["args"].append(server_info["image"])
            
            if env_vars:
                server_config["env"] = env_vars
                
            config["mcp"]["servers"][server_id] = server_config
            
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_docker_compose_config(self):
        """生成 Docker Compose 配置"""
        config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "mcp-network": {
                    "driver": "bridge"
                }
            }
        }
        
        for server_id, server_info in self.selected_servers.items():
            service_config = {
                "image": server_info["image"],
                "container_name": f"{server_id}-mcp",
                "stdin_open": True,
                "tty": True,
                "restart": "unless-stopped",
                "networks": ["mcp-network"]
            }
            
            # 安全選項
            security_opts = []
            if self.security_vars.get("no_privileges", tk.BooleanVar(value=True)).get():
                security_opts.append("no-new-privileges:true")
                
            if security_opts:
                service_config["security_opt"] = security_opts
                
            if self.security_vars.get("read_only", tk.BooleanVar(value=True)).get():
                service_config["read_only"] = True
                service_config["tmpfs"] = ["/tmp"]
                
            # 資源限制
            if self.security_vars.get("memory_limit", tk.BooleanVar(value=True)).get():
                service_config["mem_limit"] = self.memory_var.get()
                
            # 環境變數
            env_vars = []
            for env_var in server_info["env_vars"]:
                key = f"{server_id}.{env_var}"
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
                
            # 端口映射
            if server_info["ports"]:
                service_config["ports"] = [f"{port}:{port}" for port in server_info["ports"]]
                
            config["services"][f"{server_id}-mcp"] = service_config
            
        return yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
    # 輔助功能方法
    def check_docker_status(self):
        """檢查 Docker 狀態"""
        try:
            # 檢查 Docker 版本
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise Exception("Docker 未安裝")
                
            version = result.stdout.strip()
            
            # 檢查 Docker 是否運行
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                messagebox.showwarning("Docker 狀態", 
                                     f"Docker 已安裝但未運行\n{version}\n\n請啟動 Docker Desktop")
                self.status_var.set("Docker 未運行")
                return False
                
            # 檢查 MCP 映像
            result = subprocess.run(["docker", "images", "--filter", "reference=mcp/*"], 
                                  capture_output=True, text=True, timeout=5)
            mcp_images = len(result.stdout.strip().split('\n')) - 1  # 減去標題行
            
            messagebox.showinfo("Docker 狀態", 
                              f"✅ Docker 正常運行\n{version}\n\n📦 已安裝 {mcp_images} 個 MCP 映像")
            self.status_var.set(f"Docker 正常運行 - {mcp_images} 個 MCP 映像")
            return True
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("錯誤", "檢查 Docker 狀態超時")
            self.status_var.set("檢查超時")
        except FileNotFoundError:
            messagebox.showerror("錯誤", "找不到 Docker 命令\n請確認 Docker 已正確安裝")
            self.status_var.set("Docker 未安裝")
        except Exception as e:
            messagebox.showerror("錯誤", f"檢查 Docker 時發生錯誤:\n{str(e)}")
            self.status_var.set("檢查失敗")
            
        return False
        
    def install_selected_servers(self):
        """安裝選定的服務器"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先選擇至少一個 MCP 服務器")
            return
            
        if not self.check_docker_status():
            return
            
        # 確認安裝
        server_list = "\n".join([f"• {info['name']} ({info['image']})" 
                                for info in self.selected_servers.values()])
        
        if not messagebox.askyesno("確認安裝", 
                                  f"即將下載以下 Docker 映像:\n\n{server_list}\n\n這可能需要一些時間。是否繼續?"):
            return
            
        self.show_installation_progress()
        
    def show_installation_progress(self):
        """顯示安裝進度視窗"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("安裝進度")
        progress_window.geometry("500x400")
        progress_window.transient(self.root)
        progress_window.grab_set()
        progress_window.resizable(False, False)
        
        # 進度標籤
        progress_label = ttk.Label(progress_window, text="準備安裝...", style='Header.TLabel')
        progress_label.pack(pady=10)
        
        # 進度條
        progress_bar = ttk.Progressbar(progress_window, mode='determinate', 
                                     maximum=len(self.selected_servers))
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        # 詳細日誌
        log_frame = ttk.LabelFrame(progress_window, text="安裝日誌", padding="5")
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        log_text = scrolledtext.ScrolledText(log_frame, height=15, width=60, font=('Consolas', 9))
        log_text.pack(fill=tk.BOTH, expand=True)
        
        def install_worker():
            """背景安裝工作"""
            success_count = 0
            total_count = len(self.selected_servers)
            
            for i, (server_id, server_info) in enumerate(self.selected_servers.items()):
                progress_label.config(text=f"正在安裝 {server_info['name']}... ({i+1}/{total_count})")
                log_text.insert(tk.END, f"\n🚀 開始下載 {server_info['image']}...\n")
                log_text.see(tk.END)
                progress_window.update()
                
                try:
                    # 執行 docker pull
                    process = subprocess.Popen(
                        ["docker", "pull", server_info['image']], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        text=True,
                        universal_newlines=True
                    )
                    
                    # 即時顯示輸出
                    for line in process.stdout:
                        log_text.insert(tk.END, line)
                        log_text.see(tk.END)
                        progress_window.update()
                        
                    process.wait()
                    
                    if process.returncode == 0:
                        log_text.insert(tk.END, f"✅ {server_info['name']} 安裝成功!\n")
                        success_count += 1
                    else:
                        log_text.insert(tk.END, f"❌ {server_info['name']} 安裝失敗!\n")
                        
                except Exception as e:
                    log_text.insert(tk.END, f"❌ {server_info['name']} 安裝錯誤: {str(e)}\n")
                    
                progress_bar['value'] = i + 1
                log_text.see(tk.END)
                progress_window.update()
                
            # 完成
            progress_label.config(text=f"安裝完成! 成功: {success_count}/{total_count}")
            log_text.insert(tk.END, f"\n🎉 安裝完成! 成功安裝 {success_count} 個服務器\n")
            log_text.see(tk.END)
            
            # 關閉按鈕
            close_button = ttk.Button(progress_window, text="關閉", 
                                    command=progress_window.destroy)
            close_button.pack(pady=10)
            
            self.status_var.set(f"安裝完成: {success_count}/{total_count} 成功")
            
        # 啟動安裝
        self.root.after(100, install_worker)
        
    def generate_all_configs(self):
        """生成所有選定平台的配置"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先選擇至少一個 MCP 服務器")
            return
            
        self.update_config_preview()
        self.status_var.set("已生成所有平台配置")
        messagebox.showinfo("成功", "已生成所有選定平台的配置檔案")
        
    def save_all_configs(self):
        """儲存所有配置到檔案"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先生成配置")
            return
            
        # 選擇儲存目錄
        save_dir = filedialog.askdirectory(title="選擇配置檔案儲存目錄")
        if not save_dir:
            return
            
        configs = self.generate_all_platform_configs()
        saved_files = []
        
        file_names = {
            "claude": "claude_desktop_config.json",
            "vscode": "mcp.json", 
            "cursor": "cursor_mcp_config.json",
            "compose": "docker-compose.yml"
        }
        
        try:
            for platform, config in configs.items():
                if config and self.platform_vars.get(platform, tk.BooleanVar()).get():
                    file_path = os.path.join(save_dir, file_names[platform])
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(config)
                    saved_files.append(file_names[platform])
                    
            if saved_files:
                messagebox.showinfo("成功", f"已儲存以下配置檔案:\n\n" + "\n".join(f"• {f}" for f in saved_files))
                self.status_var.set(f"已儲存 {len(saved_files)} 個配置檔案")
            else:
                messagebox.showwarning("警告", "沒有需要儲存的配置檔案")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存配置檔案時發生錯誤:\n{str(e)}")
            
    def copy_configs(self):
        """複製配置到剪貼簿"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "請先生成配置")
            return
            
        # 獲取當前顯示的配置
        current_tab = self.config_notebook.tab(self.config_notebook.select(), "text")
        platform_map = {
            "Claude Desktop": "claude",
            "VS Code": "vscode", 
            "Cursor": "cursor",
            "Docker Compose": "compose"
        }
        
        platform = platform_map.get(current_tab)
        if platform and platform in self.config_texts:
            config_content = self.config_texts[platform].get(1.0, tk.END)
            if config_content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(config_content)
                messagebox.showinfo("成功", f"已複製 {current_tab} 配置到剪貼簿")
                self.status_var.set(f"已複製 {current_tab} 配置")
            else:
                messagebox.showwarning("警告", "配置內容為空")
                
    def copy_to_clipboard(self, text):
        """複製文字到剪貼簿"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("成功", "已複製到剪貼簿")
        
    def clear_all_selections(self):
        """清除所有選擇和配置"""
        if messagebox.askyesno("確認", "這將清除所有選擇和配置，是否繼續?"):
            self.selected_servers.clear()
            self.env_entries.clear()
            self.transport_vars.clear()
            
            # 重置UI
            self.populate_server_list()
            self.update_env_config()
            self.update_config_preview()
            
            # 重置篩選
            self.category_var.set("全部")
            self.search_var.set("")
            
            self.status_var.set("已清除所有選擇")
            
    def export_settings(self):
        """匯出設定"""
        if not self.selected_servers:
            messagebox.showwarning("警告", "沒有可匯出的設定")
            return
            
        settings = {
            "selected_servers": list(self.selected_servers.keys()),
            "env_vars": {},
            "transport_settings": {},
            "platform_settings": {k: v.get() for k, v in self.platform_vars.items()},
            "security_settings": {k: v.get() for k, v in self.security_vars.items()},
            "resource_settings": {
                "memory": self.memory_var.get(),
                "cpu": self.cpu_var.get(),
                "network": self.network_var.get()
            }
        }
        
        # 匯出環境變數 (不包含實際值，只包含欄位名稱)
        for key, entry in self.env_entries.items():
            if entry.get():  # 只匯出有值的欄位
                settings["env_vars"][key] = "***HIDDEN***"  # 隱藏實際值
                
        # 匯出傳輸設定
        for server_id, var in self.transport_vars.items():
            settings["transport_settings"][server_id] = var.get()
            
        # 儲存到檔案
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")],
            initialname="mcp_settings.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"設定已匯出到:\n{filename}")
                self.status_var.set("設定已匯出")
            except Exception as e:
                messagebox.showerror("錯誤", f"匯出設定時發生錯誤:\n{str(e)}")
                
    def import_settings(self):
        """匯入設定"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 清除現有選擇
            self.selected_servers.clear()
            
            # 匯入服務器選擇
            for server_id in settings.get("selected_servers", []):
                if server_id in self.mcp_servers:
                    self.selected_servers[server_id] = self.mcp_servers[server_id].copy()
                    
            # 匯入平台設定
            for platform, value in settings.get("platform_settings", {}).items():
                if platform in self.platform_vars:
                    self.platform_vars[platform].set(value)
                    
            # 匯入安全設定
            for setting, value in settings.get("security_settings", {}).items():
                if setting in self.security_vars:
                    self.security_vars[setting].set(value)
                    
            # 匯入資源設定
            resource_settings = settings.get("resource_settings", {})
            self.memory_var.set(resource_settings.get("memory", "512m"))
            self.cpu_var.set(resource_settings.get("cpu", "1.0"))
            self.network_var.set(resource_settings.get("network", "bridge"))
            
            # 更新UI
            self.populate_server_list()
            self.update_env_config()
            self.update_config_preview()
            
            messagebox.showinfo("成功", f"已匯入設定:\n• {len(self.selected_servers)} 個服務器\n• 平台和安全設定")
            self.status_var.set(f"已匯入 {len(self.selected_servers)} 個服務器設定")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"匯入設定時發生錯誤:\n{str(e)}")
            
    def show_detailed_help(self):
        """顯示詳細說明視窗"""
        help_window = tk.Toplevel(self.root)
        help_window.title("詳細使用說明")
        help_window.geometry("800x600")
        help_window.transient(self.root)
        
        # 建立分頁說明
        help_notebook = ttk.Notebook(help_window)
        help_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 快速入門
        quick_frame = ttk.Frame(help_notebook)
        help_notebook.add(quick_frame, text="快速入門")
        
        quick_text = scrolledtext.ScrolledText(quick_frame, wrap=tk.WORD, font=('Helvetica', 11))
        quick_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        quick_content = """
🚀 MCP Docker 配置器快速入門指南

1. 選擇 MCP 服務器
   • 在「服務器選擇」分頁瀏覽可用的服務器
   • 使用分類篩選和搜尋功能快速找到需要的服務器
   • 雙擊或點擊選擇欄位來選擇/取消選擇服務器

2. 配置環境變數
   • 為選定的服務器輸入必要的 API 金鑰和認證資訊
   • 敏感資訊會自動隱藏顯示

3. 選擇目標平台
   • 在「配置生成」分頁選擇需要的平台
   • 支援 Claude Desktop、VS Code、Cursor 和 Docker Compose

4. 自訂安全和資源設定
   • 配置容器安全選項
   • 設定資源限制

5. 生成和儲存配置
   • 點擊「生成所有配置」查看預覽
   • 使用「儲存配置」將檔案儲存到指定目錄
   • 或使用「複製到剪貼簿」快速複製單個配置

6. 安裝 Docker 映像
   • 使用「安裝選定服務器」自動下載所需的 Docker 映像
   • 支援即時進度顯示和日誌記錄
        """
        
        quick_text.insert(tk.INSERT, quick_content.strip())
        quick_text.config(state=tk.DISABLED)
        
        # 配置說明
        config_frame = ttk.Frame(help_notebook)
        help_notebook.add(config_frame, text="配置說明")
        
        config_text = scrolledtext.ScrolledText(config_frame, wrap=tk.WORD, font=('Helvetica', 11))
        config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        config_content = """
⚙️ 配置檔案說明和使用方法

📱 Claude Desktop 配置
位置: 
• macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
• Windows: %APPDATA%/Claude/claude_desktop_config.json

使用方法:
1. 將生成的配置內容複製到上述檔案
2. 重新啟動 Claude Desktop
3. 在對話中測試 MCP 工具是否正常工作

📝 VS Code 配置  
位置: 專案根目錄的 .vscode/mcp.json

使用方法:
1. 在 VS Code 專案中建立 .vscode 目錄 (如果不存在)
2. 建立 mcp.json 檔案並貼上配置內容
3. 重新載入 VS Code 視窗
4. 在 VS Code 的 MCP 整合中使用

📋 Cursor 配置
位置: Cursor 設定中的 MCP 區段

使用方法:
1. 開啟 Cursor 設定
2. 找到 MCP 相關設定區域
3. 貼上生成的配置內容
4. 儲存並重啟 Cursor

🐳 Docker Compose 配置
位置: 專案目錄的 docker-compose.yml

使用方法:
1. 將配置儲存為 docker-compose.yml
2. 在終端執行: docker-compose up -d
3. 使用 docker-compose logs 查看日誌
4. 使用 docker-compose down 停止服務

🔒 安全注意事項:
• 切勿在公開儲存庫中提交包含 API 金鑰的配置檔案
• 使用環境變數或 .env 檔案管理敏感資訊
• 定期更新和輪換 API 金鑰
• 啟用所有推薦的安全選項
        """
        
        config_text.insert(tk.INSERT, config_content.strip())
        config_text.config(state=tk.DISABLED)
        
        # 故障排除
        troubleshoot_frame = ttk.Frame(help_notebook)
        help_notebook.add(troubleshoot_frame, text="故障排除")
        
        troubleshoot_text = scrolledtext.ScrolledText(troubleshoot_frame, wrap=tk.WORD, font=('Helvetica', 11))
        troubleshoot_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        troubleshoot_content = """
🔧 常見問題和解決方案

❌ Docker 相關問題

問題: "找不到 Docker 命令"
解決: 
• 確認 Docker Desktop 已正確安裝
• 檢查 Docker 是否已加入系統 PATH
• 重新啟動終端或命令提示字元

問題: "Docker 已安裝但未運行"
解決:
• 啟動 Docker Desktop 應用程式
• 等待 Docker 服務完全啟動 (狀態列顯示綠色)
• 檢查系統資源是否足夠

問題: "容器無法啟動"
解決:
• 檢查環境變數是否正確設定
• 確認 API 金鑰有效且有適當權限
• 查看容器日誌: docker logs <container_name>

⚙️ 配置相關問題

問題: "Claude Desktop 無法識別 MCP 服務器"
解決:
• 檢查配置檔案語法是否正確 (使用 JSON 驗證器)
• 確認檔案路徑和名稱正確
• 重新啟動 Claude Desktop

問題: "VS Code 無法載入 MCP 配置"
解決:
• 確認 .vscode/mcp.json 檔案存在且語法正確
• 重新載入 VS Code 視窗 (Ctrl+Shift+P > Reload Window)
• 檢查 VS Code 版本是否支援 MCP

問題: "API 金鑰無效或權限不足"
解決:
• 重新生成 API 金鑰
• 檢查 API 金鑰的權限範圍
• 確認服務商額度未用完

🔒 安全相關問題

問題: "擔心 API 金鑰洩露"
解決:
• 使用環境變數而非硬編碼
• 定期輪換 API 金鑰
• 不在版本控制中提交敏感資訊
• 使用 .gitignore 排除配置檔案

問題: "容器權限過高"
解決:
• 啟用所有安全選項 (唯讀檔案系統、禁止權限提升等)
• 使用非 root 使用者運行容器
• 限制網路存取和資源使用

📞 獲得支援

如果問題仍未解決:
• 查看 Docker MCP 官方文檔
• 在 GitHub 討論區提問
• 檢查社群論壇和問答網站
• 聯繫相關服務商的技術支援
        """
        
        troubleshoot_text.insert(tk.INSERT, troubleshoot_content.strip())
        troubleshoot_text.config(state=tk.DISABLED)
        
    # 進階功能方法
    def add_volume(self):
        """添加卷掛載"""
        volume_dialog = tk.Toplevel(self.root)
        volume_dialog.title("添加卷掛載")
        volume_dialog.geometry("400x200")
        volume_dialog.transient(self.root) 
        volume_dialog.grab_set()
        
        ttk.Label(volume_dialog, text="主機路徑:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        host_var = tk.StringVar()
        host_entry = ttk.Entry(volume_dialog, textvariable=host_var, width=40)
        host_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(volume_dialog, text="容器路徑:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        container_var = tk.StringVar()
        container_entry = ttk.Entry(volume_dialog, textvariable=container_var, width=40)
        container_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(volume_dialog, text="模式:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        mode_var = tk.StringVar(value="rw")
        mode_combo = ttk.Combobox(volume_dialog, textvariable=mode_var, 
                                values=["rw", "ro"], width=37)
        mode_combo.grid(row=2, column=1, padx=10, pady=10)
        
        def add_volume_entry():
            host = host_var.get().strip()
            container = container_var.get().strip()
            mode = mode_var.get()
            
            if host and container:
                self.volume_tree.insert("", tk.END, values=(host, container, mode))
                volume_dialog.destroy()
            else:
                messagebox.showwarning("警告", "請填寫完整的路徑資訊")
                
        button_frame = ttk.Frame(volume_dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="確定", command=add_volume_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=volume_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def remove_volume(self):
        """移除選定的卷掛載"""
        selection = self.volume_tree.selection()
        if selection:
            self.volume_tree.delete(selection[0])
        else:
            messagebox.showwarning("警告", "請先選擇要移除的卷掛載")
            
    def browse_volume(self):
        """瀏覽選擇卷掛載路徑"""
        path = filedialog.askdirectory(title="選擇主機路徑")
        if path:
            # 這裡可以將路徑自動填入到添加卷掛載對話框
            messagebox.showinfo("路徑", f"選擇的路徑: {path}")


def main():
    """主函數 - 啟動應用程式"""
    try:
        # 檢查依賴項
        import yaml
    except ImportError:
        import tkinter.messagebox as mb
        mb.showwarning("缺少依賴", 
                      "缺少 PyYAML 模組，Docker Compose 配置功能將無法使用\n\n" +
                      "請執行以下命令安裝:\npip install PyYAML")
    
    # 建立主視窗
    root = tk.Tk()
    
    # 設定應用程式圖示 (如果有的話)
    try:
        # root.iconbitmap('mcp_icon.ico')  # 取消註解並提供圖示檔案
        pass
    except:
        pass
    
    # 建立應用程式實例
    app = MCPDockerConfigurator(root)
    
    # 設定關閉事件
    def on_closing():
        if messagebox.askokcancel("退出", "確定要退出 MCP Docker 配置器嗎?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 啟動主迴圈
    root.mainloop()


if __name__ == "__main__":
    main()
