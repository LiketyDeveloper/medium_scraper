"""
The file, that contains User Interface code on tkinter
"""
import os
from datetime import datetime
import json

from typing import Dict


import tkinter as tk
from tkinter import filedialog
from abc import ABC, abstractmethod

class AppWindow(ABC):

    def __init__(self) -> None:
        """
        Initialize the main application window and its components.
        """
        self.root = tk.Tk()
        self.root.title("User Parser")
        self.root.geometry("800x350")
        self.root.resizable(width=False, height=False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.iconbitmap('static\icon.ico')
        
        self.left_frame = tk.Frame(self.root, padx=10, pady=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        self.right_frame = tk.Frame(self.root, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._proxy = self._create_labeled_entry("Прокси:", "Введите прокси: логин:пароль@хост:порт", entry_name="proxy") 
        self._email = self._create_labeled_entry("Почта:", "Введите почту:", entry_name="email")   
        self._password = self._create_labeled_entry("Пароль:", "Введите пароль:", show='*', entry_name="password")
        self._link = self._create_labeled_entry("Ссылка:", "Введите ссылку:")
        
        self._load_config()
        
        self._add_horizontal_line()
        
        self._save_directory = self._add_path_choose(label="Выберите рабочую директорию", command=self._select_save_directory)
        self._add_button(text="Спарсить пользователей", command=self.start_parsing)
        
        self._add_horizontal_line()
        
        self._read_file = self._add_path_choose(label="Выберите файл с пользователями:", command=self._select_read_file)
        self._add_button(text="Проставить лайки", command=self.start_liking)
                
        self._add_log_window()
    
    
    @abstractmethod
    def start_parsing(self): pass
    
    
    @abstractmethod
    def start_liking(self): pass
    
    
    def _load_config(self) -> None:
        """
        Load the saved configuration from a file and set the fields in the
        window with the loaded values.
        """
        config_path = "src\\cache\\config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
                if config["proxy"]:
                    self._proxy.delete(0, tk.END) 
                    self._proxy.config(fg='black')
                    self._proxy.insert(0, config["proxy"])
                if config["email"]:
                    self._email.delete(0, tk.END) 
                    self._email.config(fg='black')
                    self._email.insert(0, config["email"])
                if config["password"]:
                    self._password.delete(0, tk.END) 
                    self._password.config(fg='black')
                    self._password.insert(0, config["password"])
    
        
    @property
    def proxy(self) -> Dict[str, str]:
        """
        Get the proxy settings formatted as a dictionary.

        Returns:
            dict: A dictionary containing the proxy login, password, host, and port.
        """
        if self._proxy.cget('fg') == 'grey':
            return {
                "login": "",
                "password": "",
                "host": "",
                "port": ""
            }
        
        proxy = self._proxy.get().replace("http://", "").replace("https://", "")
        auth, ip = proxy.split("@")
        login, password = auth.split(":")
        host, port = ip.split(":")
        
        proxy = {
            "login": login,
            "password": password,
            "host": host,
            "port": port
        }
        
        return proxy
    
    
    @property
    def email(self) -> str:
        """
        Get the email entered by the user.

        Returns:
            str: The email address from the entry field.
        """
        if self._email.cget('fg') == 'grey':
            return ""
        return self._email.get()
    
    
    @property
    def password(self) -> str:
        """
        Get the password entered by the user.

        Returns:
            str: The password from the entry field.
        """
        if self._email.cget('fg') == 'grey':
            return ""
        return self._password.get()


    @property
    def link(self) -> str:
        """
        Get the link entered by the user.

        Returns:
            str: The link from the entry field.
        """
        if self._link.cget('fg') == 'grey':
            return ""
        return self._link.get()


    @property
    def save_directory(self) -> str:
        """
        Get the directory where parsed users files will be saved.

        Returns:
            str: The path to the save directory.
        """
        if self._save_directory.cget('fg') == 'grey':
            return ""
        return self._save_directory.get()
  
    
    @property
    def read_file(self) -> str:
        """
        Get the path of the file selected for reading user data.

        Returns:
            str: The path to the read file.
        """
        if self._read_file.cget('fg') == 'grey':
            return ""
        
        return self._read_file.get()


    def _create_labeled_entry(self, label_text: str, placeholder_text: str, show: str = None, entry_name:str = "!entry") -> tk.Entry:
        """
        Create a labeled entry widget with a placeholder.

        Args:
            label_text (str): The text for the label.
            placeholder_text (str): The placeholder text for the entry.
            show (str, optional): The character to show for password entry. Defaults to None.
            entry_name (str, optional): The name for the entry widget. Defaults to "!entry".

        Returns:
            tk.Entry: The created entry widget.
        """

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


    def _set_placeholder(self, entry: tk.Entry, placeholder_text: str) -> None:
        """
        Set the placeholder text for a given entry widget.

        Args:
            entry (tk.Entry): The entry widget to set the placeholder for.
            placeholder_text (str): The text to be used as a placeholder.
        """
        entry.insert(0, placeholder_text)
        entry.config(fg='grey')


    def _on_entry_focus_in(self, event: tk.Event, placeholder_text: str) -> None:
        """
        Handle the focus in event for an entry widget, clearing the placeholder.

        Args:
            event (tk.Event): The focus in event.
            placeholder_text (str): The placeholder text to clear.
        """
        entry = event.widget
        if entry.get() == placeholder_text:
                entry.delete(0, tk.END) 
                entry.config(fg='black')


    def _on_entry_focus_out(self, event: tk.Event, placeholder_text: str) -> None:
        """
        Handle the focus out event for an entry widget, restoring the placeholder if empty.

        Args:
            event (tk.Event): The focus out event.
            placeholder_text (str): The placeholder text to restore.
        """
        entry = event.widget
        text = entry.get()
        if not text:
            self._set_placeholder(event.widget, placeholder_text)


    def _add_path_choose(self, label, command) -> tk.Button:
        """
        Add a button to choose a directory.

        Args:
            label (str): The label for the button.
            command (callable): The function to call when the button is clicked.

        Returns:
            tk.Button: The created button widget.
        """
        frame = tk.Frame(self.left_frame)
        frame.pack(fill=tk.X)

        entry = tk.Entry(frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        select_button = tk.Button(frame, text="Choose", command=lambda:  command(entry))

        select_button.pack(side=tk.RIGHT)
        
        self._set_placeholder(entry, label)

        entry.bind("<FocusIn>", lambda e: self._on_entry_focus_in(e, label))
        entry.bind("<FocusOut>", lambda e: self._on_entry_focus_out(e, label))

        return entry
        
        
    def _add_button(self, text, command) -> None:
        """
        Add a button to the interface.

        Args:
            text (str): The text to display on the button.
            command (callable): The function to call when the button is clicked.
        """
        parse_button = tk.Button(self.left_frame, text=text, command=command)
        parse_button.pack(fill=tk.X, pady=5)
    
    
    def _add_log_window(self) -> None:
        """
        Add a log window to the interface for displaying logs.
        """
        self.log_text = tk.Text(self.right_frame, wrap=tk.WORD, height=20, width=30, state=tk.DISABLED)
        self.log_text.pack(expand=True, fill=tk.BOTH)

        self.log_scroll = tk.Scrollbar(self.right_frame, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scroll.set)


    def _add_horizontal_line(self) -> None:
        """
        Add a horizontal line (divider) to the frame.
        """
        line = tk.Frame(self.left_frame, height=1, bg="#131417")
        line.pack(fill=tk.X, pady=20)


    def _select_save_directory(self, text_entry: tk.Entry) -> None:
        """
        Open a dialog to select a save directory and update the UI accordingly.
        """
        directory = filedialog.askdirectory()
        if directory:
            text_entry.delete(0, tk.END) 
            text_entry.config(fg='black')
            text_entry.insert(0, directory)
        
                
    def _select_read_file(self, text_entry: tk.Entry) -> None:
        """
        Open a dialog to select a file for reading user data and update the UI accordingly.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            text_entry.delete(0, tk.END) 
            text_entry.config(fg='black')
            text_entry.insert(0, file_path)

    def log(self, *args) -> None:
        """
        Log messages to the log window with a timestamp.

        Args:
            *args: The messages to log.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {' '.join(args)}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)
    
    
    def start(self) -> None:
        """
        Start the main event loop of the application.
        """
        self.root.mainloop()
        
    
    def on_closing(self):
        config = {
            "proxy": self._proxy.get(),
            "email": self.email,
            "password": self.password,
        }
        with open("src\\cache\\config.json", "w", encoding="utf-8") as f:
            json.dump(config, f)
            
        self.root.destroy()