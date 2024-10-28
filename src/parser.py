import json
import os
import re
import csv
import time
from pprint import pprint

from typing import Dict, Callable, Optional

import imaplib
import email

from fake_useragent import UserAgent

import requests
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException


class MediumParser:

    def __init__(self, app, log_func: Callable[..., None] = None, show_window: bool = False) -> None:
        """
        Initialize the MediumParser instance.

        Args:
            log_func (Callable[..., None], optional): A function for logging messages. Defaults to print.
            show_window (bool, optional): Whether to display the browser window. Defaults to False.
        """
        
        self.app = app

        self._is_logged = False
        self.log = log_func or print
        
        self._driver = None
        self._proxy_config = None
        
        self.log("[SUCCESS] Parser successfully initialized")
        
    
    def initialize_driver(self, proxies: Dict[str, str] = None):
        if self._proxy_config != proxies:
            self._proxy_config = proxies

            if self._driver is not None:
                self._driver.close()
                self._driver.quit()
            
            self._driver = uc.Chrome(
                use_subprocess=False,
                options=self._get_options(proxies=self._proxy_config)
            )
        
        
        
    @property
    def driver(self) -> uc.Chrome:
        """The selenium webdriver instance used by the parser."""
        return self._driver
    
    
    def _get_options(self, proxies: Dict[str, str] = None) -> uc.ChromeOptions:  
        """
        Configure Chrome options for the webdriver.

        Args:
            proxy (Dict[str, str], optional): A dictionary containing proxy 
            settings with keys 'host', 'port', 'login', and 'password'. If 
            provided, a Chrome extension is created to enable proxy usage.

        Returns:
            uc.ChromeOptions: A configured ChromeOptions object for the webdriver.
        """
        chrome_options = uc.ChromeOptions()
        
        if proxies:
            fields = ["host", "port", "login", "password"]
            
            if not all(key in proxies for key in fields):
                raise ValueError("Proxy must contain all of the following fields: host, port, login, password")
            
            self.log("Loading extension for proxy")
                
            manifest_json = \
"""{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": [
            "background.js"
        ]
    },
    "minimum_chrome_version": "22.0.0"
}
"""
            
            background_js = \
