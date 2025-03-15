"""
PyVSCode IDE - Advanced Python Development Environment

Authors:
    - Michael M Nkomo (R245142R)
    - Takura M. Hove

This module implements a VS Code-like IDE with advanced academic features including:
    - Code analysis and metrics
    - Educational components
    - Real-time syntax analysis
"""


import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import sys
import ast
import time
import json
from pathlib import Path
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
import threading
from datetime import datetime
import re
import platform
import ctypes
from ttkthemes import ThemedTk
import numpy as np
import jedi
import webbrowser

class CodeAnalyzer:
    """Analyzes Python code for metrics and quality."""
    
    def analyze_code(self, code_text):
        """Analyzes code for various metrics."""
        try:
            tree = ast.parse(code_text)
            
            # Basic metrics
            metrics = {
                'loc': len(code_text.splitlines()),
                'functions': len([node for node in ast.walk(tree) 
                                if isinstance(node, ast.FunctionDef)]),
                'classes': len([node for node in ast.walk(tree) 
                              if isinstance(node, ast.ClassDef)]),
                'imports': len([node for node in ast.walk(tree) 
                              if isinstance(node, (ast.Import, ast.ImportFrom))]),
                'comments': self._count_comments(code_text),
                'docstrings': self._count_docstrings(tree),
                'complexity': self._calculate_complexity(tree)
            }
            
            return metrics
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {}
            
    def _count_comments(self, code_text):
        """Counts number of comments in code."""
        return len([line for line in code_text.splitlines() 
                   if line.strip().startswith('#')])
                   
    def _count_docstrings(self, tree):
        """Counts number of docstrings."""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    count += 1
        return count
        
    def _calculate_complexity(self, tree):
        """Calculates cyclomatic complexity."""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                               ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

