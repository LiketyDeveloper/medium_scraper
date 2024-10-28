import os
import time
import csv
from datetime import datetime

import threading

from .parser import MediumParser
from .ui import AppWindow


class App(AppWindow):
    
    def __init__(self) -> None:
        super().__init__()
        self.parser = MediumParser(
            app=self,
            log_func=self.log
        )
        self.start()
        
    
    def start_parsing(self) -> None:
        if self.proxy and self.link and self.save_directory:
            threading.Thread(target=self.parse_users).start()
        else:
            self.log("[ERROR] Please enter proxy, link and save directory")
    
    
    def parse_users(self) -> None:
        try:
            start = time.time()
            self.parser.initialize_driver(
                proxies=self.proxy
            )
            file_path = os.path.join(self.save_directory, f"output_{datetime.now().strftime(r'%Y-%m-%d_%H-%M')}.csv")
            
            with open(file_path, 'w', newline='') as output_file:
                fieldnames = ["profile_link", "posts"]
                dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                dict_writer.writeheader()
                
                
                users = self.parser.fetch_users_who_liked_post(self.link)
                for user in users:
                    dict_writer.writerows([user])
                    
            end = time.time()
            self.log(f"[SUCCESS] {len(users)} users collected. Took {(end-start):.2f} seconds, saved to {file_path}")
        
        except Exception as e:
            self.log(f"[ERROR] {e}")
    
    
    def start_liking(self):
        if self.proxy and self.email and self.password and self.read_file:
            threading.Thread(target=self.like_users).start()
        else:
            self.log("[ERROR] Please enter proxy, email, app password and file with users")
            
        
    def like_users(self):
        try:
            start = time.time()
            self.parser.initialize_driver(
                proxies=self.proxy
            )
            self.parser.like_users(self.read_file)
            end = time.time()
            self.log(f"[SUCCESS] All users are liked. Took {(end-start):.2f} seconds")
        
        except Exception as e:
            self.log(f"[ERROR] {e}")
    
    def on_closing(self):
        del self.parser
        super().on_closing()
    