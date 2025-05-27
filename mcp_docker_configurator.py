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

# 全域變數用於儲存從 JSON 載入的伺服器數據
MCP_SERVERS_DATA = []

def load_mcp_servers_from_catalog():
    """從 mcp_catalog.json 載入 MCP 伺服器數據"""
    global MCP_SERVERS_DATA
    try:
        with open('mcp_catalog.json', 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        
        # 檢查新格式 (version 2.0.0+)
        if isinstance(catalog_data, dict) and 'servers' in catalog_data:
            servers = catalog_data['servers']
        # 檢查舊格式
        elif isinstance(catalog_data, list):
            # 舊格式兼容
            servers = {server['id']: server for server in catalog_data}
        # 結構無效
        else:
            messagebox.showerror("錯誤", "mcp_catalog.json 檔案格式錯誤：結構無效，預期為列表或包含 'servers' 鍵的字典。")
            MCP_SERVERS_DATA = {}
            return {}
        
        MCP_SERVERS_DATA = servers
        return servers
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到 mcp_catalog.json 檔案！請確保該檔案存在於專案根目錄。")
        MCP_SERVERS_DATA = {}
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("錯誤", "mcp_catalog.json 檔案格式錯誤！")
        MCP_SERVERS_DATA = {}
        return {}

class MCPDockerConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 MCP Docker 配置器 Pro - 快速安全部署 Model Context Protocol")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f2f5')
        
        self.setup_styles()
        
        self.mcp_servers = load_mcp_servers_from_catalog()
        if not self.mcp_servers:
            self.root.quit()
            return
        
        # 核心狀態變數
        self.selected_servers = {}
        self.env_entries = {}
        self.volume_mounts = []
        self.transport_vars = {}  # 新增：傳輸協定變數
        
        # 配置變數
        self.docker_registry_var = tk.StringVar(value="mcp")
        self.network_mode_var = tk.StringVar(value="bridge")
        self.memory_limit_var = tk.StringVar(value="512m")
        self.cpu_limit_var = tk.StringVar(value="1.0")
        
        # 快速設定選項
        self.quick_setup_var = tk.StringVar(value="development")
        self.filesystem_paths_var = tk.StringVar(value="/workspace:/data:/home/user/projects")
        self.auto_best_practices_var = tk.BooleanVar(value=True)
        
        # 狀態追蹤
        self.current_step = 1
        self.total_steps = 4
        
        # 在 create_widgets 之前顯示快速指引
        self.create_widgets()

        # Defer data population and initial UI updates
        self.root.after(1, self.populate_server_list) 
        self.root.after(1, self.update_env_config)
        self.root.after(1, self.update_config_preview) # Ensure initial state of preview panes

        self.root.after(500, self.show_quick_start_guide)  # 延遲顯示指引
        
    def show_quick_start_guide(self):
        """顯示快速開始指引"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("🚀 快速開始指引")
        guide_window.geometry("600x500")
        guide_window.configure(bg='#f0f2f5')
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(guide_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="🚀 MCP Docker 配置器快速指引", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 步驟說明
        steps_text = """
❶ 選擇 MCP 服務器
   • 從左側列表選擇您需要的 MCP 服務器
   • 推薦：filesystem（檔案管理）、github（代碼管理）、postgres（數據庫）
   
❷ 配置環境變數
   • 系統會自動填入最佳實踐配置
   • filesystem 預設允許讀寫，支援多路徑配置
   • 可根據需要調整環境變數值
   
❸ 生成配置檔案
   • 選擇目標平台：Claude Desktop、VS Code、Cursor、Docker Compose
   • 系統會生成最佳化的安全配置
   • 自動應用 Docker 安全最佳實踐
   
❹ 部署和使用
   • 直接複製配置或儲存到檔案
   • 使用內建 Docker 狀態檢查工具
   • 一鍵安裝選定的服務器
        """
        
        steps_label = ttk.Label(main_frame, text=steps_text, justify=tk.LEFT, 
                               font=('Arial', 11))
        steps_label.pack(pady=(0, 20), anchor=tk.W)
        
        # 快速設定選項
        quick_frame = ttk.LabelFrame(main_frame, text="快速設定", padding=15)
        quick_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(quick_frame, text="預設環境：").pack(anchor=tk.W)
        env_frame = ttk.Frame(quick_frame)
        env_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(env_frame, text="開發環境（推薦）", 
                       variable=self.quick_setup_var, value="development").pack(anchor=tk.W)
        ttk.Radiobutton(env_frame, text="生產環境（高安全性）", 
                       variable=self.quick_setup_var, value="production").pack(anchor=tk.W)
        ttk.Radiobutton(env_frame, text="測試環境（最小權限）", 
                       variable=self.quick_setup_var, value="testing").pack(anchor=tk.W)
        
        ttk.Checkbutton(quick_frame, text="自動應用最佳實踐配置", 
                       variable=self.auto_best_practices_var).pack(anchor=tk.W, pady=5)
        
        # 底部按鈕
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="開始配置", 
                  command=lambda: [self.apply_quick_setup(), guide_window.destroy()],
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="跳過指引", 
                  command=guide_window.destroy).pack(side=tk.RIGHT)
    
    def apply_quick_setup(self):
        """應用快速設定"""
        setup_type = self.quick_setup_var.get()
        
        if setup_type == "development":
            # 開發環境：推薦常用的服務器
            recommended_servers = ["filesystem", "github", "fetch", "git"]
        elif setup_type == "production":
            # 生產環境：高安全性服務器
            recommended_servers = ["postgres", "memory", "sentry"]
        else:
            # 測試環境：輕量級服務器
            recommended_servers = ["sqlite", "time", "everything"]
        
        # 自動選擇推薦的服務器
        for server_id in recommended_servers:
            if server_id in self.mcp_servers:
                self.selected_servers[server_id] = True
        
        # 更新界面
        self.populate_server_list()
        self.update_env_config()
        
        # 顯示提示
        messagebox.showinfo("快速設定完成", 
                           f"已自動選擇 {setup_type} 環境推薦的 MCP 服務器。\n"
                           f"請繼續配置環境變數，然後生成配置檔案。")
        self.show_quick_start_guide()
        
    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam') # clam 主題通常比預設的更現代

        # --- 顏色定義 ---
        BG_COLOR = '#f0f2f5' # 更現代的淺灰背景
        FG_COLOR = '#333333' # 深灰色文字
        ACCENT_COLOR = '#0078d4' # 主題藍色 (類 VS Code)
        BUTTON_BG = '#0078d4'
        BUTTON_FG = '#ffffff'
        BUTTON_ACTIVE_BG = '#005a9e'
        TREE_HEADER_BG = '#e1e1e1'
        TREE_SELECTED_BG = '#cce4f7' # 淡藍色選中背景
        INPUT_BG = '#ffffff'
        INPUT_FG = '#333333'
        LABEL_FG = '#111111'
        STATUS_BAR_BG = '#0078d4'
        STATUS_BAR_FG = '#ffffff'

        self.root.configure(bg=BG_COLOR)

        # --- 通用樣式配置 ---
        style.configure('.', background=BG_COLOR, foreground=FG_COLOR, font=('Arial', 10)) # 使用 Arial 字體
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=LABEL_FG, font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), foreground=ACCENT_COLOR)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=FG_COLOR)
        style.configure('Category.TLabel', font=('Arial', 12, 'bold'), foreground=ACCENT_COLOR, padding=(0,10,0,5))

        # --- Notebook 樣式 ---
        style.configure('TNotebook', background=BG_COLOR, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10, 'bold'), foreground=FG_COLOR)
        style.map('TNotebook.Tab', 
                  background=[('selected', BG_COLOR)], 
                  foreground=[('selected', ACCENT_COLOR)],
                  expand=[('selected', [1, 1, 1, 0])]) # 選中 tab 視覺效果

        # --- Button 樣式 ---
        style.configure('TButton', font=('Arial', 10, 'bold'), 
                        background=BUTTON_BG, foreground=BUTTON_FG,
                        padding=(10, 5),
                        borderwidth=0, relief='flat')
        style.map('TButton', 
                  background=[('active', BUTTON_ACTIVE_BG), ('pressed', BUTTON_ACTIVE_BG)],
                  relief=[('pressed', 'flat'), ('active', 'flat')])
        
        style.configure('Accent.TButton', background=ACCENT_COLOR, foreground='#ffffff')
        style.map('Accent.TButton', background=[('active', '#005fba')])

        # --- Treeview 樣式 ---
        style.configure('Treeview', 
                        background=INPUT_BG, foreground=INPUT_FG, 
                        fieldbackground=INPUT_BG, rowheight=28, font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), 
                          background=TREE_HEADER_BG, foreground=FG_COLOR, relief='flat', padding=(5,5))
        style.map('Treeview.Heading', background=[('active', '#cccccc')])
        style.map('Treeview', background=[('selected', TREE_SELECTED_BG)], foreground=[('selected', FG_COLOR)])

        # --- Entry 和 ScrolledText (透過 Tkinter 設定) ---
        self.root.option_add("*TEntry*Font", ('Arial', 10))
        self.root.option_add("*TEntry*Background", INPUT_BG)
        self.root.option_add("*TEntry*Foreground", INPUT_FG)
        self.root.option_add("*TEntry*selectBackground", ACCENT_COLOR)
        self.root.option_add("*TEntry*selectForeground", 'white')
        self.root.option_add("*Text*Font", ('Arial', 10))
        self.root.option_add("*Text*Background", INPUT_BG)
        self.root.option_add("*Text*Foreground", INPUT_FG)
        self.root.option_add("*Text*selectBackground", ACCENT_COLOR)
        self.root.option_add("*Text*selectForeground", 'white')

        # --- LabelFrame 樣式 ---
        style.configure('TLabelframe', background=BG_COLOR, borderwidth=1, relief="groove", padding=10)
        style.configure('TLabelframe.Label', background=BG_COLOR, foreground=ACCENT_COLOR, font=('Arial', 11, 'bold'))

        # --- Checkbutton and Radiobutton ---
        style.configure('TCheckbutton', background=BG_COLOR, font=('Arial', 10))
        style.configure('TRadiobutton', background=BG_COLOR, font=('Arial', 10))

        # --- Scrollbar ---
        style.configure('Vertical.TScrollbar', background=BG_COLOR, troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=FG_COLOR)
        style.map('Vertical.TScrollbar', 
                  background=[('active', '#cccccc')], 
                  gripcount=[('pressed', 1)])
        
        # --- Status Bar (使用 tk.Label) ---
        self.status_bar_style = {
            'bg': STATUS_BAR_BG,
            'fg': STATUS_BAR_FG,
            'font': ('Arial', 10, 'bold'),
            'relief': tk.SUNKEN,
            'anchor': tk.W,
            'padx': 10
        }

    def create_widgets(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左側面板: 服務器選擇 和 環境變數
        left_pane_notebook = ttk.Notebook(main_pane, width=600) # 設定初始寬度
        main_pane.add(left_pane_notebook, weight=2) # 調整權重

        self.server_selection_frame = ttk.Frame(left_pane_notebook, padding=(10,10))
        left_pane_notebook.add(self.server_selection_frame, text=' ❶ 選擇服務器 ')
        self.create_server_selection_ui(self.server_selection_frame)

        self.env_config_frame_outer = ttk.Frame(left_pane_notebook, padding=(10,10))
        left_pane_notebook.add(self.env_config_frame_outer, text=' ❷ 環境變數 ')
        self.create_env_config_ui(self.env_config_frame_outer)

        # 右側面板: 配置生成, 進階設定, 使用說明
        right_pane_notebook = ttk.Notebook(main_pane)
        main_pane.add(right_pane_notebook, weight=3) # 調整權重

        self.config_generation_frame = ttk.Frame(right_pane_notebook, padding=(10,10))
        right_pane_notebook.add(self.config_generation_frame, text=' ❸ 配置生成 ')
        self.create_config_generation_ui(self.config_generation_frame)

        self.advanced_settings_frame = ttk.Frame(right_pane_notebook, padding=(10,10))
        right_pane_notebook.add(self.advanced_settings_frame, text=' ❹ 進階設定 ')
        self.create_advanced_settings_ui(self.advanced_settings_frame)

        self.help_frame = ttk.Frame(right_pane_notebook, padding=(10,10))
        right_pane_notebook.add(self.help_frame, text=' ❺ 使用說明 ')
        self.create_help_ui(self.help_frame)
        
        # --- 底部按鈕和狀態列 --- 
        bottom_frame = ttk.Frame(self.root, padding=(10,5))
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 左側按鈕
        left_button_frame = ttk.Frame(bottom_frame)
        left_button_frame.pack(side=tk.LEFT)

        ttk.Button(left_button_frame, text="🔍 檢查 Docker", command=self.check_docker, style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(left_button_frame, text="📥 安裝選定服務器", command=self.install_servers, style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(left_button_frame, text="🧹 清除所有", command=self.clear_all_selections, style='TButton').pack(side=tk.LEFT, padx=5)

        # 右側按鈕
        right_button_frame = ttk.Frame(bottom_frame)
        right_button_frame.pack(side=tk.RIGHT)

        ttk.Button(right_button_frame, text="💾 匯出設定", command=self.export_settings, style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(right_button_frame, text="📁 匯入設定", command=self.import_settings, style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(right_button_frame, text="❓ 說明", command=self.show_help_popup, style='TButton').pack(side=tk.LEFT, padx=5)

        # 初始化狀態變數
        self.status_var = tk.StringVar()
        self.status_var.set("MCP Docker 配置器 v1.1 - 就緒")
        
        self.status_label = tk.Label(self.root, text="就緒", **self.status_bar_style)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_server_selection_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        # 頂部搜尋與篩選
        filter_bar = ttk.Frame(parent_frame)
        filter_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0,15))
        
        ttk.Label(filter_bar, text="分類:").pack(side=tk.LEFT, padx=(0,5))
        categories = ["全部"] + sorted(list(set(s.get("category", "未分類") for s in self.mcp_servers.values())))
        self.category_var = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(filter_bar, textvariable=self.category_var, values=categories, 
                                      state="readonly", width=15, font=('Arial', 10))
        category_combo.pack(side=tk.LEFT, padx=(0,10))
        category_combo.bind("<<ComboboxSelected>>", self.filter_servers)
        
        ttk.Label(filter_bar, text="搜尋:").pack(side=tk.LEFT, padx=(0,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=20, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=(0,10))
        search_entry.bind("<KeyRelease>", self.filter_servers)

        # Treeview 顯示服務器列表
        tree_frame = ttk.Frame(parent_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('selected', 'name', 'category', 'description', 'image', 'official')
        self.server_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.server_tree.heading('selected', text='✓')
        self.server_tree.heading('name', text='名稱 (熱門度)')
        self.server_tree.heading('category', text='分類')
        self.server_tree.heading('description', text='描述與應用場景')
        self.server_tree.heading('image', text='Docker 映像')
        self.server_tree.heading('official', text='官方')

        self.server_tree.column('selected', width=30, anchor=tk.CENTER, stretch=False)
        self.server_tree.column('name', width=180, anchor=tk.W)
        self.server_tree.column('category', width=100, anchor=tk.W)
        self.server_tree.column('description', width=450, anchor=tk.W)
        self.server_tree.column('image', width=200, anchor=tk.W)
        self.server_tree.column('official', width=50, anchor=tk.CENTER, stretch=False)

        # 讓描述欄位可以換行顯示 (透過 tag configure)


        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.server_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.server_tree.xview)
        self.server_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.server_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # 綁定事件
        self.server_tree.bind("<Double-1>", self.toggle_server_selection)
        self.server_tree.bind("<Button-3>", self.show_server_context_menu)  # 右鍵選單
        self.server_tree.bind("<Button-1>", self.on_server_click) # 處理點擊選擇框

    
    def create_env_config_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(parent_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        self.env_scroll_frame = ttk.Frame(canvas)

        self.env_scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.env_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        

    def create_config_generation_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1) # 讓配置預覽區域可以擴展

        # --- 第一行：平台選擇和傳輸協定 ---
        top_controls_frame = ttk.Frame(parent_frame)
        top_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        platform_lf = ttk.LabelFrame(top_controls_frame, text="目標平台", padding=10)
        platform_lf.pack(side=tk.LEFT, padx=(0,10), fill=tk.Y)

        self.claude_var = tk.BooleanVar(value=True)
        self.vscode_var = tk.BooleanVar(value=False)
        self.cursor_var = tk.BooleanVar(value=False)
        self.compose_var = tk.BooleanVar(value=True)
        
        # 將平台變數添加到 platform_vars 字典中
        self.platform_vars = {
            "claude": self.claude_var,
            "vscode": self.vscode_var,
            "cursor": self.cursor_var,
            "compose": self.compose_var
        }

        ttk.Checkbutton(platform_lf, text="Claude Desktop", variable=self.claude_var, command=self.update_config_previews_visibility).pack(anchor=tk.W)
        ttk.Checkbutton(platform_lf, text="VS Code", variable=self.vscode_var, command=self.update_config_previews_visibility).pack(anchor=tk.W)
        ttk.Checkbutton(platform_lf, text="Cursor", variable=self.cursor_var, command=self.update_config_previews_visibility).pack(anchor=tk.W)
        ttk.Checkbutton(platform_lf, text="Docker Compose", variable=self.compose_var, command=self.update_config_previews_visibility).pack(anchor=tk.W)

        transport_lf = ttk.LabelFrame(top_controls_frame, text="傳輸協定 (影響 Claude/VSCode/Cursor)", padding=10)
        transport_lf.pack(side=tk.LEFT, padx=(0,10), fill=tk.Y)
        self.transport_config_var = tk.StringVar(value="stdio")
        ttk.Radiobutton(transport_lf, text="stdio (推薦本地)", variable=self.transport_config_var, value="stdio").pack(anchor=tk.W)
        ttk.Radiobutton(transport_lf, text="sse (需網路端口)", variable=self.transport_config_var, value="sse").pack(anchor=tk.W)
        
        security_lf = ttk.LabelFrame(top_controls_frame, text="安全選項 (影響 Claude/Compose)", padding=10)
        security_lf.pack(side=tk.LEFT, fill=tk.Y)

        self.security_options_vars = {
            "read_only": tk.BooleanVar(value=False),
            "no_new_privileges": tk.BooleanVar(value=False),
            "memory_limit_docker": tk.StringVar(value=""), # 給 docker compose
        }
        
        # 將安全變數添加到 security_vars 字典中
        self.security_vars = {
            "read_only": self.security_options_vars["read_only"],
            "no_privileges": self.security_options_vars["no_new_privileges"],
            "memory_limit": self.security_options_vars["memory_limit_docker"]
        }
        ttk.Checkbutton(security_lf, text="唯讀根檔案系統 (--read-only)", variable=self.security_options_vars["read_only"]).pack(anchor=tk.W)
        ttk.Checkbutton(security_lf, text="禁止權限提升 (--security-opt no-new-privileges)", variable=self.security_options_vars["no_new_privileges"]).pack(anchor=tk.W)
        mem_limit_frame = ttk.Frame(security_lf)
        mem_limit_frame.pack(anchor=tk.W)
        ttk.Label(mem_limit_frame, text="Compose 記憶體限制 (e.g., 512m):").pack(side=tk.LEFT)
        ttk.Entry(mem_limit_frame, textvariable=self.security_options_vars["memory_limit_docker"], width=10).pack(side=tk.LEFT)

        # --- 配置預覽 Notebook ---
        self.config_notebook = ttk.Notebook(parent_frame)
        self.config_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))

        self.config_texts = {}
        platforms_for_preview = {
            "claude": "Claude Desktop (claude_desktop_config.json)",
            "vscode": "VS Code (.vscode/mcp.json)",
            "cursor": "Cursor (MCP JSON)",
            "compose": "Docker Compose (docker-compose.yml)"
        }
        for key, title in platforms_for_preview.items():
            tab_frame = ttk.Frame(self.config_notebook, padding=5)
            self.config_notebook.add(tab_frame, text=f' {title} ') # 加空格讓 tab 看起來更好
            st = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, height=15, width=80, relief=tk.SOLID, borderwidth=1)
            st.pack(fill=tk.BOTH, expand=True)
            self.config_texts[key] = st
        
        self.update_config_previews_visibility() # 初始隱藏/顯示

        # --- 底部按鈕 ---
        action_buttons_frame = ttk.Frame(parent_frame)
        action_buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10,0))

        ttk.Button(action_buttons_frame, text="🚀 生成所有配置", command=self.generate_all_configs, style='Accent.TButton').pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(action_buttons_frame, text="💾 儲存當前配置", command=self.save_current_config).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(action_buttons_frame, text="📋 複製當前配置", command=self.copy_current_config_to_clipboard).pack(side=tk.LEFT)

    def create_advanced_settings_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        # parent_frame.rowconfigure(0, weight=1) # 讓內容可以擴展

        # Docker 設定
        docker_settings_lf = ttk.LabelFrame(parent_frame, text="Docker 設定", padding=15)
        docker_settings_lf.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0,15))
        docker_settings_lf.columnconfigure(1, weight=1)

        ttk.Label(docker_settings_lf, text="基礎映像登錄檔前綴:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(docker_settings_lf, textvariable=self.docker_registry_var, width=30).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(docker_settings_lf, text="網路模式 (Compose):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(docker_settings_lf, textvariable=self.network_mode_var, 
                       values=["bridge", "host", "none"], state="readonly", width=28).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        # 資源限制 (影響 Claude / VS Code / Cursor)
        resource_limits_lf = ttk.LabelFrame(parent_frame, text="容器資源限制 (影響 Claude/VSCode/Cursor)", padding=15)
        resource_limits_lf.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0,15))
        resource_limits_lf.columnconfigure(1, weight=1)

        ttk.Label(resource_limits_lf, text="記憶體限制 (e.g., 512m, 1g):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(resource_limits_lf, textvariable=self.memory_limit_var, width=30).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(resource_limits_lf, text="CPU 核心數限制 (e.g., 0.5, 1):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(resource_limits_lf, textvariable=self.cpu_limit_var, width=30).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        # 卷掛載 (影響所有，但主要透過 Compose 實現)
        volumes_lf = ttk.LabelFrame(parent_frame, text="卷掛載 (主要影響 Docker Compose)", padding=15)
        volumes_lf.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        volumes_lf.columnconfigure(0, weight=1)
        volumes_lf.rowconfigure(1, weight=1)

        # 添加卷的輸入區域
        add_volume_frame = ttk.Frame(volumes_lf)
        add_volume_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0,10))
        self.host_path_var = tk.StringVar()
        self.container_path_var = tk.StringVar()
        self.volume_mode_var = tk.StringVar(value="rw")

        ttk.Label(add_volume_frame, text="主機路徑:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Entry(add_volume_frame, textvariable=self.host_path_var, width=20).pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(add_volume_frame, text="容器路徑:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Entry(add_volume_frame, textvariable=self.container_path_var, width=20).pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(add_volume_frame, text="模式:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Combobox(add_volume_frame, textvariable=self.volume_mode_var, values=["rw", "ro"], state="readonly", width=5).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(add_volume_frame, text="➕ 新增掛載", command=self.add_volume_mount).pack(side=tk.LEFT)

        # 顯示已添加卷的列表
        self.volumes_listbox = tk.Listbox(volumes_lf, height=5, selectmode=tk.SINGLE, relief=tk.SOLID, borderwidth=1)
        self.volumes_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))
        ttk.Button(volumes_lf, text="➖ 移除選定掛載", command=self.remove_selected_volume_mount).grid(row=2, column=0, sticky=tk.W)
        self.refresh_volumes_listbox()

    def create_help_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        help_text_widget = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, padx=10, pady=10, font=('Arial', 10))
        help_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 載入 README.md 或特定說明內容
        readme_path = "README.md"
        help_content = """
        MCP Docker 配置器使用說明

        歡迎使用 MCP Docker 配置器！此工具旨在協助您輕鬆選擇、配置並生成適用於多個平台的 MCP Docker 服務器設定。

        主要步驟：
        1.  **選擇服務器 (❶)**：
            *   瀏覽左上角的服務器列表。
            *   使用「分類」下拉選單或「搜尋」框來篩選服務器。
            *   雙擊服務器或點擊其名稱前的核取方塊來選擇。
            *   右鍵點擊服務器可查看更多選項，如開啟文檔或複製映像名稱。

        2.  **環境變數 (❷)**：
            *   當您選擇服務器後，如果該服務器需要環境變數 (如 API 金鑰)，則會在此面板顯示輸入欄位。
            *   請填寫必要的資訊。包含 "token", "key" 的敏感欄位會自動隱藏輸入內容。

        3.  **配置生成 (❸)**：
            *   選擇您想要為哪些平台 (Claude Desktop, VS Code, Cursor, Docker Compose) 生成配置。
            *   選擇傳輸協定 (stdio 或 sse)。
            *   設定安全選項，如唯讀檔案系統、記憶體限制等。
            *   點擊「生成所有配置」按鈕，預覽會在下方的分頁中顯示。
            *   您可以「儲存當前配置」到檔案或「複製當前配置」到剪貼簿。

        4.  **進階設定 (❹)**：
            *   設定 Docker 基礎映像登錄檔前綴 (預設為 docker.io)。
            *   為 Docker Compose 設定網路模式。
            *   為 Claude/VSCode/Cursor 設定容器的記憶體和 CPU 限制。
            *   管理卷掛載 (主要影響 Docker Compose)。

        5.  **使用說明 (❺)**：
            *   此面板提供本工具的快速指南和提示。
            *   您也可以點擊主視窗右下角的「❓ 說明」按鈕查看更詳細的彈出式說明。

        底部按鈕功能：
        *   **檢查 Docker**：確認 Docker 是否已安裝並正在運行。
        *   **安裝選定服務器**：自動從 Docker Hub 下載您選擇的服務器的最新映像。
        *   **清除所有**：取消所有服務器選擇並清空環境變數等設定。
        *   **匯出設定**：將您當前的選擇和設定儲存到一個 JSON 檔案中，方便日後匯入。
        *   **匯入設定**：從之前匯出的 JSON 檔案載入設定。

        提示：
        *   在服務器列表上右鍵點擊單個服務器，可以快速複製其 Docker 映像名稱或開啟其官方文檔連結。
        *   「熱門度」欄位可以幫助您了解哪些服務器較常被使用。
        *   生成的配置文件名和建議存放路徑會在「使用說明」或儲存時提示。
        *   建議定期檢查並更新您的 Docker 映像以獲取最新功能和安全修補。

        如果您在專案根目錄下有名為 README.md 的檔案，這裡會優先顯示該檔案的內容。
        """
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                help_text_widget.insert(tk.INSERT, readme_content)
            except Exception as e:
                help_text_widget.insert(tk.INSERT, f"無法讀取 README.md: {e}\n\n{help_content.strip()}")
        else:
            help_text_widget.insert(tk.INSERT, help_content.strip())
        help_text_widget.config(state=tk.DISABLED)
        
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
            if category_filter != "全部" and info.get("category") != category_filter:
                continue
                
            # 搜尋篩選  
            if search_term and not any(search_term in text.lower() for text in [
                server_id, info.get("name", ""), info.get("description", ""), info.get("category", "") , info.get("popularity", "")
            ]):
                continue
                
            # 創建精緻的標籤和顯示
            selected = "✅" if server_id in self.selected_servers else "⬜"
            
            # 安全級別標籤
            security_level = info.get("security_level", "medium")
            security_emoji = {"high": "🔒", "medium": "🔐", "low": "🔓"}.get(security_level, "🔐")
            
            # Docker 需求標籤
            docker_required = info.get("docker_required", True)
            docker_emoji = "🐳" if docker_required else "📦"
            
            # 熱門程度標籤
            popularity = info.get("popularity", "中等")
            popularity_emoji = {"極高": "🔥", "高": "⭐", "中等": "🌟", "低": "💫"}.get(popularity, "🌟")
            
            # 官方標籤
            official_emoji = "🏛️" if info.get("official", False) else ""
            
            # 組合名稱顯示
            name_with_tags = f"{info.get('name', 'N/A')} {security_emoji}{docker_emoji}{popularity_emoji}{official_emoji}"
            
            # 顯示應用場景 - 新增
            use_cases = info.get("use_cases", [])
            use_cases_str = "、".join(use_cases[:3])  # 只顯示前3個應用場景
            if len(use_cases) > 3:
                use_cases_str += "..."
                
            description_with_use_cases = f"{info.get('description', '')}\n🎯 應用: {use_cases_str}"

            # 插入項目，包含精緻標籤
            item_id = self.server_tree.insert("", tk.END, iid=server_id, values=(
                selected, 
                name_with_tags, 
                info.get("category", "N/A"), 
                description_with_use_cases,
                info.get("image", "N/A")
            ))
            
            # 根據安全級別設定顏色
            if security_level == "high":
                self.server_tree.set(item_id, "name", name_with_tags)
                # 可以添加標籤來設定不同的顏色
                self.server_tree.item(item_id, tags=("high_security",))
            elif security_level == "low":
                self.server_tree.item(item_id, tags=("low_security",))
            
        # 配置標籤顏色
        self.server_tree.tag_configure("high_security", background="#ffe6e6")  # 淺紅色背景
        self.server_tree.tag_configure("low_security", background="#e6ffe6")   # 淺綠色背景
        
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
            column = self.server_tree.identify("column", event.x, event.y)
            if column == "#1":  # 選擇欄位
                self.toggle_server_selection(event)
                
    def show_server_context_menu(self, event):
        """顯示服務器右鍵選單"""
        item = self.server_tree.identify_row(event.y)
        if not item:
            return
            
        context_menu = tk.Menu(self.root, tearoff=0)
        server_info = self.mcp_servers.get(item)
        if not server_info: return # 如果找不到服務器資訊則返回
        
        context_menu.add_command(label=f"📋 複製映像名稱: {server_info.get('image', 'N/A')}", 
                               command=lambda: self.copy_to_clipboard(server_info.get('image', '')))
        context_menu.add_command(label=f"🌐 開啟文檔: {server_info.get('url', '#')}", 
                               command=lambda: webbrowser.open(server_info.get('url', '#')) if server_info.get('url') else None)
        context_menu.add_separator()
        
        # 新增：顯示應用場景
        use_cases = server_info.get('use_cases', [])
        if use_cases:
            use_cases_menu = tk.Menu(context_menu, tearoff=0)
            for uc in use_cases:
                use_cases_menu.add_command(label=uc, state=tk.DISABLED) # 應用場景不可點擊
            context_menu.add_cascade(label="💡 主要應用場景", menu=use_cases_menu)
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
            # 顯示環境變數管理說明
            info_frame = ttk.LabelFrame(self.env_scroll_frame, text="🔧 環境變數管理說明", padding=15)
            info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=5)
            
            info_text = """
📋 環境變數儲存和管理方式：

🔐 安全儲存：
  • API 金鑰等敏感資訊不會儲存在配置檔案中
  • 匯出設定時敏感資訊會被隱藏處理
  • 建議使用系統環境變數或 .env 檔案管理

💾 配置方式：
  1. 系統環境變數（推薦生產環境）
  2. .env 檔案（適合開發環境）
  3. Docker secrets（適合 Docker Compose）
  4. 外部密鑰管理服務（如 HashiCorp Vault）

🔄 修改環境變數：
  • 修改系統環境變數後重啟應用
  • 更新 .env 檔案內容
  • 使用「匯入設定」功能載入新配置
  • 重新配置並生成新的配置檔案

💡 最佳實踐：
  • 定期輪換 API 金鑰
  • 不要在版本控制中提交敏感資訊
  • 使用最小權限原則設定 API 金鑰權限
  • 為不同環境（開發/測試/生產）使用不同的金鑰
            """
            
            ttk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                     font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W)
            
            # 顯示選擇提示
            select_frame = ttk.Frame(self.env_scroll_frame)
            select_frame.grid(row=1, column=0, pady=20)
            ttk.Label(select_frame, text="👈 請先在左側選擇 MCP 服務器開始配置", 
                     style='Header.TLabel', font=('Arial', 12)).pack()
            return
            
        row = 0
        # 添加環境變數管理說明標題
        title_frame = ttk.Frame(self.env_scroll_frame)
        title_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10), padx=5)
        ttk.Label(title_frame, text="🔧 環境變數配置", style='Category.TLabel').pack(side=tk.LEFT)
        ttk.Button(title_frame, text="💡 管理說明", 
                  command=self.show_env_management_help).pack(side=tk.RIGHT)
        row += 1
        
        for server_id, server_info in self.selected_servers.items():
            # 服務器標題
            server_frame = ttk.LabelFrame(self.env_scroll_frame, 
                                        text=f"{server_info['name']} ({server_info['image']})", 
                                        padding="10")
            server_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
            
            # 環境變數輸入
            env_row = 0
            if server_info.get("environment_vars"):
                for env_var, default_value in server_info["environment_vars"].items():
                    ttk.Label(server_frame, text=f"{env_var}:", style='Header.TLabel').grid(
                        row=env_row, column=0, sticky=tk.W, pady=5)
                    
                    # 判斷是否為敏感資訊
                    is_sensitive = any(keyword in env_var.lower() for keyword in ["token", "key", "secret", "password"])
                    entry = ttk.Entry(server_frame, width=50, show="*" if is_sensitive else None)
                    entry.grid(row=env_row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
                    
                    # 預填預設值（除了敏感資訊）
                    if not is_sensitive and default_value and default_value != "your_token_here":
                        entry.insert(0, default_value)
                    
                    self.env_entries[f"{server_id}.{env_var}"] = entry
                    env_row += 1
            
            # 如果沒有環境變數需求，顯示提示
            if env_row == 0:
                ttk.Label(server_frame, text="✅ 此服務器無需環境變數配置", 
                         style='Header.TLabel').grid(row=0, column=0, pady=10)
                
            server_frame.columnconfigure(1, weight=1)
            row += 1
            
        self.env_scroll_frame.columnconfigure(0, weight=1)
        
    def show_env_management_help(self):
        """顯示環境變數管理幫助"""
        help_window = tk.Toplevel(self.root)
        help_window.title("🔧 環境變數管理說明")
        help_window.geometry("700x600")
        help_window.transient(self.root)
        help_window.grab_set()
        
        main_frame = ttk.Frame(help_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        ttk.Label(main_frame, text="🔧 環境變數管理完整指南", 
                 style='Title.TLabel').pack(pady=(0, 15))
        
        # 說明內容
        help_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=25, width=70,
                                             font=('Arial', 11))
        help_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        content = """
🔐 安全性原則

環境變數包含 API 金鑰等敏感資訊，需要妥善管理：
• 永遠不要在程式碼或配置檔案中硬編碼敏感資訊
• 使用環境變數、.env 檔案或專業的密鑰管理服務
• 定期輪換 API 金鑰和令牌
• 為不同環境使用不同的憑證

💾 儲存方式

1. 系統環境變數（推薦生產環境）
   Windows: 
   set GITHUB_PERSONAL_ACCESS_TOKEN=your_token
   setx GITHUB_PERSONAL_ACCESS_TOKEN your_token  # 永久設置
   
   macOS/Linux:
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token
   echo 'export GITHUB_PERSONAL_ACCESS_TOKEN=your_token' >> ~/.bashrc

2. .env 檔案（適合開發環境）
   在專案根目錄創建 .env 檔案：
   GITHUB_PERSONAL_ACCESS_TOKEN=your_token
   SLACK_BOT_TOKEN=xoxb-your-token
   DATABASE_URI=postgresql://user:pass@localhost/db

3. Docker Compose 環境檔案
   創建 .env 檔案供 docker-compose.yml 使用：
   GITHUB_TOKEN=your_token
   然後在 docker-compose.yml 中引用：
   environment:
     - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}