class VSCodeThemes:
    """VS Code-like themes for CodeTerm IDE."""
    
    @staticmethod
    def get_theme(name):
        themes = {
            'Dark+ (default)': {
                'background': '#1E1E1E',
                'foreground': '#D4D4D4',
                'toolbar_bg': '#252526',
                'toolbar_fg': '#CCCCCC',
                'sidebar_bg': '#252526',
                'sidebar_fg': '#CCCCCC',
                'tab_bg': '#2D2D2D',
                'tab_fg': '#FFFFFF',
                'selection_bg': '#264F78',
                'line_number': '#858585',
                'line_highlight': '#282828',
                'scrollbar': '#424242'
            },
            'Light+ (default)': {
                'background': '#FFFFFF',
                'foreground': '#000000',
                'toolbar_bg': '#F3F3F3',
                'toolbar_fg': '#333333',
                'sidebar_bg': '#F3F3F3',
                'sidebar_fg': '#333333',
                'tab_bg': '#ECECEC',
                'tab_fg': '#333333',
                'selection_bg': '#ADD6FF',
                'line_number': '#237893',
                'line_highlight': '#F5F5F5',
                'scrollbar': '#C5C5C5'
            },
            'Monokai': {
                'background': '#272822',
                'foreground': '#F8F8F2',
                'toolbar_bg': '#1e1f1c',
                'toolbar_fg': '#F8F8F2',
                'sidebar_bg': '#1e1f1c',
                'sidebar_fg': '#F8F8F2',
                'tab_bg': '#34352f',
                'tab_fg': '#F8F8F2',
                'selection_bg': '#49483E',
                'line_number': '#90908A',
                'line_highlight': '#3E3D32',
                'scrollbar': '#414339'
            },
            'GitHub Dark': {
                'background': '#24292E',
                'foreground': '#E1E4E8',
                'toolbar_bg': '#1F2428',
                'toolbar_fg': '#E1E4E8',
                'sidebar_bg': '#1F2428',
                'sidebar_fg': '#E1E4E8',
                'tab_bg': '#2F363D',
                'tab_fg': '#E1E4E8',
                'selection_bg': '#444D56',
                'line_number': '#768390',
                'line_highlight': '#2B3036',
                'scrollbar': '#444D56'
            }
        }
        return themes.get(name, themes['Dark+ (default)'])
        
    def setup_theme(self, app):
        """Sets up the current theme."""
        theme = VSCodeThemes.get_theme(app.config['theme'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk styles
        style.configure('CodeTerm.TFrame', background=theme['background'])
        style.configure('CodeTerm.TLabel', background=theme['background'], foreground=theme['foreground'])
        style.configure('CodeTerm.TButton', background=theme['toolbar_bg'], foreground=theme['toolbar_fg'])
        style.configure('CodeTerm.TEntry', background=theme['background'], foreground=theme['foreground'])
        style.configure('CodeTerm.Treeview', background=theme['sidebar_bg'], foreground=theme['sidebar_fg'],
                       fieldbackground=theme['sidebar_bg'])
        
        # Welcome page styles
        style.configure('Welcome.TFrame', background=theme['background'])
        style.configure('Welcome.TLabel', background=theme['background'], foreground=theme['foreground'])
        style.configure('Welcome.TButton', padding=10)
        style.configure('Welcome.TLabelframe', background=theme['background'], foreground=theme['foreground'])
        style.configure('Welcome.TLabelframe.Label', background=theme['background'], foreground=theme['foreground'])
        
        # Card styles for marketplace
        style.configure('Card.TFrame', background=theme['tab_bg'], relief='solid', borderwidth=1)
        
        # Configure text widget colors
        text_config = {
            'background': theme['background'],
            'foreground': theme['foreground'],
            'selectbackground': theme['selection_bg'],
            'inactiveselectbackground': theme['selection_bg'],
            'insertbackground': theme['foreground'],
            'highlightthickness': 0,
            'borderwidth': 0
        }
        
        # Apply theme to all text widgets
        for editor in app.tab_control.winfo_children():
            if isinstance(editor, ttk.Frame):
                for child in editor.winfo_children():
                    if isinstance(child, tk.Text):
                        for key, value in text_config.items():
                            child.configure(**{key: value})
                            
        # Configure menu colors
        app.root.configure(background=theme['background'])
        
    def change_theme(self, app, theme_name):
        """Change the IDE theme."""
        app.config['theme'] = theme_name
        self.setup_theme(app)
        app.save_config()

class LanguageSupport:
    """Handles multi-language support and syntax highlighting."""
    
    def __init__(self):
        self.supported_languages = {}
        self.file_extensions = {}
        self.load_languages()
        
    def load_languages(self):
        """Load supported languages and their lexers."""
        for lexer in get_all_lexers():
            name = lexer[0]
            extensions = lexer[2]
            if extensions:  # Only add languages with file extensions
                self.supported_languages[name] = {
                    'extensions': extensions,
                    'mime_types': lexer[3]
                }
                for ext in extensions:
                    if ext.startswith('.'):
                        self.file_extensions[ext[1:]] = name
                        
    def get_language_for_file(self, filename):
        """Get language based on file extension."""
        ext = filename.split('.')[-1] if '.' in filename else ''
        return self.file_extensions.get(ext, 'Plain Text')
        
    def get_lexer_for_file(self, filename):
        """Get Pygments lexer for file."""
        try:
            return get_lexer_for_filename(filename)
        except:
            return None

class TerminalEmulator:
    """Integrated terminal emulator."""
    
    def __init__(self, parent, **kwargs):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Terminal output
        self.output = ScrolledText(
            self.frame,
            wrap=tk.WORD,
            background=kwargs.get('background', '#1E1E1E'),
            foreground=kwargs.get('foreground', '#D4D4D4'),
            insertbackground=kwargs.get('cursor', '#FFFFFF'),
            font=('Cascadia Code', 10)
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Input line
        self.input_frame = ttk.Frame(self.frame)
        self.input_frame.pack(fill=tk.X)
        
        self.prompt = ttk.Label(
            self.input_frame,
            text="$ ",
            font=('Cascadia Code', 10),
            foreground=kwargs.get('foreground', '#D4D4D4')
        )
        self.prompt.pack(side=tk.LEFT)
        
        self.input = ttk.Entry(
            self.input_frame,
            font=('Cascadia Code', 10),
            style='Terminal.TEntry'
        )
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind events
        self.input.bind('<Return>', self.execute_command)
        self.input.bind('<Up>', self.history_up)
        self.input.bind('<Down>', self.history_down)
        
        # Terminal state
        self.history = []
        self.history_index = 0
        self.current_directory = os.getcwd()
        self.process = None
        
    def execute_command(self, event=None):
        """Execute terminal command."""
        command = self.input.get().strip()
        if not command:
            return
            
        # Add to history
        self.history.append(command)
        self.history_index = len(self.history)
        
        # Clear input
        self.input.delete(0, tk.END)
        
        # Show command in output
        self.output.insert(tk.END, f"\n$ {command}\n")
        
        try:
            # Create process
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.current_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get output
            stdout, stderr = self.process.communicate()
            
            # Show output
            if stdout:
                self.output.insert(tk.END, stdout)
            if stderr:
                self.output.insert(tk.END, stderr, 'error')
                
            # Scroll to end
            self.output.see(tk.END)
            
        except Exception as e:
            self.output.insert(tk.END, f"Error: {str(e)}\n", 'error')
            
    def history_up(self, event=None):
        """Show previous command from history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self.history[self.history_index])
            
    def history_down(self, event=None):
        """Show next command from history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self.history[self.history_index])

class Authentication:
    """Handles user authentication with GitHub and Google."""
    
    def __init__(self):
        self.github_client_id = "YOUR_GITHUB_CLIENT_ID"
        self.google_client_id = "YOUR_GOOGLE_CLIENT_ID"
        self.user = None
        
    def show_login_dialog(self, parent):
        """Show login dialog with GitHub and Google options."""
        dialog = tk.Toplevel(parent)
        dialog.title("Login to CodeTerm")
        dialog.geometry("400x300")
        dialog.transient(parent)
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Header
        header = ttk.Label(
            dialog,
            text="Welcome to CodeTerm",
            font=('Segoe UI', 16, 'bold')
        )
        header.pack(pady=20)
        
        # Login buttons
        github_btn = ttk.Button(
            dialog,
            text="Continue with GitHub",
            command=lambda: self.github_login(dialog)
        )
        github_btn.pack(pady=10, padx=50, fill=tk.X)
        
        google_btn = ttk.Button(
            dialog,
            text="Continue with Google",
            command=lambda: self.google_login(dialog)
        )
        google_btn.pack(pady=10, padx=50, fill=tk.X)
        
        # Skip button
        skip_btn = ttk.Button(
            dialog,
            text="Continue without login",
            command=dialog.destroy
        )
        skip_btn.pack(pady=10, padx=50, fill=tk.X)
        
    def github_login(self, dialog):
        """Handle GitHub OAuth login."""
        auth_url = f"https://github.com/login/oauth/authorize?client_id={self.github_client_id}&scope=user,repo"
        webbrowser.open(auth_url)
        dialog.destroy()
        
    def google_login(self, dialog):
        """Handle Google OAuth login."""
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self.google_client_id}&response_type=code&scope=email%20profile&redirect_uri=http://localhost:8000/callback"
        webbrowser.open(auth_url)
        dialog.destroy()

class PluginMarketplace:
    """Handles plugin discovery, installation, and management."""
    
    def __init__(self):
        self.plugins = {
            'themes': {
                'material-theme': {
                    'name': 'Material Theme',
                    'description': 'Material Design themes for CodeTerm',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '🎨',
                    'installed': False
                },
                'github-theme': {
                    'name': 'GitHub Theme',
                    'description': 'GitHub-inspired themes (Light & Dark)',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '🌓',
                    'installed': False
                }
            },
            'languages': {
                'python-pack': {
                    'name': 'Python Pack',
                    'description': 'Enhanced Python support with debugging',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '🐍',
                    'installed': True
                },
                'javascript-pack': {
                    'name': 'JavaScript Pack',
                    'description': 'JavaScript/TypeScript support with ESLint',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '📜',
                    'installed': False
                }
            },
            'tools': {
                'git-tools': {
                    'name': 'Git Tools',
                    'description': 'Advanced Git integration',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '🔄',
                    'installed': False
                },
                'docker-tools': {
                    'name': 'Docker Tools',
                    'description': 'Docker container management',
                    'author': 'CodeTerm Team',
                    'version': '1.0.0',
                    'icon': '🐳',
                    'installed': False
                }
            }
        }
        
    def show_marketplace(self, parent):
        """Show the plugin marketplace window."""
        window = tk.Toplevel(parent)
        window.title("CodeTerm Marketplace")
        window.geometry("800x600")
        window.transient(parent)
        
        # Center window
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')
        
        # Search bar
        search_frame = ttk.Frame(window)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=search_var,
            font=('Segoe UI', 10),
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Categories
        notebook = ttk.Notebook(window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create pages for each category
        for category, plugins in self.plugins.items():
            page = ttk.Frame(notebook)
            notebook.add(page, text=category.title())
            
            # Create plugin cards
            for plugin_id, plugin in plugins.items():
                self._create_plugin_card(page, plugin_id, plugin)
                
    def _create_plugin_card(self, parent, plugin_id, plugin):
        """Create a card widget for a plugin."""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill=tk.X, padx=10, pady=5)
        
        # Plugin icon and name
        header = ttk.Frame(card)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            header,
            text=f"{plugin['icon']} {plugin['name']}",
            font=('Segoe UI', 12, 'bold')
        ).pack(side=tk.LEFT)
        
        # Install/Uninstall button
        action_text = "Uninstall" if plugin['installed'] else "Install"
        ttk.Button(
            header,
            text=action_text,
            command=lambda: self._toggle_plugin(plugin_id, plugin)
        ).pack(side=tk.RIGHT)
        
        # Description
        ttk.Label(
            card,
            text=plugin['description'],
            wraplength=600
        ).pack(fill=tk.X, padx=5)
        
        # Metadata
        meta = ttk.Frame(card)
        meta.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            meta,
            text=f"v{plugin['version']}",
            font=('Segoe UI', 8)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            meta,
            text=plugin['author'],
            font=('Segoe UI', 8)
        ).pack(side=tk.RIGHT)
        
    def _toggle_plugin(self, plugin_id, plugin):
        """Toggle plugin installation state."""
        plugin['installed'] = not plugin['installed']
        # In a real implementation, this would handle actual installation/uninstallation

