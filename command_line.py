import requests
from bs4 import BeautifulSoup 
import json
from termcolor import colored

def query_article(name: str, save_path: str, proxy: str):
    
    ARTICLE_CONTENT_NOT_FOUND_ERROR = "Luogu cannot serve content"
    
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
    headers={
        "User-Agent": userAgent,
    }

    proxies = {
        "http": proxy,
        "https": proxy,
    }

    response=requests.get(name,headers=headers,proxies=proxies)

    soup = BeautifulSoup(response.text, "html.parser")
    
    title_tag = soup.head.title # type: ignore
    
    if title_tag and title_tag.string == ARTICLE_CONTENT_NOT_FOUND_ERROR:
        return False, "Luogu cannot serve content; please check your proxy"
    
    script_tag = soup.find("script", id="lentille-context", type="application/json")

    if not script_tag:
        return False, "Something went wrong; please raise an issue on GitHub"

    json_string: str = script_tag.string # type: ignore
    json_data = json.loads(json_string)

    content = json_data["data"]["article"]["content"]

    try:
        with open(save_path,"w", encoding='utf-8') as f:
            f.write(content)
        return True, f"Article {name} saved to {save_path}"
    except Exception:
        return False, f"Error writing to f{save_path}"


name = input("Please input the article url... > ")
save_path = input("Which file do you want to save in ? (e.g. ./1.md) > ")
proxy = ""

if name.find("www.luogu.com.cn") == -1:
    proxy = input("Please input your proxy (e.g. http://127.0.0.1:8001, leave blank if using a global proxy) > ")

result, message = query_article(name, save_path, proxy)

print(colored(message, "green" if result else "red"))