"""var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt("%s") // Ensure port is an integer
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({ value: config, scope: "regular" }, function () {
    console.log("Proxy settings applied.");
});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    { urls: ["<all_urls>"] },
    ['blocking']
);
""" % (proxies["host"], proxies["port"], proxies["login"], proxies["password"])
            
            proxy_folder = os.path.join(os.path.dirname(__file__), "proxy_auth_plugin")
            
            if not os.path.exists(proxy_folder):
                os.makedirs(proxy_folder)
                
            with open(os.path.join(proxy_folder, "manifest.json"), "w") as f:
                f.write(manifest_json)
                
            with open(os.path.join(proxy_folder, "background.js"), "w") as f:
                f.write(background_js)

            chrome_options.add_argument(f"--load-extension={proxy_folder}")

        user_agent = UserAgent()
        chrome_options.add_argument(f'--user-agent={user_agent.chrome}')
        
        return chrome_options


    def _get_headers(self, for_link: str = None, graph_ql_operation: str = None) -> Dict[str, str]:
        """
        Generate headers for HTTP requests.

        Returns:
            Dict[str, str]: A dictionary containing the User-Agent header.
        """
        
        user_agent = UserAgent()
        headers = {
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            "user-agent": user_agent.chrome,
        }
        
        if for_link:
            if not isinstance(for_link, str):
                self.log("[ERROR] parser._get_headers: Link must be a string")
            if not for_link.startswith("http"):
                for_link = "https://" + for_link
            if for_link[-1] == "/":
                for_link = for_link[:-1]
                
            frontend_path = for_link.split("/")[-2:]
            if "medium.com" in frontend_path[0]:
                frontend_path = f"{frontend_path[1]}"
            else:
                frontend_path = "/".join(frontend_path)
                
            headers["medium-frontend-path"] = f"{frontend_path}"
            headers["referer"] = f"https://medium.com/{frontend_path}"
        
        if graph_ql_operation:
            if not isinstance(graph_ql_operation, str):
                self.log("[ERROR] parser._get_headers: Link must be a string")
                
            headers["graphql-operation"] = graph_ql_operation
            headers['origin'] = 'https://medium.com'
            headers["apollographql-client-version"] = "main-20241017-182126-a0128a89d2"
            headers["content-type"] = "application/json"
            headers["medium-frontend-app"] = "lite/main-20241017-182126-a0128a89d2"
            headers["medium-frontend-route"] = "post"
            headers['apollographql-client-name'] = 'lite'
        
        return headers
            
    def _get_proxies(self) -> Dict[str, str]:
        """
        Retrieve the proxy configuration for HTTP requests.

        Returns:
            Dict[str, str]: A dictionary containing the proxy settings formatted for use with requests.
        """
        proxy =  f'http://{self._proxy_config["login"]}:{self._proxy_config["password"]}@{self._proxy_config["host"]}:{self._proxy_config["port"]}'
        proxies = {
            "http": proxy,
            "https": proxy
        }
        
        return proxies
    
    
    def _get_cookies(self, link: str) -> Dict[str, str]:
        """
        Retrieve cookies from the loaded webpage.

        Args:
            link (str): The URL of the webpage to load and retrieve cookies from.

        Returns:
            Dict[str, str]: A dictionary of cookies from the webdriver.
        """
        self._load_page(link)
        
        driver_cookies = {}
            
        for cookie in self.driver.get_cookies():
            driver_cookies[cookie["name"]] = cookie["value"]
            
        return driver_cookies
    

    def fetch_users_who_liked_post(self, link: str) -> list[Dict[str, str]]:
        """
        Fetch users who liked a specific post.

        Args:
            link (str): The URL of the post to fetch the likers for.

        Returns:
            List[Dict[str, Union[str, List[Dict[str, str]]]]]: A list of users who liked the post, each containing their profile link and posts.
        """
        
        if not isinstance(link, str):
            self.log(f"[ERROR] parser.fetch_users_who_liked_post: Link must be a string")
        if not link.startswith("http"):
            link = "https://" + link 
        
        # Getting query
        with open('src\\graphql_queries\\fetch_users.gql') as f:
            query = f.read()
        
        operation_name = "PostVotersDialogQuery"
                
        post_id = link.split("-")[-1]
        all_users = []
        next_page = None

        headers = self._get_headers(for_link=link, graph_ql_operation="PostVotersDialogQuery")
        
        proxies = self._get_proxies()
        
        cookies = {}
        
        variables = {
            "postId": post_id,
            "pagingOptions": {
                "limit": 25  # 25 is the maximum allowed limit
            }
        }
        
        session = requests.Session()
        while True:
                    
            response = session.post(
                f'https://medium.com/_/graphql',
                json={"operationName": operation_name, 'query': query, 'variables': variables},
                headers=headers,
                proxies=proxies,
                cookies=cookies
            )

            if not response.ok:
                self.log(f"[ERROR] parser._fetch_users_who_liked_post Something went wrong, can't get users. Status code: {response.status_code}")
                return all_users

            self.log("[SUCCESS] Parsing...")

            
            #If there is a next page, include it in the request
            if next_page:
                variables["pagingOptions"]["page"] = next_page

            # Parse the response
            data = response.json()
            voters = data['data']['post']['voters']['items']
            
            users = [] 
            for voter in voters:
                user = voter['user']
                result = {}
                if len(user["homepagePostsConnection"]["posts"]) > 0:
                    if user["hasSubdomain"]:
                        result["profile_link"] = (f'https://{user["customDomainState"]["live"]["domain"]}')
                    else:
                        result["profile_link"] = f"https://medium.com/@{user['username']}"

                    result["posts"] = []
                    for post in user["homepagePostsConnection"]["posts"]:
                        post = {
                            "id": post["id"],
                            "url": post["mediumUrl"]
                        }
                        result["posts"].append(post)

                    result["posts"] = json.dumps(result["posts"])
                    users.append(result)
                    
                    
            all_users.extend(users)

            # Check for the next page
            next_page_info = data['data']['post']['voters']['pagingInfo']['next']
            if next_page_info:
                next_page = next_page_info['page']
            else:
                break  # Exit the loop if there are no more pages

        return all_users     
    
    
    def _login(self):
        
        with open('src\\graphql_queries\\send_activation.gql') as f:
            query = f.read()
        
        operation_name = "SendAcctAuthEmail"
        
        headers = self._get_headers(graph_ql_operation=operation_name)
        
        proxies = self._get_proxies()
        
        cookies = self._get_cookies("https://medium.com/m/signin")
        # cookies = {}
        
        variables = {
            'email': self.app.email,
            'operation': 'login',
            'redirect': 'https://medium.com/?source=login-------------------------------------',
            'type': 'DEFAULT_MAGIC_LINK',
            'fullName': None,
            'captchaValue': None,
        }
        
        # pprint(headers)
        # pprint(proxies)
        # pprint(cookies)
        
        self.log("[INFO] Trying to login...")
        response = requests.post(
            'https://medium.com/_/graphql', 
            json={"operationName": operation_name, 'query': query, 'variables': variables},
            headers=headers, 
            proxies=proxies,
            cookies=cookies, 
        )
        
        if response.ok:
            self.log("[INFO] Request is sent successfully, waiting for the confirmation link")
            time.sleep(5)
            link = self.get_confirmation_link()
            self._driver.get(link)
            
            try:
                WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Your sign in link has expired')]"))
                )
                
            except TimeoutException:
                self.log("[SUCCESS] Successfully logged in")
                self._is_logged = True
        else:
            self.log(f"[ERROR] Couldn't log in: {response}")
    
    def like_users(self, from_file: str):
        """
        Like users from a specified file.

        Args:
            from_file (str): The path to the file containing user information to like.
        """
        if not isinstance(from_file, str):
            self.log(f"[ERROR] parser.like_users: from_file must be a string")
        
        if not self._is_logged:
            self._login()
        
        with open("src\\graphql_queries\\clap.gql") as f:
            query = f.read()
            
        operation_name = "ClapMutation"
        
        proxies = self._get_proxies()

        cookies = {}
        
        with open(from_file, 'r') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                user_link = row["profile_link"]
                posts = json.loads(row["posts"])
                
                post = posts[0]

                headers = self._get_headers(for_link=post["url"], graph_ql_operation=operation_name)

                if not cookies:
                    cookies = self._get_cookies(post["url"])
                
                variables = {
                    'targetPostId': post["id"],
                    'userId': cookies["uid"],
                    'numClaps': 1,
                }    
                    
                while True:
                    response = requests.post(
                        'https://medium.com/_/graphql', 
                        json={"operationName": operation_name, 'query': query, 'variables': variables},
                        headers=headers, 
                        proxies=proxies,
                        cookies=cookies, 
                    )
                    
                    if response.ok:
                        self.log(f"[SUCCESS][{i}] liked {user_link}")
                        break
                    else:
                        self.log(f"[ERROR] Couldn't like {user_link}: {response}, trying again...")
                        cookies = self._get_page_cookies(post["url"])
    
    def _load_page(self, link: str, timeout: int = 30) -> None:        
        """
        Load a webpage with the specified timeout.

        Args:
            link (str): The URL of the webpage to load.
            timeout (int, optional): The timeout in seconds. Defaults to 30.
        """
        self.driver.find_element
        if not isinstance(link, str) and isinstance(timeout, int):
            self.log(f"[ERROR] parser._load_page: Link must be a string and timout must be an integer")
        if not link.startswith("http"):
            link = "https://" + link
        
        self.driver.set_page_load_timeout(timeout)
        
        try:
            self.driver.get(link)
        except TimeoutException:
            pass
        except Exception as e:
            self.log(f"[ERROR] parser._load_page {e}")
        finally:
            self.driver.set_page_load_timeout(30)
    
    
    def get_confirmation_link(self, count=10) -> Optional[str]:
        """
        Retrieves the verification link from the latest email from Medium.

        Args:
            count (int): The number of latest emails to check. Defaults to 10.

        Returns:
            str: The verification link if found, otherwise None.
        """
        
        self.log("[INFO] Getting confirmation link...")
        
        # Create server and login
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(self.app.email, self.app.password)

        # Selecting the email
        mail.select('INBOX')
        _, data = mail.search(None, 'FROM "noreply@medium.com"')
        
        # Get the list of email IDs
        email_ids = data[0].split()
        
        if email_ids:
            latest_email_id = email_ids[-1]
            
            _, msg = mail.fetch(latest_email_id, "(RFC822)")
            
            for response in msg:
                if not isinstance(response, tuple):
                    continue
                    
                msg = email.message_from_bytes(response[1])

                # Get the body text
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))

                        # Skip text/plain type
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body = part.get_payload(decode=True)  # decode
                            break
                else:
                    body = msg.get_payload(decode=True)

                # Decode the body to a string
                body_str = body.decode()

                # Use regex to find the verification link
                link_pattern = r'(https?://[^\s]+)'
                links = re.findall(link_pattern, body_str)

                # Print the verification link if found
                if links:
                    return links[0]
                else:
                    self.log("[ERROR] В сообщении не нашлось ссылки.")

        else:
            self.log("[ERROR] Не нашлось письма подтверждения.")

        mail.close()
        mail.logout()
        

    def __del__(self):
        if self.driver:
            self._driver.close()
            self._driver.quit()
            self.log("[SUCCESS] Web-driver successfully closed")
    