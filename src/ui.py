from datetime import datetime

import tkinter as tk
from tkinter import filedialog, messagebox
from abc import ABC, abstractmethod

class AppWindow(ABC):

    def __init__(self):
        """Initialize the main application window."""
        self.root = tk.Tk()
        self.root.title("User Parser")
        self.root.geometry("800x350")
        self.root.resizable(width=False, height=False)
        
        self.left_frame = tk.Frame(self.root, padx=10, pady=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._proxy = self._create_labeled_entry("Прокси:", "Введите прокси:", entry_name="proxy") 
        self._email = self._create_labeled_entry("Почта:", "Введите почту:", entry_name="email")   
        self._password = self._create_labeled_entry("Пароль:", "Введите пароль:", show='*', entry_name="password")
        self._link = self._create_labeled_entry("Ссылка:", "Введите ссылку:")
        
        self._add_horizontal_line()
        
        self._save_directory = None
        self._save_directory_btn = self._add_directory_choose(label="Выберите рабочую директорию", command=self._select_save_directory)
        self._add_button(text="Спарсить пользователей", command=self.log)
        
        self._add_horizontal_line()
        
        self._read_file = None
        self._read_file_btn = self._add_directory_choose(label="Выберите файл с пользователями:", command=self._select_read_file)
        self._add_button(text="Проставить лайки", command=self.log)
                
        self._add_log_window()
        
        
    @property
    def proxy(self) -> str:
        proxy = self._proxy.replace("http://", "").replace("https://", "")
        auth, ip = proxy.split("@")
        login, password = auth.split(":")
        host, port = ip.split(":")
        
        return {
            "login": login,
            "password": password,
            "host": host,
            "port": port
        }
    
    
    @property
    def email(self) -> str:
        return self._email.get()
    
    
    @property
    def password(self) -> str:
        return self._password.get()


    @property
    def link(self) -> str:
        return self._link.get()


    @property
    def save_directory(self) -> str:
        return self._save_directory
  
    
    @property
    def read_file(self) -> str:
        return self._read_file


    def _create_labeled_entry(self, label_text, placeholder_text, show=None, entry_name="!entry"):
        """Create a labeled entry widget with a placeholder."""
        frame = tk.Frame(self.left_frame)
        frame.pack(fill=tk.X, pady=5)

        label = tk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)

        entry = tk.Entry(frame, width=40, show=show, name=entry_name)
        entry.pack(side=tk.RIGHT)
        self._set_placeholder(entry, placeholder_text)

        entry.bind("<FocusIn>", lambda e: self._on_entry_focus_in(e, placeholder_text))
        entry.bind("<FocusOut>", lambda e: self._on_entry_focus_out(e, placeholder_text))
        
        return entry


    def _set_placeholder(self, entry, placeholder_text):
        """Set the placeholder text for a given entry widget."""
        entry.insert(0, placeholder_text)
        entry.config(fg='grey')


    def _on_entry_focus_in(self, event, placeholder_text):
        """Handle the focus in event for an entry widget."""
        entry = event.widget
        if entry.get() == placeholder_text:
                entry.delete(0, tk.END) 
                entry.config(fg='black')


    def _on_entry_focus_out(self, event, placeholder_text):
        """Handle the focus out event for an entry widget."""
        entry = event.widget
        text = entry.get()
        if not text:
            self._set_placeholder(event.widget, placeholder_text)


    def _add_directory_choose(self, label, command):
        select_button = tk.Button(self.left_frame, text=label, command=command)
        select_button.pack(fill=tk.X)
        
        return select_button
        
        
    def _add_button(self, text, command):
        parse_button = tk.Button(self.left_frame, text=text, command=command)
        parse_button.pack(fill=tk.X, pady=5)
    
    
    def _add_log_window(self):
        """Add log window at the right of the main window."""
        self.log_text = tk.Text(self.right_frame, wrap=tk.WORD, height=20, width=30, state=tk.DISABLED)
        self.log_text.pack(expand=True, fill=tk.BOTH)

        self.log_scroll = tk.Scrollbar(self.right_frame, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scroll.set)


    def _add_horizontal_line(self):
        """Add a horizontal line (divider) to the frame."""
        line = tk.Frame(self.left_frame, height=1, bg="#131417")
        line.pack(fill=tk.X, pady=20)


    def _select_save_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self._save_directory = directory
            self._save_directory_btn.config(text=f"Выбрана директория: ...{directory[-25:]}")
        
                
    def _select_read_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self._read_file = file_path
            self._read_file_btn.config(text=f"Выбран файл: ...{file_path[-25:]}")


    def log(self, *args):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {' '.join(args)}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)
        
    
        
    
    def start(self):
        self.root.mainloop()
        