class VSCodeLikeIDE:
    """
    Main IDE class implementing VS Code-like functionality with academic features.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("PyVSCode IDE - Academic Edition")
        
        # Make the window start maximized
        self.root.state('zoomed')
        
        # Enable DPI awareness for Windows
        if platform.system() == "Windows":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            
        # Initialize analyzers
        self.code_analyzer = CodeAnalyzer()
        self.language_support = LanguageSupport()
        self.auth = Authentication()
        self.plugin_marketplace = PluginMarketplace()
        
        # Setup theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuration
        self.config = {
            'font_family': 'Consolas',
            'font_size': 12,
            'theme': 'dark',
            'show_metrics': True,
            'auto_suggestions': True,
            'tab_size': 4,
            'highlight_line': True,
            'show_line_numbers': True,
            'wrap_text': False,
            'auto_indent': True,
            'educational_hints': True
        }
        self.load_config()
        
        # Variables
        self.current_file = None
        self.open_files = {}
        self.current_editor = None
        self.is_running = False
        self.search_results = []
        
        self.setup_ui()
        self.setup_keybindings()
        self.setup_autocomplete()
        
        VSCodeThemes.setup_theme(self)
        
    def setup_ui(self):
        """Sets up the main UI components."""
        # Main container
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar (File Explorer, Search, Extensions)
        self.setup_sidebar()
        
        # Right side (Editor and Terminal)
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned)
        
        # Middle section (Editor and Metrics)
        self.middle_paned = ttk.PanedWindow(self.right_paned, orient=tk.HORIZONTAL)
        self.right_paned.add(self.middle_paned)
        
        # Editor area
        self.setup_editor_area()
        
        # Metrics sidebar
        self.setup_metrics_sidebar()
        
        # Terminal area
        self.setup_terminal_area()
        
        # Status bar
        self.setup_status_bar()
        
    def setup_sidebar(self):
        """Sets up the file explorer sidebar with activity bar."""
        self.sidebar = ttk.Frame(self.main_paned)
        self.main_paned.add(self.sidebar)
        
        # Activity Bar
        self.activity_bar = ttk.Frame(self.sidebar)
        self.activity_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Activity buttons with modern icons
        activities = [
            ("📁", "Explorer", self.show_explorer),
            ("🔍", "Search", self.show_search),
            ("📊", "Analysis", self.toggle_metrics),
            ("⚙️", "Settings", self.show_settings),
            ("🛍️", "Marketplace", self.show_marketplace)
        ]
        
        for icon, tooltip, command in activities:
            btn = ttk.Button(self.activity_bar, text=icon, command=command)
            btn.pack(pady=5)
            self.create_tooltip(btn, tooltip)
        
        # Explorer panel
        self.explorer = ttk.Frame(self.sidebar)
        self.explorer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Explorer header with folder management
        explorer_header = ttk.Frame(self.explorer)
        explorer_header.pack(fill=tk.X)
        ttk.Label(explorer_header, text="EXPLORER", 
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Add folder button
        ttk.Button(explorer_header, text="📂", 
                  command=self.open_folder).pack(side=tk.RIGHT, padx=2)
        
        # File tree with icons
        self.file_tree = ttk.Treeview(self.explorer, selectmode="browse", 
                                     style="Custom.Treeview")
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.heading("#0", text="", anchor=tk.W)
        
        # File tree scrollbar
        tree_scroll = ttk.Scrollbar(self.explorer, orient="vertical", 
                                  command=self.file_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bind file tree events
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
    def open_folder(self):
        """Opens a folder and populates the file tree."""
        folder = filedialog.askdirectory()
        if folder:
            self.current_folder = folder
            self.populate_file_tree()
            
    def populate_file_tree(self):
        """Populates the file tree with the contents of the current folder."""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        if not hasattr(self, 'current_folder'):
            return
            
        # Add root folder
        root = self.file_tree.insert('', 'end', text=os.path.basename(self.current_folder),
                                   values=[self.current_folder], open=True)
                                   
        def add_directory(parent, path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    
                    # Skip __pycache__ and .git folders
                    if item in ['__pycache__', '.git']:
                        continue
                        
                    # Choose icon based on type
                    if os.path.isfile(item_path):
                        icon = "📄 " if not item.endswith('.py') else "🐍 "
                    else:
                        icon = "📁 "
                        
                    node = self.file_tree.insert(parent, 'end', 
                                               text=icon + item,
                                               values=[item_path])
                                               
                    if os.path.isdir(item_path):
                        add_directory(node, item_path)
            except PermissionError:
                pass
                
        add_directory(root, self.current_folder)
        
    def on_file_select(self, event):
        """Handles file selection in the tree."""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            path = self.file_tree.item(item)['values'][0]
            if os.path.isfile(path):
                self.status_left.config(text=f"Selected: {os.path.basename(path)}")
                
    def on_file_double_click(self, event):
        """Handles double click on file in tree."""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            path = self.file_tree.item(item)['values'][0]
            if os.path.isfile(path):
                self.open_file_from_path(path)
                
    def open_file_from_path(self, path):
        """Opens a file from the given path."""
        try:
            with open(path, 'r') as file:
                code = file.read()
                editor = self.create_editor()
                self.tab_control.add(editor, text=os.path.basename(path))
                editor.delete('1.0', tk.END)
                editor.insert('1.0', code)
                self.tab_control.select(editor)
                self.current_file = path
                self.highlight_syntax()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def setup_metrics_sidebar(self):
        """Sets up the metrics and analysis sidebar."""
        self.metrics_frame = ttk.Frame(self.middle_paned)
        self.middle_paned.add(self.metrics_frame)
        
        # Metrics header
        ttk.Label(self.metrics_frame, text="CODE METRICS", 
                 font=('Segoe UI', 10, 'bold')).pack(pady=5)
        
        # Metrics display
        self.metrics_text = ScrolledText(self.metrics_frame, 
                                       width=30, 
                                       height=20, 
                                       font=(self.config['font_family'], 10))
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Visualization area
        self.viz_canvas = tk.Canvas(self.metrics_frame, height=200)
        self.viz_canvas.pack(fill=tk.X, pady=5)
        
        # Suggestions area
        ttk.Label(self.metrics_frame, text="SUGGESTIONS", 
                 font=('Segoe UI', 10, 'bold')).pack(pady=5)
        self.suggestions_text = ScrolledText(self.metrics_frame, 
                                          width=30, 
                                          height=10, 
                                          font=(self.config['font_family'], 10))
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
    def update_metrics(self):
        """Updates the code metrics display."""
        if not self.current_editor:
            return
            
        code = self.current_editor.get("1.0", tk.END)
        metrics = self.code_analyzer.analyze_code(code)
        
        # Update metrics display
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, "Code Metrics:\n\n")
        for key, value in metrics.items():
            self.metrics_text.insert(tk.END, f"{key.title()}: {value}\n")
            
        # Update suggestions
        suggestions = []
        if metrics.get('complexity', 0) > 10:
            suggestions.append("High complexity detected. Consider breaking down functions.")
            
        if metrics.get('loc', 0) > 300:
            suggestions.append("Large file size. Consider splitting into modules.")
            
        self.suggestions_text.delete("1.0", tk.END)
        for suggestion in suggestions:
            self.suggestions_text.insert(tk.END, f"• {suggestion}\n")
            
        # Update visualization
        self.update_metrics_visualization(metrics)
        
    def update_metrics_visualization(self, metrics):
        """Updates the metrics visualization."""
        # Clear previous visualization
        self.viz_canvas.delete("all")
        
        # Create bar chart
        chart_height = 150
        chart_width = 250
        max_value = max(metrics.values())
        
        for i, (key, value) in enumerate(metrics.items()):
            if isinstance(value, (int, float)):
                bar_height = (value / max_value) * chart_height
                self.viz_canvas.create_rectangle(
                    30 + i * 50, chart_height - bar_height,
                    70 + i * 50, chart_height,
                    fill="#569cd6"
                )
                self.viz_canvas.create_text(
                    50 + i * 50, chart_height + 20,
                    text=key[:4],
                    angle=45
                )
                
    def run_code(self):
        """Runs the code."""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first")
            return
            
        self.terminal.delete("1.0", tk.END)
        self.terminal.insert(tk.END, f"Running {os.path.basename(self.current_file)}...\n\n")
        self.status_left.config(text="Running...")
        
        def run():
            try:
                python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
                process = subprocess.Popen([python_cmd, self.current_file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
                                        
                output, error = process.communicate()
                
                self.terminal.insert(tk.END, output)
                if error:
                    self.terminal.insert(tk.END, f"\nErrors:\n{error}", "error")
                    
                self.status_left.config(text="Ready")
            except Exception as e:
                self.terminal.insert(tk.END, f"\nError: {e}", "error")
                
        threading.Thread(target=run).start()
        
    def show_educational_hints(self, event=None):
        """Shows educational hints for the current code context."""
        if not self.current_editor or not self.config['educational_hints']:
            return
            
        cursor_pos = self.current_editor.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line = self.current_editor.get(line_start, cursor_pos.split('.')[0] + '.end')
        
        # Analyze current line and context
        hints = []
        code = self.current_editor.get("1.0", tk.END)
        
        try:
            tree = ast.parse(code)
            
            # Function definition hints
            if line.strip().startswith('def '):
                hints.append("🎓 Function Tips:\n"
                           "- Add a docstring to describe the function\n"
                           "- Consider adding type hints\n"
                           "- Add parameter descriptions")
                           
            # Class definition hints
            elif line.strip().startswith('class '):
                hints.append("🎓 Class Tips:\n"
                           "- Add a class docstring\n"
                           "- Consider inheritance relationships\n"
                           "- Add proper initialization")
                           
            # Loop hints
            elif any(x in line for x in ['for ', 'while ']):
                hints.append("🎓 Loop Tips:\n"
                           "- Consider loop efficiency\n"
                           "- Add a break condition\n"
                           "- Handle edge cases")
                           
            # Exception handling
            elif 'try' in line:
                hints.append("🎓 Exception Tips:\n"
                           "- Catch specific exceptions\n"
                           "- Add proper error messages\n"
                           "- Consider cleanup in finally")
                           
            # Import statements
            elif 'import ' in line:
                hints.append("🎓 Import Tips:\n"
                           "- Group related imports\n"
                           "- Consider using specific imports\n"
                           "- Check for unused imports")
                           
            # Variable assignments
            elif '=' in line and '==' not in line:
                hints.append("🎓 Variable Tips:\n"
                           "- Use descriptive names\n"
                           "- Consider type hints\n"
                           "- Initialize properly")
                           
            # Conditional statements
            elif 'if ' in line:
                hints.append("🎓 Condition Tips:\n"
                           "- Check edge cases\n"
                           "- Consider else cases\n"
                           "- Simplify complex conditions")
                           
            # Function calls
            elif '(' in line and 'def ' not in line:
                hints.append("🎓 Function Call Tips:\n"
                           "- Check parameter types\n"
                           "- Handle return values\n"
                           "- Consider error cases")
                           
            # Code complexity hints
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 20:
                        hints.append("🎓 Complexity Tips:\n"
                                   "- Consider breaking down large functions\n"
                                   "- Extract reusable components\n"
                                   "- Add more documentation")
                                   
            # Best practices
            hints.append("🎓 Best Practices:\n"
                       "- Follow PEP 8 style guide\n"
                       "- Write clear comments\n"
                       "- Use meaningful names")
                       
        except Exception:
            pass
            
        # Show hints
        if hints:
            hint_text = "\n\n".join(hints)
            self.show_tooltip(self.current_editor, hint_text)

    def create_tooltip(self, widget, text):
        """Creates a tooltip for a widget."""
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Create tooltip window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            # Modern styling
            style = ttk.Style()
            style.configure("Tooltip.TLabel", 
                          background="#2d2d2d",
                          foreground="#ffffff",
                          padding=8,
                          font=("Segoe UI", 9))
            
            # Create tooltip content
            label = ttk.Label(self.tooltip, text=text, style="Tooltip.TLabel")
            label.pack()
            
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
        
    def show_tooltip(self, widget, text):
        """Shows a tooltip at the current cursor position."""
        # Get cursor position
        try:
            x, y, _, h = widget.bbox("insert")
            x = x + widget.winfo_rootx()
            y = y + h + widget.winfo_rooty()
            
            # Create tooltip window
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            
            # Position tooltip
            screen_width = self.tooltip.winfo_screenwidth()
            screen_height = self.tooltip.winfo_screenheight()
            
            # Create tooltip content with modern styling
            frame = ttk.Frame(self.tooltip, style="Tooltip.TFrame")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar for long content
            canvas = tk.Canvas(frame, background="#2d2d2d", 
                             highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", 
                                    command=canvas.yview)
            content_frame = ttk.Frame(canvas, style="Tooltip.TFrame")
            
            # Configure scrolling
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Create window for content
            window = canvas.create_window((0, 0), window=content_frame, 
                                       anchor=tk.NW)
            
            # Add content with proper wrapping
            label = ttk.Label(content_frame, text=text, 
                            style="Tooltip.TLabel",
                            wraplength=400)
            label.pack(padx=5, pady=5)
            
            # Update geometry
            content_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Calculate tooltip size and position
            width = min(content_frame.winfo_reqwidth() + 20, 400)
            height = min(content_frame.winfo_reqheight() + 20, 300)
            
            # Adjust position if tooltip would go off screen
            if x + width > screen_width:
                x = screen_width - width
            if y + height > screen_height:
                y = widget.winfo_rooty() - height
                
            self.tooltip.wm_geometry(f"{width}x{height}+{x}+{y}")
            
            # Configure modern styles
            style = ttk.Style()
            style.configure("Tooltip.TFrame",
                          background="#2d2d2d")
            style.configure("Tooltip.TLabel",
                          background="#2d2d2d",
                          foreground="#ffffff",
                          font=("Segoe UI", 9),
                          wraplength=380)
                          
            # Add close button
            close_btn = ttk.Label(frame, text="×", 
                                style="TooltipClose.TLabel",
                                cursor="hand2")
            close_btn.place(relx=1.0, rely=0.0, anchor=tk.NE)
            close_btn.bind('<Button-1>', 
                         lambda e: self.tooltip.destroy())
            
            # Configure close button style
            style.configure("TooltipClose.TLabel",
                          background="#2d2d2d",
                          foreground="#ffffff",
                          font=("Segoe UI", 12, "bold"))
                          
            # Add fade-out effect
            def fade_out():
                if hasattr(self, 'tooltip'):
                    self.tooltip.destroy()
            self.root.after(10000, fade_out)  # Fade out after 10 seconds
            
        except Exception as e:
            print(f"Tooltip error: {e}")
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

    def setup_keybindings(self):
        """Sets up keyboard shortcuts."""
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<Control-m>', lambda e: self.toggle_metrics())
        self.root.bind('<Control-space>', lambda e: self.show_completions())
        self.root.bind('<KeyRelease>', self.show_educational_hints)
        
    def setup_editor_area(self):
        self.editor_frame = ttk.Frame(self.middle_paned)
        self.middle_paned.add(self.editor_frame)
        
        # Tab management
        self.tab_control = ttk.Notebook(self.editor_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Welcome page
        self.show_welcome_page()
        
    def show_welcome_page(self):
        """Show the welcome page with getting started information."""
        if not hasattr(self, 'welcome_tab'):
            self.welcome_tab = ttk.Frame(self.tab_control)
            self.tab_control.add(self.welcome_tab, text="Welcome to CodeTerm")
            
            # Welcome content
            content = ttk.Frame(self.welcome_tab, style='Welcome.TFrame')
            content.pack(fill=tk.BOTH, expand=True)
            
            # Left side - Main content
            left_frame = ttk.Frame(content, style='Welcome.TFrame')
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=50, pady=30)
            
            # Header with logo
            header_frame = ttk.Frame(left_frame, style='Welcome.TFrame')
            header_frame.pack(fill=tk.X)
            
            logo_text = ttk.Label(
                header_frame,
                text="⌨️",  # You can replace this with an actual logo image
                font=('Segoe UI', 48),
                style='Welcome.TLabel'
            )
            logo_text.pack()
            
            title = ttk.Label(
                header_frame,
                text="CodeTerm IDE",
                font=('Segoe UI', 24, 'bold'),
                style='Welcome.TLabel'
            )
            title.pack()
            
            subtitle = ttk.Label(
                header_frame,
                text="Modern Development Environment",
                font=('Segoe UI', 12),
                style='Welcome.TLabel'
            )
            subtitle.pack(pady=(0, 20))
            
            # Quick actions
            actions_frame = ttk.LabelFrame(left_frame, text="Get Started", style='Welcome.TLabelframe')
            actions_frame.pack(fill=tk.X, pady=20)
            
            actions = [
                ("📂 Open Folder", "Ctrl+K Ctrl+O", self.open_folder),
                ("📄 New File", "Ctrl+N", self.new_file),
                ("⚙️ Configure IDE", "Ctrl+,", self.show_settings),
                ("🔌 Browse Extensions", "Ctrl+Shift+X", lambda: self.plugin_marketplace.show_marketplace(self.root))
            ]
            
            for text, shortcut, command in actions:
                action_frame = ttk.Frame(actions_frame, style='Welcome.TFrame')
                action_frame.pack(fill=tk.X, pady=2)
                
                btn = ttk.Button(
                    action_frame,
                    text=text,
                    command=command,
                    style='Welcome.TButton'
                )
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
                
                shortcut_label = ttk.Label(
                    action_frame,
                    text=shortcut,
                    style='Welcome.TLabel'
                )
                shortcut_label.pack(side=tk.RIGHT, padx=5)
            
            # Right side - Recent and Learn
            right_frame = ttk.Frame(content, style='Welcome.TFrame')
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=30)
            
            # Recent files
            if hasattr(self, 'recent_files') and self.recent_files:
                recent_frame = ttk.LabelFrame(right_frame, text="Recent", style='Welcome.TLabelframe')
                recent_frame.pack(fill=tk.X, pady=(0, 20))
                
                for file in self.recent_files[:5]:
                    btn = ttk.Button(
                        recent_frame,
                        text=os.path.basename(file),
                        command=lambda f=file: self.open_file_from_path(f),
                        style='Welcome.TButton'
                    )
                    btn.pack(fill=tk.X, pady=2, padx=5)
            
            # Learn section
            learn_frame = ttk.LabelFrame(right_frame, text="Learn", style='Welcome.TLabelframe')
            learn_frame.pack(fill=tk.X)
            
            learn_items = [
                ("📚 Documentation", "Browse CodeTerm docs"),
                ("🎓 Tutorials", "Learn step by step"),
                ("🔍 Tips & Tricks", "Become a power user"),
                ("🌟 What's New", "See latest features")
            ]
            
            for title, desc in learn_items:
                item_frame = ttk.Frame(learn_frame, style='Welcome.TFrame')
                item_frame.pack(fill=tk.X, pady=5, padx=5)
                
                ttk.Label(
                    item_frame,
                    text=title,
                    font=('Segoe UI', 10, 'bold'),
                    style='Welcome.TLabel'
                ).pack(anchor=tk.W)
                
                ttk.Label(
                    item_frame,
                    text=desc,
                    style='Welcome.TLabel'
                ).pack(anchor=tk.W)
            
            # Pro tips
            tips_frame = ttk.LabelFrame(right_frame, text="Pro Tips", style='Welcome.TLabelframe')
            tips_frame.pack(fill=tk.X, pady=20)
            
            tips = [
                "🎨 Change themes in View > Theme menu",
                "⌨️ Use Ctrl+Shift+P for Command Palette",
                "🔍 Quick search with Ctrl+P",
                "📦 Install extensions from Marketplace"
            ]
            
            for tip in tips:
                ttk.Label(
                    tips_frame,
                    text=tip,
                    font=('Segoe UI', 10),
                    style='Welcome.TLabel'
                ).pack(anchor=tk.W, pady=2, padx=5)
                
    def setup_terminal_area(self):
        self.terminal_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(self.terminal_frame)
        
        # Terminal header
        terminal_header = ttk.Frame(self.terminal_frame)
        terminal_header.pack(fill=tk.X)
        ttk.Label(terminal_header, text="TERMINAL").pack(side=tk.LEFT, padx=5)
        
        # Terminal output
        self.terminal = ScrolledText(self.terminal_frame, 
                                   height=10, 
                                   bg="#1e1e1e", 
                                   fg="#ffffff",
                                   font=(self.config['font_family'], self.config['font_size']))
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
    def setup_status_bar(self):
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Left side
        self.status_left = ttk.Label(self.status_bar, text="Ready")
        self.status_left.pack(side=tk.LEFT, padx=5)
        
        # Right side
        self.status_right = ttk.Label(self.status_bar, text="Python 3")
        self.status_right.pack(side=tk.RIGHT, padx=5)
        
        # File info
        self.file_info = ttk.Label(self.status_bar, text="")
        self.file_info.pack(side=tk.RIGHT, padx=5)
        
    def create_editor(self):
        editor = ScrolledText(self.tab_control,
                            wrap=tk.NONE,
                            undo=True,
                            font=(self.config['font_family'], self.config['font_size']))
        
        # Line numbers
        editor.line_numbers = ScrolledText(self.tab_control,
                                         width=4,
                                         wrap=tk.NONE,
                                         font=(self.config['font_family'], self.config['font_size']))
        editor.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Syntax highlighting
        editor.bind('<KeyRelease>', self.highlight_syntax)
        editor.bind('<Tab>', self.handle_tab)
        editor.bind('<Control-space>', self.show_completions)
        
        return editor
        
    def create_welcome_page(self):
        welcome = ttk.Frame(self.tab_control)
        self.tab_control.add(welcome, text="Welcome")
        
        welcome_text = """Welcome to PyVSCode IDE
        
