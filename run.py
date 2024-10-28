from src.ui import AppWindow
from src.parser import MediumParser
from datetime import datetime
import csv
import time

from pprint import pprint

def main():
    app = AppWindow()
    app.start()
    
    # parser = MediumParser()
    # link = "https://medium.com/gitconnected/13-python-command-line-things-i-regret-not-knowing-earlier-aa92a5fe314e"
    
    # file_path = f"data/output_{datetime.now().strftime(r'%Y-%m-%d_%H-%M')}.csv"
        
    # with open(file_path, 'w', newline='') as output_file:
    #     fieldnames = ["profile_link", "posts"]
    #     dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    #     dict_writer.writeheader()
    #     start = time.time()
        
    #     users = parser.fetch_users_who_liked_post(link)
    #     for user in users:
    #         dict_writer.writerows([user])
            
    #     end = time.time()
    #     print(f"[SUCCESS] {len(users)} пользователей собрано. Заняло {(end-start):.2f} секунд, сохранено {file_path}")
    
    # parser.like_users("data\\output_2024-10-28_02-11.csv")
    
if __name__ == "__main__":
    main()