4. Docker Secrets（生產環境）
   echo "your_token" | docker secret create github_token -
   在 docker-compose.yml 中使用：
   secrets:
     - github_token

🔄 修改和更新

當需要更新環境變數時：

1. 更新環境變數值
2. 重啟相關的 Docker 容器或應用程式
3. 驗證新的配置是否生效
4. 更新備份和文檔

對於此工具：
1. 修改環境變數後
2. 重新選擇服務器並輸入新值
3. 重新生成配置檔案
4. 使用新配置重新部署

🛡️ 最佳實踐

• 使用專業的密鑰管理服務（如 HashiCorp Vault、AWS Secrets Manager）
• 實施密鑰輪換策略
• 監控 API 金鑰的使用情況
• 為每個服務使用最小權限的 API 金鑰
• 在 .gitignore 中排除 .env 檔案
• 定期審查和清理未使用的憑證

📁 檔案位置建議

開發環境：
  專案根目錄/.env
  ~/.bashrc 或 ~/.zshrc

生產環境：
  Docker secrets
  Kubernetes secrets
  雲端密鑰管理服務

💡 故障排除

如果環境變數無法讀取：
1. 檢查變數名稱是否正確
2. 確認環境變數已正確設置
3. 重啟終端或應用程式
4. 檢查 Docker 容器是否正確掛載環境變數
5. 查看應用程式日誌獲取更多資訊
        """
        
        help_text.insert(tk.INSERT, content.strip())
        help_text.config(state=tk.DISABLED)
        
        # 關閉按鈕
        ttk.Button(main_frame, text="關閉", 
                  command=help_window.destroy).pack(pady=(10, 0))
    
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
            if self.security_vars.get("read_only", tk.BooleanVar(value=False)).get():
                server_config["args"].extend(["--read-only"])
            if self.security_vars.get("no_privileges", tk.BooleanVar(value=False)).get():
                server_config["args"].extend(["--security-opt", "no-new-privileges"])
            
            # 記憶體限制
            memory_limit = self.memory_limit_var.get()
            if memory_limit and memory_limit != "":
                server_config["args"].extend(["--memory", memory_limit])
            
            # CPU 限制  
            cpu_limit = self.cpu_limit_var.get()
            if cpu_limit and cpu_limit != "":
                server_config["args"].extend(["--cpus", cpu_limit])
                
            # 環境變數
            env_vars = {}
            if server_info.get("environment_vars"):
                for env_var in server_info["environment_vars"].keys():
                    key = f"{server_id}.{env_var}"
                    if key in self.env_entries:
                        value = self.env_entries[key].get()
                        if value:
                            server_config["args"].extend(["-e", f"{env_var}={value}"])
                            env_vars[env_var] = value
            
            # 卷掛載
            if server_info.get("volumes"):
                for volume in server_info["volumes"]:
                    server_config["args"].extend(["-v", volume])
                        
            # 添加映像名稱
            server_config["args"].append(server_info["image"])
                
            config["mcpServers"][server_id] = server_config
            
        return json.dumps(config, indent=2, ensure_ascii=False)
        
    def generate_vscode_config(self):
        """生成 VS Code 配置"""
        inputs = []
        servers = {}
        
        # 收集所有環境變數輸入
        for server_id, server_info in self.selected_servers.items():
            if server_info.get("environment_vars"):
                for env_var in server_info["environment_vars"].keys():
                    input_id = f"{server_id}_{env_var.lower()}"
                    inputs.append({
                        "type": "promptString",
                        "id": input_id,
                        "description": f"{server_info['name']} {env_var}",
                        "password": any(keyword in env_var.lower() for keyword in ["token", "key", "secret", "password"])
                    })
                
        # 生成服務器配置
        for server_id, server_info in self.selected_servers.items():
            server_config = {
                "command": "docker",
                "args": ["run", "-i", "--rm"]
            }
            
            # 安全選項
            if self.security_vars.get("read_only", tk.BooleanVar(value=False)).get():
                server_config["args"].extend(["--read-only"])
                
            # 環境變數處理
            if server_info.get("environment_vars"):
                for env_var in server_info["environment_vars"].keys():
                    input_id = f"{server_id}_{env_var.lower()}"
                    server_config["args"].extend(["-e", f"{env_var}=${{input:{input_id}}}"])
                
            server_config["args"].append(server_info["image"])
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
            if server_info.get("environment_vars"):
                for env_var in server_info["environment_vars"].keys():
                    key = f"{server_id}.{env_var}"
                    if key in self.env_entries:
                        value = self.env_entries[key].get()
                        if value:
                            env_vars[env_var] = value
                        else:
                            env_vars[env_var] = f"<YOUR_{env_var}_HERE>"
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
            if self.security_vars.get("no_privileges", tk.BooleanVar(value=False)).get():
                security_opts.append("no-new-privileges:true")
                
            if security_opts:
                service_config["security_opt"] = security_opts
                
            if self.security_vars.get("read_only", tk.BooleanVar(value=False)).get():
                service_config["read_only"] = True
                service_config["tmpfs"] = ["/tmp"]
                
            # 資源限制
            memory_limit = self.security_vars.get("memory_limit", tk.StringVar()).get()
            if memory_limit and memory_limit.strip():
                service_config["mem_limit"] = memory_limit
            elif self.memory_limit_var.get():
                service_config["mem_limit"] = self.memory_limit_var.get()
                
            # 環境變數
            env_vars = []
            if server_info.get("environment_vars"):
                for env_var in server_info["environment_vars"].keys():
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
            if server_info.get("default_ports"):
                # 確保端口是字串列表
                ports_to_map = [str(p) for p in server_info["default_ports"]]
                service_config["ports"] = [f"{port}:{port}" for port in ports_to_map]
            
            # 卷掛載
            if server_info.get("volumes"):
                service_config["volumes"] = server_info["volumes"]
                
            config["services"][f"{server_id}-mcp"] = service_config
            
        return yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
    # 輔助功能方法
    def check_docker_status(self):
        """檢查 Docker 狀態"""
        try:
            # 檢查 Docker 版本
            version_result = subprocess.run(["docker", "--version"], 
                                          capture_output=True, text=True, timeout=5, check=True) # Add check=True
            version = version_result.stdout.strip()
            
            # 檢查 Docker 是否運行
            info_result = subprocess.run(["docker", "info"], 
                                       capture_output=True, text=True, timeout=5, check=True) # Add check=True
            
            # 檢查 MCP 映像 (This command is less critical, so direct error if it fails might be too much, but check=True can be used if needed)
            images_result = subprocess.run(["docker", "images", "--filter", "reference=mcp/*"], 
                                           capture_output=True, text=True, timeout=5, check=True)
            mcp_images = len(images_result.stdout.strip().split('\n')) - 1  # 減去標題行
            
            messagebox.showinfo("Docker 狀態", 
                              f"✅ Docker 正常運行\n{version}\n\n📦 已安裝 {mcp_images} 個 MCP 映像")
            self.status_var.set(f"Docker 正常運行 - {mcp_images} 個 MCP 映像")
            return True
            
        except subprocess.CalledProcessError as e:
            error_message = f"Docker 命令執行失敗: {e.cmd}\n錯誤碼: {e.returncode}\n輸出:\n{e.stderr or e.stdout}"
            messagebox.showerror("Docker 錯誤", error_message)
            self.status_var.set("Docker 命令錯誤")
        except subprocess.TimeoutExpired:
            messagebox.showerror("錯誤", "檢查 Docker 狀態超時")
            self.status_var.set("檢查 Docker 超時")
        except FileNotFoundError:
            messagebox.showerror("錯誤", "找不到 Docker 命令。\n請確認 Docker 已正確安裝並在系統 PATH 中。")
            self.status_var.set("Docker 未安裝")
        except Exception as e:
            messagebox.showerror("錯誤", f"檢查 Docker 時發生未預期錯誤:\n{str(e)}")
            self.status_var.set("檢查 Docker 失敗")
            
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
                        universal_newlines=True,
                        errors='replace' # Handle potential encoding errors in output
                    )
                    
                    # 即時顯示輸出
                    for line in process.stdout: # type: ignore
                        log_text.insert(tk.END, line)
                        log_text.see(tk.END)
                        progress_window.update()
                        
                    process.wait(timeout=300) # Add a timeout (e.g., 5 minutes per image)
                    
                    if process.returncode == 0:
                        log_text.insert(tk.END, f"✅ {server_info['name']} ({server_info['image']}) 安裝成功!\n")
                        success_count += 1
                    else:
                        log_text.insert(tk.END, f"❌ {server_info['name']} ({server_info['image']}) 安裝失敗! Docker 返回碼: {process.returncode}\n")
                        
                except FileNotFoundError:
                    log_text.insert(tk.END, f"❌ Docker 命令 'docker pull' 未找到。請檢查 Docker 是否正確安裝。\n")
                    # Potentially stop further processing if docker is not found
                    progress_label.config(text="Docker 命令未找到")
                    break 
                except subprocess.TimeoutExpired:
                    log_text.insert(tk.END, f"❌ {server_info['name']} ({server_info['image']}) 安裝超時。\n")
                    if process: process.kill() # Ensure the process is killed on timeout
                except Exception as e:
                    log_text.insert(tk.END, f"❌ {server_info['name']} ({server_info['image']}) 安裝時發生未預期錯誤: {str(e)}\n")
                    
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
        
        error_messages = []
        for platform, config_content in configs.items():
            if config_content and self.platform_vars.get(platform, tk.BooleanVar()).get():
                file_path = os.path.join(save_dir, file_names[platform])
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(config_content)
                    saved_files.append(file_names[platform])
                except (IOError, OSError) as e:
                    error_msg = f"無法儲存檔案 '{file_names[platform]}':\n{e}"
                    messagebox.showerror("儲存錯誤", error_msg)
                    error_messages.append(error_msg)
                except Exception as e: # Catch any other unexpected error during write
                    error_msg = f"儲存檔案 '{file_names[platform]}' 時發生未預期錯誤:\n{e}"
                    messagebox.showerror("儲存錯誤", error_msg)
                    error_messages.append(error_msg)
                    
        if saved_files and not error_messages:
            messagebox.showinfo("成功", f"已成功儲存以下配置檔案:\n\n" + "\n".join(f"• {f}" for f in saved_files))
            self.status_var.set(f"已儲存 {len(saved_files)} 個配置檔案")
        elif saved_files and error_messages:
            messagebox.showwarning("部分成功", 
                                 f"已儲存 {len(saved_files)} 個檔案, 但以下檔案儲存失敗:\n\n" + 
                                 "\n".join(error_messages))
            self.status_var.set(f"部分配置儲存成功，{len(error_messages)} 個失敗")
        elif not saved_files and error_messages:
            messagebox.showerror("全部失敗", 
                               f"所有檔案儲存失敗:\n\n" + 
                               "\n".join(error_messages))
            self.status_var.set("所有配置儲存失敗")
        else: # No files selected or generated for saving
            messagebox.showwarning("警告", "沒有需要儲存的配置檔案。")
            self.status_var.set("沒有配置被儲存")
            
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
                "memory": self.memory_limit_var.get(),
                "cpu": self.cpu_limit_var.get(),
                "network": self.network_mode_var.get()
            },
            "quick_setup": self.quick_setup_var.get(),
            "auto_best_practices": self.auto_best_practices_var.get()
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
                messagebox.showinfo("成功", f"設定已成功匯出到:\n{filename}")
                self.status_var.set("設定已匯出")
            except (IOError, OSError) as e:
                messagebox.showerror("匯出錯誤", f"無法寫入檔案 '{filename}':\n{e}")
                self.status_var.set("匯出設定失敗")
            except Exception as e: # Catch any other unexpected error during export
                messagebox.showerror("匯出錯誤", f"匯出設定時發生未預期錯誤:\n{str(e)}")
                self.status_var.set("匯出設定失敗")
                
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
        except (IOError, OSError) as e:
            messagebox.showerror("匯入錯誤", f"無法讀取檔案 '{filename}':\n{e}")
            self.status_var.set("匯入設定失敗 - 檔案讀取錯誤")
            return
        except json.JSONDecodeError as e:
            messagebox.showerror("匯入錯誤", f"檔案 '{filename}' 不是有效的 JSON 格式:\n{e}")
            self.status_var.set("匯入設定失敗 - JSON 格式錯誤")
            return
        except Exception as e: # Catch any other unexpected error during load
            messagebox.showerror("匯入錯誤", f"匯入設定時發生未預期錯誤:\n{str(e)}")
            self.status_var.set("匯入設定失敗 - 未預期錯誤")
            return

        # Proceed with applying settings if loading was successful
        try:
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
            self.memory_limit_var.set(resource_settings.get("memory", "512m"))
            self.cpu_limit_var.set(resource_settings.get("cpu", "1.0"))
            self.network_mode_var.set(resource_settings.get("network", "bridge"))
            
            # 更新UI
            self.populate_server_list()
            self.update_env_config()
            self.update_config_preview()
            
            messagebox.showinfo("成功", f"已成功匯入設定:\n• {len(self.selected_servers)} 個服務器\n• 平台和安全設定")
            self.status_var.set(f"已匯入 {len(self.selected_servers)} 個服務器設定")
            
        except Exception as e: # Catch errors during the application of settings
            messagebox.showerror("設定應用錯誤", f"套用匯入的設定時發生錯誤:\n{str(e)}")
            self.status_var.set("套用匯入設定失敗")
            
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
        filename = filedialog.askopenfilename(title="選擇檔案路徑")
        if filename:
            self.host_path_var.set(filename)

    def update_config_previews_visibility(self):
        """根據平台選擇更新配置預覽的可見性"""
        pass  # 現在只是一個占位符
    
    def check_docker(self):
        """檢查 Docker 狀態"""
        self.check_docker_status()
    
    def install_servers(self):
        """安裝選定的服務器"""
        self.install_selected_servers()
    
    def save_current_config(self):
        """儲存當前配置"""
        self.save_all_configs()
    
    def copy_current_config_to_clipboard(self):
        """複製當前配置到剪貼簿"""
        self.copy_configs()
    
    def add_volume_mount(self):
        """添加卷掛載"""
        host_path = self.host_path_var.get().strip()
        container_path = self.container_path_var.get().strip()
        mode = self.volume_mode_var.get()
        
        if host_path and container_path:
            volume_entry = f"{host_path}:{container_path}:{mode}"
            self.volumes_listbox.insert(tk.END, volume_entry)
            self.host_path_var.set("")
            self.container_path_var.set("")
        else:
            messagebox.showwarning("警告", "請輸入主機路徑和容器路徑")
    
    def remove_selected_volume_mount(self):
        """移除選定的卷掛載"""
        selection = self.volumes_listbox.curselection()
        if selection:
            self.volumes_listbox.delete(selection[0])
        else:
            messagebox.showwarning("警告", "請先選擇要移除的卷掛載")
    
    def refresh_volumes_listbox(self):
        """刷新卷掛載列表"""
        pass  # 現在只是一個占位符
    
    def show_help_popup(self):
        """顯示說明彈出視窗"""
        self.show_detailed_help()

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