Get Started:
• Create a new file (Ctrl+N)
• Open a file (Ctrl+O)
• Open folder
        
Recent Files:
"""
        label = ttk.Label(welcome, text=welcome_text, justify=tk.LEFT)
        label.pack(padx=20, pady=20)
        
    def show_explorer(self):
        """Shows the explorer panel."""
        self.explorer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def show_search(self):
        """Shows the search panel."""
        if hasattr(self, 'search_frame'):
            self.search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            self.setup_search_panel()
            
    def setup_search_panel(self):
        """Sets up the search panel."""
        self.search_frame = ttk.Frame(self.sidebar)
        self.search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search header
        search_header = ttk.Frame(self.search_frame)
        search_header.pack(fill=tk.X)
        ttk.Label(search_header, text="SEARCH", 
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Search entry
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.bind('<Return>', self.perform_search)
        
        # Search results
        self.search_results = ScrolledText(self.search_frame, 
                                         height=20,
                                         font=(self.config['font_family'], 10))
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=5)
        
    def perform_search(self, event=None):
        """Performs a search in the current folder."""
        query = self.search_entry.get()
        if not query or not hasattr(self, 'current_folder'):
            return
            
        self.search_results.delete('1.0', tk.END)
        self.search_results.insert(tk.END, f"Searching for '{query}'...\n\n")
        
        try:
            for root, dirs, files in os.walk(self.current_folder):
                for file in files:
                    if file.endswith('.py'):
                        path = os.path.join(root, file)
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                rel_path = os.path.relpath(path, self.current_folder)
                                self.search_results.insert(tk.END, 
                                                        f"🔍 {rel_path}\n")
        except Exception as e:
            self.search_results.insert(tk.END, f"Error: {e}\n")
            
    def show_settings(self):
        """Shows the settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x500")
        
        # Settings notebook
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Editor settings
        editor_frame = ttk.Frame(notebook)
        notebook.add(editor_frame, text="Editor")
        
        # Font settings
        ttk.Label(editor_frame, text="Font Family:").pack(pady=5)
        font_combo = ttk.Combobox(editor_frame, 
                                values=['Consolas', 'Courier New', 'Monaco'])
        font_combo.set(self.config['font_family'])
        font_combo.pack(pady=5)
        
        ttk.Label(editor_frame, text="Font Size:").pack(pady=5)
        size_spin = ttk.Spinbox(editor_frame, from_=8, to=24)
        size_spin.set(self.config['font_size'])
        size_spin.pack(pady=5)
        
        # Theme settings
        ttk.Label(editor_frame, text="Theme:").pack(pady=5)
        theme_combo = ttk.Combobox(editor_frame, 
                                 values=['dark', 'light'])
        theme_combo.set(self.config['theme'])
        theme_combo.pack(pady=5)
        
        # Analysis settings
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        
        ttk.Checkbutton(analysis_frame, 
                       text="Show metrics panel",
                       variable=tk.BooleanVar(value=self.config['show_metrics'])
                       ).pack(pady=5)
        
        ttk.Checkbutton(analysis_frame,
                       text="Auto suggestions",
                       variable=tk.BooleanVar(value=self.config['auto_suggestions'])
                       ).pack(pady=5)
        
        # Save button
        def save_settings():
            self.config.update({
                'font_family': font_combo.get(),
                'font_size': int(size_spin.get()),
                'theme': theme_combo.get()
            })
            VSCodeThemes.change_theme(self, theme_combo.get())
            self.save_config()
            settings_window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        ttk.Button(settings_window, text="Save", 
                  command=save_settings).pack(pady=10)
                  
    def toggle_metrics(self):
        """Toggles the metrics panel."""
        if self.config['show_metrics']:
            self.metrics_frame.pack_forget()
            self.config['show_metrics'] = False
        else:
            self.metrics_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
            self.config['show_metrics'] = True
            self.update_metrics()

    def load_config(self):
        """Loads IDE configuration from file."""
        config_dir = Path.home() / '.pyvscode'
        config_path = config_dir / 'config.json'
        
        # Default configuration
        self.config = {
            'font_family': 'Consolas',
            'font_size': 12,
            'theme': 'dark',
            'show_metrics': True,
            'auto_suggestions': True,
            'tab_size': 4,
            'highlight_line': True,
            'show_line_numbers': True,
            'wrap_text': False,
            'auto_indent': True,
            'educational_hints': True
        }
        
        try:
            # Create config directory if it doesn't exist
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing config if available
            if config_path.exists():
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            else:
                # Save default config
                self.save_config()
                
        except Exception as e:
            messagebox.showwarning("Config Warning", 
                                 f"Failed to load config: {e}\nUsing defaults.")
                                 
    def save_config(self):
        """Saves IDE configuration to file."""
        config_dir = Path.home() / '.pyvscode'
        config_path = config_dir / 'config.json'
        
        try:
            # Create config directory if it doesn't exist
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def new_file(self):
        editor = self.create_editor()
        self.tab_control.add(editor, text="Untitled")
        self.tab_control.select(editor)
        
    def save_file(self):
        if not self.current_editor:
            return
            
        if not self.current_file:
            file_path = asksaveasfilename(defaultextension=".py",
                                        filetypes=[("Python Files", "*.py"),
                                                 ("All Files", "*.*")])
            if not file_path:
                return
            self.current_file = file_path
            
        try:
            text = self.current_editor.get("1.0", tk.END)
            with open(self.current_file, 'w') as file:
                file.write(text)
            self.status_left.config(text=f"Saved: {os.path.basename(self.current_file)}")
            
            # Update tab title
            self.tab_control.tab(self.current_editor, text=os.path.basename(self.current_file))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            
    def highlight_syntax(self, event=None):
        if not self.current_editor:
            return
            
        content = self.current_editor.get("1.0", tk.END)
        self.current_editor.tag_remove("keyword", "1.0", tk.END)
        
        # Basic syntax highlighting (you can enhance this)
        keywords = ['def', 'class', 'for', 'while', 'if', 'else', 'try', 'except',
                   'import', 'from', 'return', 'True', 'False', 'None']
                   
        for keyword in keywords:
            start = "1.0"
            while True:
                start = self.current_editor.search(r'\m' + keyword + r'\M',
                                              start, tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.current_editor.tag_add("keyword", start, end)
                start = end
                
        self.current_editor.tag_config("keyword", foreground="#569cd6")
        
    def handle_tab(self, event):
        # Insert spaces instead of tab
        event.widget.insert(tk.INSERT, " " * self.config['tab_size'])
        return "break"
        
    def show_completions(self, event=None):
        """Shows code completion suggestions."""
        if not self.current_editor:
            return "break"
            
        # Get current line and cursor position
        index = self.current_editor.index(tk.INSERT)
        line_no = int(index.split('.')[0])
        column = int(index.split('.')[1])
        
        # Get the code and create Jedi Script
        code = self.current_editor.get('1.0', tk.END)
        
        try:
            # Get completions using jedi
            script = jedi.Script(code, path=self.current_file)
            completions = script.complete(line_no, column)
            
            if not completions:
                return "break"
                
            # Create completion window
            if hasattr(self, 'completion_window') and self.completion_window:
                self.completion_window.destroy()
            self.completion_window = tk.Toplevel(self.root)
            
            # Position window near cursor
            x, y, _, h = self.current_editor.bbox(index)
            x = x + self.current_editor.winfo_rootx()
            y = y + h + self.current_editor.winfo_rooty()
            
            self.completion_window.geometry(f"+{x}+{y}")
            self.completion_window.overrideredirect(True)
            
            # Create frame for completions
            frame = ttk.Frame(self.completion_window)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Create listbox for completions
            self.completion_list = tk.Listbox(
                frame,
                font=(self.config['font_family'], 10),
                selectmode=tk.SINGLE,
                height=min(len(completions), 10),
                activestyle='none',
                bg=self.style.lookup('TFrame', 'background'),
                fg=self.style.lookup('TLabel', 'foreground'),
                selectbackground=self.style.lookup('TButton', 'background', ['active']),
                selectforeground=self.style.lookup('TButton', 'foreground', ['active'])
            )
            self.completion_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Configure scrollbar
            self.completion_list.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.completion_list.yview)
            
            # Store completions for later use
            self.current_completions = completions
            
            # Add completions to listbox with icons
            for comp in completions:
                icon = self._get_completion_icon(comp.type)
                self.completion_list.insert(tk.END, f"{icon} {comp.name} - {comp.type}")
                
            # Bind selection and navigation
            self.completion_list.bind('<Return>', lambda e: self.insert_completion())
            self.completion_list.bind('<Double-Button-1>', lambda e: self.insert_completion())
            self.completion_list.bind('<Escape>', lambda e: self.completion_window.destroy())
            self.completion_list.bind('<Up>', self._navigate_completions)
            self.completion_list.bind('<Down>', self._navigate_completions)
            self.completion_list.bind('<Prior>', self._navigate_completions)  # Page Up
            self.completion_list.bind('<Next>', self._navigate_completions)   # Page Down
            
            # Select first item
            if self.completion_list.size() > 0:
                self.completion_list.select_set(0)
                self.completion_list.focus_set()
            
        except Exception as e:
            if hasattr(self, 'completion_window') and self.completion_window:
                self.completion_window.destroy()
                self.completion_window = None
            print(f"Completion error: {e}")
            
        return "break"
        
    def _get_completion_icon(self, completion_type):
        """Returns an appropriate icon for the completion type."""
        icons = {
            'module': '📦',
            'class': '🔷',
            'function': '🔸',
            'instance': '📎',
            'keyword': '🔑',
            'statement': '📄',
            'import': '📥'
        }
        return icons.get(completion_type, '•')
        
    def _navigate_completions(self, event):
        """Handles keyboard navigation in completion list."""
        if not hasattr(self, 'completion_list') or not self.completion_list:
            return
            
        current = self.completion_list.curselection()
        size = self.completion_list.size()
        
        if not current:
            self.completion_list.select_set(0)
            return
            
        current = current[0]
        
        if event.keysym == 'Up':
            new = max(0, current - 1)
        elif event.keysym == 'Down':
            new = min(size - 1, current + 1)
        elif event.keysym == 'Prior':  # Page Up
            new = max(0, current - 5)
        elif event.keysym == 'Next':   # Page Down
            new = min(size - 1, current + 5)
        else:
            return
            
        self.completion_list.select_clear(0, tk.END)
        self.completion_list.select_set(new)
        self.completion_list.see(new)
        
    def insert_completion(self):
        """Inserts the selected completion."""
        if not hasattr(self, 'completion_list') or not self.completion_list:
            return
            
        selection = self.completion_list.curselection()
        if not selection:
            return
            
        # Get the selected completion
        completion = self.current_completions[selection[0]]
        
        # Get current word boundaries
        cursor_pos = self.current_editor.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line = self.current_editor.get(line_start, cursor_pos)
        
        # Find the start of the current word
        word_start = len(line)
        for i in range(len(line) - 1, -1, -1):
            if not line[i].isalnum() and line[i] not in '_':
                break
            word_start = i
            
        # Calculate positions
        start_pos = f"{cursor_pos.split('.')[0]}.{word_start}"
        
        # Insert the completion
        self.current_editor.delete(start_pos, cursor_pos)
        self.current_editor.insert(start_pos, completion.complete)
        
        # Close completion window
        if hasattr(self, 'completion_window') and self.completion_window:
            self.completion_window.destroy()
            self.completion_window = None
        self.current_editor.focus_set()
        
    def setup_autocomplete(self):
        """Sets up code autocompletion using Jedi."""
        self.jedi_script = None
        self.completion_window = None
        self.completion_list = None
        
    def bind_autocomplete(self, editor):
        """Binds autocomplete to an editor widget."""
        editor.bind('<Control-space>', self.show_completions)

    def on_tab_changed(self, event):
        selection = self.tab_control.select()
        if selection:
            self.current_editor = self.tab_control.children[selection.split('.')[-1]]
            
    def show_marketplace(self):
        """Shows the plugin marketplace."""
        self.plugin_marketplace.show_marketplace(self.root)

def main():
    root = ThemedTk(theme="clam")
    app = VSCodeLikeIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()
