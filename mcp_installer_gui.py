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
import yaml # 新增，用於生成 docker-compose.yml

# 全域變數用於儲存從 JSON 載入的伺服器數據
MCP_SERVERS_DATA = []

def load_mcp_servers_from_catalog():
    """從 mcp_catalog.json 載入 MCP 伺服器數據"""
    global MCP_SERVERS_DATA
    try:
        with open('mcp_catalog.json', 'r', encoding='utf-8') as f:
            catalog_data = json.load(f) # Load into a temporary variable

        if isinstance(catalog_data, dict) and 'servers' in catalog_data:
            # New format: catalog_data is a dict with a 'servers' key
            actual_servers_dict = catalog_data['servers']
            MCP_SERVERS_DATA = actual_servers_dict 
            return actual_servers_dict
        elif isinstance(catalog_data, list):
            # Old format: catalog_data is a list of server objects
            # Ensure each item is a dict with an 'id' before processing
            actual_servers_dict = {
                server['id']: server 
                for server in catalog_data 
                if isinstance(server, dict) and 'id' in server
            }
            # Check if the conversion resulted in an empty dict from a non-empty list,
            # which might indicate malformed list items.
            if not actual_servers_dict and catalog_data:
                 messagebox.showerror("錯誤", "mcp_catalog.json 檔案格式錯誤：列表中的項目無效。")
                 MCP_SERVERS_DATA = {}
                 return {}
            MCP_SERVERS_DATA = actual_servers_dict
            return actual_servers_dict
        else:
            # Invalid structure
            messagebox.showerror("錯誤", "mcp_catalog.json 檔案格式錯誤：結構無效，預期為列表或包含 'servers' 鍵的字典。")
            MCP_SERVERS_DATA = {}
            return {}

    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到 mcp_catalog.json 檔案！請確保該檔案存在於專案根目錄。")
        MCP_SERVERS_DATA = {}
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("錯誤", "mcp_catalog.json 檔案格式錯誤！")
        MCP_SERVERS_DATA = {}
        return {}

class MCPInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Docker 安裝器 - 簡約版")
        self.root.geometry("1250x850") # 調整視窗大小
        
        self.setup_styles()
        
        self.mcp_servers = load_mcp_servers_from_catalog()
        if not self.mcp_servers:
            self.root.quit()
            return
        
        self.selected_servers = {}
        self.env_entries = {}
        
        self.create_widgets()
        self.update_status_bar("就緒")

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        BG_COLOR = '#f0f2f5' 
        FG_COLOR = '#333333' 
        ACCENT_COLOR = '#0078d4' 
        BUTTON_BG = '#0078d4'
        BUTTON_FG = '#ffffff'
        BUTTON_ACTIVE_BG = '#005a9e'
        TREE_HEADER_BG = '#e1e1e1'
        TREE_SELECTED_BG = '#cce4f7' 
        INPUT_BG = '#ffffff'
        INPUT_FG = '#333333'
        LABEL_FG = '#111111'
        STATUS_BAR_BG = '#0078d4'
        STATUS_BAR_FG = '#ffffff'

        self.root.configure(bg=BG_COLOR)

        style.configure('.', background=BG_COLOR, foreground=FG_COLOR, font=('Arial', 10))
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=LABEL_FG, font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), foreground=ACCENT_COLOR)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=FG_COLOR, anchor=tk.CENTER)

        style.configure('TNotebook', background=BG_COLOR, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10, 'bold'), foreground=FG_COLOR)
        style.map('TNotebook.Tab', 
                  background=[('selected', BG_COLOR)], 
                  foreground=[('selected', ACCENT_COLOR)],
                  expand=[('selected', [1, 1, 1, 0])])

        style.configure('TButton', font=('Arial', 10, 'bold'), 
                        background=BUTTON_BG, foreground=BUTTON_FG,
                        padding=(10, 5),
                        borderwidth=0, relief='flat')
        style.map('TButton', 
                  background=[('active', BUTTON_ACTIVE_BG), ('pressed', BUTTON_ACTIVE_BG)],
                  relief=[('pressed', 'flat'), ('active', 'flat')])
        style.configure('Accent.TButton', background=ACCENT_COLOR, foreground='#ffffff') # For primary action buttons
        style.map('Accent.TButton', background=[('active', '#005fba')])

        style.configure('Treeview', 
                        background=INPUT_BG, foreground=INPUT_FG, 
                        fieldbackground=INPUT_BG, rowheight=28, font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), 
                          background=TREE_HEADER_BG, foreground=FG_COLOR, relief='flat', padding=(5,5))
        style.map('Treeview.Heading', background=[('active', '#cccccc')])
        style.map('Treeview', background=[('selected', TREE_SELECTED_BG)], foreground=[('selected', FG_COLOR)])

        self.root.option_add("*TEntry*Font", ('Arial', 10))
        self.root.option_add("*Text*Font", ('Arial', 10))
        self.root.option_add("*Text*Background", INPUT_BG)
        self.root.option_add("*Text*selectBackground", ACCENT_COLOR)

        style.configure('TLabelframe', background=BG_COLOR, borderwidth=1, relief="groove", padding=10)
        style.configure('TLabelframe.Label', background=BG_COLOR, foreground=ACCENT_COLOR, font=('Arial', 11, 'bold'))
        
        self.status_bar_style = {
            'bg': STATUS_BAR_BG,
            'fg': STATUS_BAR_FG,
            'font': ('Arial', 10, 'bold'),
            'relief': tk.SUNKEN,
            'anchor': tk.W,
            'padx': 10
        }

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=(15,15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1) # 讓 Notebook 區域可以擴展
        
        # 標題
        title_label = ttk.Label(main_frame, text="MCP Docker 服務器安裝與配置 (簡約版)", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.EW)
        
        # Notebook 分頁
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 分頁 1: 服務器選擇與環境變數 (合併)
        self.server_env_frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.server_env_frame, text=' ❶ 選擇服務器與配置環境變數 ')
        self.create_server_env_tab(self.server_env_frame)
        
        # 分頁 2: 配置生成
        self.config_gen_frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.config_gen_frame, text=' ❷ 生成配置與腳本 ')
        self.create_config_generation_tab(self.config_gen_frame)
        
        # 分頁 3: 安裝指南 (簡化)
        self.install_guide_frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.install_guide_frame, text=' ❸ 快速指南 ')
        self.create_installation_guide_tab(self.install_guide_frame)
        
        # 底部按鈕區域
        button_frame = ttk.Frame(main_frame, padding=(0,10,0,0))
        button_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        button_frame.columnconfigure(0, weight=1) # 讓按鈕組居中
        button_frame.columnconfigure(2, weight=1)

        action_buttons_subframe = ttk.Frame(button_frame)
        action_buttons_subframe.grid(row=0, column=1) # 放置在中間欄
        
        ttk.Button(action_buttons_subframe, text="🔍 檢查 Docker", command=self.check_docker).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons_subframe, text="🚀 生成配置", command=self.generate_configs, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons_subframe, text="📥 安裝選定服務器", command=self.install_servers).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons_subframe, text="🧹 清除所有", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons_subframe, text="❓ 說明", command=self.show_help_popup).pack(side=tk.LEFT, padx=5)
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_bar = tk.Label(self.root, textvariable=self.status_var, **self.status_bar_style)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status_bar("MCP Docker 安裝器 - 就緒")
        
    def create_server_env_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1) # 左側 Treeview
        parent_frame.columnconfigure(1, weight=1) # 右側 Env Vars
        parent_frame.rowconfigure(0, weight=1)

        # 左側：服務器選擇
        server_list_lf = ttk.LabelFrame(parent_frame, text="可用的 MCP 服務器", padding=10)
        server_list_lf.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0,10))
        server_list_lf.columnconfigure(0, weight=1)
        server_list_lf.rowconfigure(1, weight=1)

        # 篩選與搜尋
        filter_bar = ttk.Frame(server_list_lf)
        filter_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0,10))
        
        ttk.Label(filter_bar, text="分類:").pack(side=tk.LEFT, padx=(0,5))
        categories = ["全部"] + sorted(list(set(s.get("category", "未分類") for s in self.mcp_servers.values())))
        self.category_var = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(filter_bar, textvariable=self.category_var, values=categories, 
                                      state="readonly", width=15, font=('Arial', 10))
        category_combo.pack(side=tk.LEFT, padx=(0,10))
        category_combo.bind("<<ComboboxSelected>>", self.filter_servers)
        
        ttk.Label(filter_bar, text="搜尋:").pack(side=tk.LEFT, padx=(0,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=25, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.filter_servers)

        # Treeview
        columns = ('selected', 'name', 'category', 'description', 'image')
        self.server_tree = ttk.Treeview(server_list_lf, columns=columns, show='headings', height=15)
        self.server_tree.heading('selected', text='✓')
        self.server_tree.heading('name', text='名稱 (熱門度)')
        self.server_tree.heading('category', text='分類')
        self.server_tree.heading('description', text='描述與應用')
        self.server_tree.heading('image', text='Docker 映像')
        
        self.server_tree.column('selected', width=30, anchor=tk.CENTER, stretch=False)
        self.server_tree.column('name', width=150)
        self.server_tree.column('category', width=100)
        self.server_tree.column('description', width=350)
        self.server_tree.column('image', width=180)
        self.server_tree.tag_configure('wrap', wraplength=330)

        vsb = ttk.Scrollbar(server_list_lf, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=vsb.set)
        self.server_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.server_tree.bind("<Double-1>", self.toggle_server_selection_event)
        self.server_tree.bind("<Button-1>", self.on_tree_click_event)
        self.populate_server_list()

        # 右側：環境變數配置
        env_lf = ttk.LabelFrame(parent_frame, text="選定服務器的環境變數", padding=10)
        env_lf.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        env_lf.columnconfigure(0, weight=1)
        env_lf.rowconfigure(0, weight=1)

        env_canvas = tk.Canvas(env_lf, borderwidth=0, highlightthickness=0, bg=env_lf.cget('background'))
        env_scrollbar = ttk.Scrollbar(env_lf, orient="vertical", command=env_canvas.yview)
        self.env_scrollable_frame = ttk.Frame(env_canvas)
        self.env_scrollable_frame.bind("<Configure>", lambda e: env_canvas.configure(scrollregion=env_canvas.bbox("all")))
        env_canvas.create_window((0,0), window=self.env_scrollable_frame, anchor="nw")
        env_canvas.configure(yscrollcommand=env_scrollbar.set)
        env_canvas.pack(side="left", fill="both", expand=True)
        env_scrollbar.pack(side="right", fill="y")
        self.update_env_config_display()

    def create_config_generation_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1) # 讓 Text Area 擴展
        
        # 配置類型選擇
        config_type_frame = ttk.LabelFrame(parent_frame, text="選擇配置類型", padding=10)
        config_type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.config_type_var = tk.StringVar(value="claude") # 預設 claude
        config_types = [
            ("Claude Desktop", "claude"), 
            ("VS Code", "vscode"), 
            ("Docker Compose", "compose"), 
            ("Shell 腳本", "shell")
        ]
        for i, (text, val) in enumerate(config_types):
            ttk.Radiobutton(config_type_frame, text=text, variable=self.config_type_var, value=val, 
                            command=self.generate_configs).pack(side=tk.LEFT, padx=10)

        # 按鈕 (生成按鈕已整合到 Radiobutton command, 或由主按鈕觸發)
        # ttk.Button(config_type_frame, text="生成所選類型配置", command=self.generate_configs, style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        
        # 配置顯示區域
        action_frame = ttk.Frame(parent_frame)
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10,0))
        ttk.Button(action_frame, text="💾 儲存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(action_frame, text="📋 複製到剪貼簿", command=self.copy_to_clipboard).pack(side=tk.LEFT)

        self.config_text_area = scrolledtext.ScrolledText(parent_frame, height=20, width=80, relief=tk.SOLID, borderwidth=1, wrap=tk.WORD, font=('Monospaced', 9))
        self.config_text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,10))
        self.config_text_area.insert(tk.INSERT, "請選擇服務器並點擊上方配置類型以生成內容，或點擊主界面的「生成配置」按鈕。")
        self.config_text_area.config(state=tk.DISABLED)
        
    def create_installation_guide_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        guide_text_widget = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, padx=10, pady=10, font=('Arial', 10))
        guide_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        guide_content = """
        MCP Docker 安裝器 - 快速指南

        1.  **準備工作**：
            *   確保已安裝 Docker Desktop 且正在運行。
            *   準備好所選服務器可能需要的 API 金鑰或環境變數值。

        2.  **使用本工具**：
            a)  在「選擇服務器與配置環境變數」分頁：
                *   從左側列表中選擇您需要的 MCP 服務器 (可複選)。
                *   在右側為選中的服務器填寫必要的環境變數。
            b)  在「生成配置與腳本」分頁：
                *   選擇您想要的配置類型 (Claude, VS Code, Docker Compose, Shell)。
                *   配置內容會自動顯示在文本框中。
                *   您可以「儲存配置」到檔案或「複製到剪貼簿」。
            c)  點擊主界面下方的「📥 安裝選定服務器」按鈕，工具將使用 `docker pull` 命令拉取選定服務器的最新映像。

        3.  **配置檔案參考位置**：
            *   **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
            *   **VS Code**: 在您的專案根目錄下建立 `.vscode/mcp.json`
            *   **Docker Compose**: 將 `docker-compose.yml` 儲存到專案目錄，然後執行 `docker-compose up -d`。
            *   **Shell 腳本**: 儲存為 `.sh` 檔案，賦予執行權限 (`chmod +x`) 後執行。

        4.  **常用 Docker 指令**：
            *   查看運行容器: `docker ps`
            *   停止容器: `docker stop <container_name_or_id>`
            *   查看日誌: `docker logs <container_name_or_id>`

        詳細資訊請參考專案的 README.md 檔案。
        """
        guide_text_widget.insert(tk.INSERT, guide_content)
        guide_text_widget.config(state=tk.DISABLED)

    def update_status_bar(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def populate_server_list(self):
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
            
        category_filter = self.category_var.get()
        search_term = self.search_var.get().lower()
        
        for server_id, info in self.mcp_servers.items():
            if category_filter != "全部" and info.get("category") != category_filter:
                continue
            
            name_lower = info.get("name", "").lower()
            desc_lower = info.get("description", "").lower()
            cat_lower = info.get("category", "").lower()
            pop_lower = info.get("popularity", "").lower()
            use_cases_lower = " ".join(info.get("use_cases", [])).lower()

            if search_term and not (
                search_term in server_id.lower() or 
                search_term in name_lower or 
                search_term in desc_lower or 
                search_term in cat_lower or 
                search_term in pop_lower or
                search_term in use_cases_lower
            ):
                continue
                
            selected_char = "✔" if server_id in self.selected_servers else "▫"
            popularity_str = f" ({info.get('popularity', 'N/A')})"
            
            description_display = info.get('description', '')
            use_cases_display = ", ".join(info.get("use_cases", []))
            if use_cases_display:
                description_display += f"\n應用: {use_cases_display}"
            
            item_tags = ('wrap',)
            self.server_tree.insert("", tk.END, iid=server_id, values=(
                selected_char, 
                info.get("name", "N/A") + popularity_str, 
                info.get("category", "N/A"), 
                description_display, 
                info.get("image", "N/A")
            ), tags=item_tags)
        self.update_status_bar(f"顯示 {len(self.server_tree.get_children())} 個服務器")
            
    def filter_servers(self, event=None):
        self.populate_server_list()
        
    def toggle_server_selection_event(self, event):
        item_id = self.server_tree.identify_row(event.y)
        if item_id:
            self.toggle_selection(item_id)

    def on_tree_click_event(self, event):
        region = self.server_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.server_tree.identify_column(event.x)
            if column == "#1": 
                item_id = self.server_tree.identify_row(event.y)
                if item_id:
                    self.toggle_selection(item_id)
    
    def toggle_selection(self, server_id):
        if server_id in self.selected_servers:
            del self.selected_servers[server_id]
        else:
            self.selected_servers[server_id] = self.mcp_servers[server_id]
        self.populate_server_list() 
        self.update_env_config_display()
        self.generate_configs() # Selection change should also trigger re-generation if a type is selected
        self.update_status_bar(f"{len(self.selected_servers)} 個服務器已選擇")

    def update_env_config_display(self):
        for widget in self.env_scrollable_frame.winfo_children():
            widget.destroy()
        self.env_entries.clear()
        
        if not self.selected_servers:
            ttk.Label(self.env_scrollable_frame, text="← 請先在左側選擇服務器", 
                      font=('Arial', 11, 'italic'), padding=(10,20)).pack(anchor=tk.CENTER, pady=20)
            return

        container_frame = ttk.Frame(self.env_scrollable_frame)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for server_id in self.selected_servers:
            server_info = self.mcp_servers.get(server_id)
            if not server_info or not server_info.get("env_vars"):
                continue
            
            server_lf = ttk.LabelFrame(container_frame, text=f"🔧 {server_info.get('name')} ({server_info.get('image')})", padding=10)
            server_lf.pack(fill=tk.X, expand=True, pady=(0,10))
            # server_lf.columnconfigure(1, weight=1)

            for i, env_var in enumerate(server_info.get("env_vars", [])):
                ttk.Label(server_lf, text=f"{env_var}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=3)
                is_sensitive = "token" in env_var.lower() or "key" in env_var.lower() or "secret" in env_var.lower()
                entry = ttk.Entry(server_lf, width=45, show="*" if is_sensitive else None, font=('Arial', 10))
                entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=3)
                server_lf.columnconfigure(1, weight=1) # Make entry expand
                self.env_entries[f"{server_id}.{env_var}"] = entry
        
        if not self.env_entries and self.selected_servers: # Selected servers but none need env vars
             ttk.Label(self.env_scrollable_frame, text="選定的服務器無需額外環境變數", 
                      font=('Arial', 11, 'italic'), padding=(10,20)).pack(anchor=tk.CENTER, pady=20)
            
    def generate_configs(self):
        if not self.selected_servers:
            self.config_text_area.config(state=tk.NORMAL)
            self.config_text_area.delete(1.0, tk.END)
            self.config_text_area.insert(tk.INSERT, "請先選擇至少一個 MCP 服務器，然後選擇配置類型。")
            self.config_text_area.config(state=tk.DISABLED)
            self.update_status_bar("未選擇服務器")
            return
            
        config_type = self.config_type_var.get()
        config_str = ""
        
        if config_type == "claude":
            config_str = self._generate_claude_or_vscode_config(is_vscode=False)
        elif config_type == "vscode":
            config_str = self._generate_claude_or_vscode_config(is_vscode=True)
        elif config_type == "compose":
            config_str = self._generate_compose_config()
        elif config_type == "shell":
            config_str = self._generate_shell_config()
        else:
            config_str = "錯誤：未知的配置類型。"
            
        self.config_text_area.config(state=tk.NORMAL)
        self.config_text_area.delete(1.0, tk.END)
        self.config_text_area.insert(tk.INSERT, config_str)
        self.config_text_area.config(state=tk.DISABLED)
        self.update_status_bar(f"已生成 {config_type} 配置")

    def _generate_claude_or_vscode_config(self, is_vscode=False):
        # Common logic for Claude Desktop and VS Code style configs
        base_config = {"mcpServers": {}}
        if is_vscode:
            base_config["inputs"] = []
        processed_inputs = set() # For VSCode to avoid duplicate input prompts

        for server_id, server_data_ref in self.selected_servers.items():
            server_info = self.mcp_servers.get(server_id)
            if not server_info: continue

            image_name = server_info.get("image", server_id)
            server_config_args = ["run", "-i", "--rm"]
            env_vars_for_mcp_env = {}

            for env_var_name in server_info.get("env_vars", []):
                server_config_args.extend(["-e", env_var_name])
                if is_vscode:
                    input_id = f"mcp.{server_id}.{env_var_name}" 
                    if input_id not in processed_inputs:
                        base_config["inputs"].append({
                    "id": input_id,
                            "type": "promptString",
                            "description": f"Enter {env_var_name} for {server_info.get('name')}",
                            "password": "token" in env_var_name.lower() or "key" in env_var_name.lower() or "secret" in env_var_name.lower()
                        })
                        processed_inputs.add(input_id)
                    env_vars_for_mcp_env[env_var_name] = f"${{input:{input_id}}}"
                else: # Claude Desktop
                    key = f"{server_id}.{env_var_name}"
                    value = self.env_entries.get(key, tk.Entry()).get()
                    if value:
                        env_vars_for_mcp_env[env_var_name] = value
            
            server_config_args.append(image_name)
            # Note: This simplified version doesn't handle SSE or custom ports like the advanced configurator
            # It assumes stdio transport for Claude/VSCode.

            mcp_server_entry = {"command": "docker", "args": server_config_args}
            if env_vars_for_mcp_env:
                 mcp_server_entry["env"] = env_vars_for_mcp_env
            base_config["mcpServers"][server_id] = mcp_server_entry
        
        return json.dumps(base_config, indent=2, ensure_ascii=False)

    def _generate_compose_config(self):
        compose_config = {"version": "3.8", "services": {}}
        for server_id, server_data_ref in self.selected_servers.items():
            server_info = self.mcp_servers.get(server_id)
            if not server_info: continue
            image_name = server_info.get("image", server_id)
            service_name = f"mcp-{server_id}"

            service_def = {
                "image": image_name,
                "stdin_open": True,
                "tty": True,
                "restart": "unless-stopped"
            }
            environment = []
            for env_var_name in server_info.get("env_vars", []):
                key = f"{server_id}.{env_var_name}"
                value = self.env_entries.get(key, tk.Entry()).get()
                if value:
                    environment.append(f"{env_var_name}={value}")
                else:
                    environment.append(env_var_name) # Expect .env file or shell env
            if environment: service_def["environment"] = environment
            
            ports_to_map = []
            for p_str in server_info.get("ports", []):
                ports_to_map.append(f"{p_str}:{p_str}")
            if ports_to_map: service_def["ports"] = list(set(ports_to_map))

            compose_config["services"][service_name] = service_def
        try:
            return yaml.dump(compose_config, sort_keys=False, allow_unicode=True, indent=2)
        except NameError: # PyYAML not installed
             return "# PyYAML not installed. Cannot generate YAML.\n" + json.dumps(compose_config, indent=2)
        except Exception as e:
            return f"# Error generating YAML: {e}\n{json.dumps(compose_config, indent=2)}" 

    def _generate_shell_config(self):
        script = "#!/bin/bash\n"
        script += "# MCP Docker Server Startup Script (Generated by MCP Installer GUI)\n"
        script += f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        script += "echo \"Checking Docker...\"\n"
        script += "if ! docker info > /dev/null 2>&1; then\n"
        script += "    echo \"Error: Docker is not running or accessible. Please start Docker and try again.\"\n"
        script += "    exit 1\n"
        script += "fi\n\n"
        
        # Environment variable setup section (guidance for user)
        script += "# --- Environment Variables (Ensure these are set in your shell or .env file if not hardcoded) ---\n"
        unique_env_vars_to_mention = set()
        for server_id in self.selected_servers:
            server_info = self.mcp_servers.get(server_id)
            if server_info and server_info.get("env_vars"):
                for env_var_name in server_info.get("env_vars"):
                    key = f"{server_id}.{env_var_name}"
                    value = self.env_entries.get(key, tk.Entry()).get()
                    if value: # If value provided in GUI, export it
                        script += f'export {env_var_name}="{value}" # Value from GUI\n'
                    else: # Otherwise, add a placeholder for user to fill
                        if env_var_name not in unique_env_vars_to_mention:
                            script += f'# export {env_var_name}="YOUR_{env_var_name}_HERE"\n'
                            unique_env_vars_to_mention.add(env_var_name)
        script += "# ---------------------------------------------------------------------------------------------\n\n"

        script += "echo \"Starting selected MCP Docker servers...\"\n"
        for server_id in self.selected_servers:
            server_info = self.mcp_servers.get(server_id)
            if not server_info: continue
            image_name = server_info.get("image", server_id)
            container_name = f"mcp-{server_id}-shell"

            script += f"\necho \"\nStarting {server_info.get('name')} ({image_name})...\"\n"
            script += f"docker rm -f {container_name} > /dev/null 2>&1 # Remove if already exists\n"
            
            cmd_parts = ["docker run -d --name", container_name]
            for env_var_name in server_info.get("env_vars", []):
                 cmd_parts.append(f'-e {env_var_name}') # Assumes env var is set in shell
            for p_str in server_info.get("ports", []):
                cmd_parts.append(f'-p {p_str}:{p_str}')
            cmd_parts.append(image_name)
            script += " ".join(cmd_parts) + "\n"
            script += f"if [ $? -eq 0 ]; then echo \"✓ {server_info.get('name')} started successfully as {container_name}\"; else echo \"✗ Failed to start {server_info.get('name')}\"; fi\n"

        script += "\n\necho \"\nAll selected server startup attempts complete.\"\n"
        script += "echo \"Use 'docker ps' to check running containers and 'docker logs <container_name>' for logs.\"\n"
        return script
        
    def save_config(self):
        config_content = self.config_text_area.get(1.0, tk.END).strip()
        if not config_content or config_content.startswith("請先選擇") or config_content.startswith("錯誤"):
            messagebox.showwarning("無內容", "沒有有效的配置內容可以儲存。", parent=self.root)
            return

        config_type = self.config_type_var.get()
        file_ext_map = {"claude": ".json", "vscode": ".json", "compose": ".yml", "shell": ".sh"}
        default_name_map = {
            "claude": "claude_desktop_config.json",
            "vscode": "mcp.json",
            "compose": "docker-compose.yml",
            "shell": "start_mcp_servers.sh"
        }
        file_ext = file_ext_map.get(config_type, ".txt")
        default_filename = default_name_map.get(config_type, "mcp_config.txt")
        
        filetypes = [("JSON", "*.json"), ("YAML", "*.yml"), ("Shell Script", "*.sh"), ("Text", "*.txt"), ("All Files", "*.*")]
        if config_type == "compose":
            current_filetypes = [("YAML", "*.yml"), ("All Files", "*.*")]
        elif config_type == "shell":
            current_filetypes = [("Shell Script", "*.sh"), ("All Files", "*.*")]
        elif config_type in ["claude", "vscode"]:
             current_filetypes = [("JSON", "*.json"), ("All Files", "*.*")]
        else:
            current_filetypes = filetypes

        filepath = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            initialfile=default_filename,
            filetypes=current_filetypes,
            title=f"儲存 {config_type.capitalize()} 配置"
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                self.update_status_bar(f"配置已儲存到 {os.path.basename(filepath)}")
                messagebox.showinfo("成功", f"{config_type.capitalize()} 配置已儲存到:\n{filepath}", parent=self.root)
            except Exception as e:
                messagebox.showerror("儲存失敗", f"無法儲存檔案: {e}", parent=self.root)
                
    def copy_to_clipboard(self):
        config_content = self.config_text_area.get(1.0, tk.END).strip()
        if not config_content or config_content.startswith("請先選擇") or config_content.startswith("錯誤"):
            messagebox.showwarning("無內容", "沒有有效的配置內容可以複製。", parent=self.root)
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(config_content)
            self.update_status_bar("配置已複製到剪貼簿。")
            messagebox.showinfo("成功", "目前生成的配置已複製到剪貼簿！", parent=self.root)
        except Exception as e:
            messagebox.showerror("複製失敗", f"無法複製到剪貼簿: {e}", parent=self.root)
        
    def check_docker(self):
        self.update_status_bar("正在檢查 Docker 狀態...")
        # (和 Configurator 中相同的檢查邏輯)
        try:
            version_result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5, check=False)
            info_result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10, check=False)
            if version_result.returncode == 0 and info_result.returncode == 0:
                messagebox.showinfo("Docker 狀態", f"Docker 正常運行 ({version_result.stdout.strip()})", parent=self.root)
                self.update_status_bar("Docker 正常運行")
            elif version_result.returncode != 0:
                messagebox.showerror("Docker 錯誤", "找不到 Docker。請安裝並確保在 PATH 中。", parent=self.root)
                self.update_status_bar("Docker 未安裝或 PATH 配置錯誤")
            else:
                messagebox.showwarning("Docker 警告", "Docker Engine 未運行。請啟動 Docker Desktop。", parent=self.root)
                self.update_status_bar("Docker Engine 未運行")
        except Exception as e:
            messagebox.showerror("檢查錯誤", f"檢查 Docker 時發生錯誤: {e}", parent=self.root)
            self.update_status_bar("檢查 Docker 錯誤")
            
    def install_servers(self):
        if not self.selected_servers:
            messagebox.showwarning("無選擇", "請先選擇要安裝的 MCP 服務器映像。", parent=self.root)
            return
        server_list_str = "\n".join([f"- {self.mcp_servers[s_id].get('name')} ({self.mcp_servers[s_id].get('image')})" 
                                    for s_id in self.selected_servers])
        if not messagebox.askyesno("確認安裝", f"即將拉取以下 Docker 映像：\n{server_list_str}\n\n是否繼續？", parent=self.root):
            return
            
        self.update_status_bar("開始安裝服務器映像...")
        progress_popup = tk.Toplevel(self.root)
        # (和 Configurator 中類似的進度彈窗邏輯)
        progress_popup.title("安裝進度")
        progress_popup.geometry("500x350")
        progress_popup.transient(self.root)
        progress_popup.grab_set()
        ttk.Label(progress_popup, text="正在拉取映像...", font=('Arial', 12)).pack(pady=10)
        log_area = scrolledtext.ScrolledText(progress_popup, height=15, width=60, wrap=tk.WORD)
        log_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        log_area.insert(tk.END, "開始拉取...\n")
        log_area.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
        installed_count, failed_count = 0,0
        total_servers = len(self.selected_servers)
        for i, server_id in enumerate(self.selected_servers.keys()):
            server_info = self.mcp_servers[server_id]
            image_to_pull = server_info.get("image")
            log_area.config(state=tk.NORMAL)
            log_area.insert(tk.END, f"\n[{i+1}/{total_servers}] 拉取 {server_info.get('name')} ({image_to_pull})...\n")
            log_area.see(tk.END)
            log_area.config(state=tk.DISABLED)
            progress_popup.update()
            try:
                process = subprocess.Popen(["docker", "pull", image_to_pull], 
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
                for line in process.stdout: # Stream output
                    log_area.config(state=tk.NORMAL); log_area.insert(tk.END, line); log_area.see(tk.END); 
                    log_area.config(state=tk.DISABLED); progress_popup.update()
                process.wait()
                if process.returncode == 0:
                    log_area.config(state=tk.NORMAL); log_area.insert(tk.END, f"✓ {server_info.get('name')} 拉取成功！\n"); installed_count += 1
                else:
                    log_area.config(state=tk.NORMAL); log_area.insert(tk.END, f"✗ {server_info.get('name')} 拉取失敗 (碼: {process.returncode})\n"); failed_count += 1
            except Exception as e:
                log_area.config(state=tk.NORMAL); log_area.insert(tk.END, f"✗ 拉取 {server_info.get('name')} 錯誤: {e}\n"); failed_count += 1
            finally:
                log_area.see(tk.END); log_area.config(state=tk.DISABLED); progress_popup.update()
        final_msg = f"安裝完成！成功: {installed_count}, 失敗: {failed_count}"
        log_area.config(state=tk.NORMAL); log_area.insert(tk.END, f"\n{final_msg}\n"); log_area.config(state=tk.DISABLED)
        self.update_status_bar(final_msg)
        ttk.Button(progress_popup, text="關閉", command=progress_popup.destroy).pack(pady=10)
        progress_popup.grab_release()
        
    def clear_all(self):
        if messagebox.askyesno("確認清除", "是否清除所有選擇和配置?", parent=self.root):
            self.selected_servers.clear()
            self.env_entries.clear()
            self.config_text_area.config(state=tk.NORMAL)
            self.config_text_area.delete(1.0, tk.END)
            self.config_text_area.insert(tk.INSERT, "選擇已清除。請重新選擇服務器和配置類型。")
            self.config_text_area.config(state=tk.DISABLED)
            self.populate_server_list()
            self.update_env_config_display()
            self.update_status_bar("所有選擇已清除")
            
    def show_help_popup(self):
        # (類似 Configurator 的 show_help_popup，但可以顯示更簡化的內容或指向 README)
        help_content_from_guide = ""
        try:
            # Reuse the content from the guide tab
            guide_tab_frame = self.install_guide_frame
            scrolled_text_widget = guide_tab_frame.winfo_children()[0] # Assuming ScrolledText is the first child
            help_content_from_guide = scrolled_text_widget.get(1.0, tk.END)
        except:
            help_content_from_guide = "請參考「快速指南」分頁或專案的 README.md 檔案獲得詳細幫助。"

        help_top = tk.Toplevel(self.root)
        help_top.title("MCP 安裝器 - 使用說明")
        help_top.geometry("700x500")
        help_top.transient(self.root)
        help_top.grab_set()
        text_area = scrolledtext.ScrolledText(help_top, wrap=tk.WORD, padx=10, pady=10, font=('Arial', 10))
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.INSERT, help_content_from_guide)
        text_area.config(state=tk.DISABLED)
        ttk.Button(help_top, text="關閉", command=help_top.destroy).pack(pady=10)

def main():
    root = tk.Tk()
    app = MCPInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
