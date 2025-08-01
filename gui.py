import requests
from bs4 import BeautifulSoup 
import json
import tkinter as tk
from tkinter import filedialog, messagebox

content = ""
success_msg: tk.Label|None = None
saved_msg: tk.Label|None = None

def query_article(name: str, proxy: str):
    
    ARTICLE_CONTENT_NOT_FOUND_ERROR = "Luogu cannot serve content"
    
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
    headers={
        "User-Agent": userAgent,
    }

    proxies = {
        "http": proxy,
        "https": proxy,
    }

    response=requests.get(name,headers=headers,proxies=proxies,timeout=10)

    soup = BeautifulSoup(response.text, "html.parser")
    
    title_tag = soup.head.title # type: ignore
    
    if title_tag and title_tag.string == ARTICLE_CONTENT_NOT_FOUND_ERROR:
        return False, "Luogu cannot serve content; please check your proxy"
    
    script_tag = soup.find("script", id="lentille-context", type="application/json")

    if not script_tag:
        return False, "Something went wrong; please raise an issue on GitHub"

    json_string: str = script_tag.string # type: ignore
    json_data = json.loads(json_string)

    global content

    content = json_data["data"]["article"]["content"]
    return True, content

def create_input(label: str, width: int):
    tk.Label(root, text=label).pack()
    entry = tk.Entry(root, width=width, justify=tk.CENTER)
    entry.pack()
    return entry

def display_download_success(url: str):
    global success_msg
    success_msg = tk.Label(root, text=f"Download {url} Success!")
    success_msg.pack()

def reset_download_success():
    global success_msg
    if success_msg:
        success_msg.pack_forget()
        success_msg = None

def display_saved_success(path: str):
    global saved_msg
    saved_msg = tk.Label(root, text=f"Successfully saved to {path}")
    saved_msg.pack()

def reset_saved_success():
    global saved_msg
    if saved_msg:
        saved_msg.pack_forget()
        saved_msg = None

def on_download():
    url = url_entry.get()
    
    if not url:
        return
    
    try:
        success, content = query_article(url, proxy_entry.get())
    except Exception as e:
        success = False
        content = e.__str__()
        
    if not success:
        messagebox.showerror("Download Error", content)
        content = ""
        save_button.config(state=tk.DISABLED)
        reset_download_success()
        reset_saved_success()
    else:
        save_button.config(state=tk.NORMAL)
        reset_download_success()
        display_download_success(url)
        reset_saved_success()

def on_save():
    save_path = filedialog.asksaveasfilename(
        title="Select file to save",
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
    )
    
    if not save_path:
        return
    
    try:
        with open(save_path,"w", encoding='utf-8') as f:
            f.write(content)
        reset_saved_success()
        display_saved_success(save_path)
    except Exception:
        messagebox.showerror("Save Error", f"Failed to save {save_path}")
        reset_saved_success()

def on_return(event: tk.Event):
    if success_msg and not saved_msg:
        on_save()
    else:
        on_download()

root = tk.Tk()
root.title("Luogu Article Downloader")

url_entry = create_input("Article Url: ",len("https://www.luogu.com.cn/article/8n1gvbbb"))
tk.Label(root, text="Proxy: (leave blank for luogu.com.cn or global proxies)").pack()
proxy_entry = create_input("e.g. http://127.0.0.1:8001",len("http://114.114.114.114"))

tk.Button(root, text="Download", command=on_download).pack()
save_button = tk.Button(root, text="Save", command=on_save)
save_button.config(state=tk.DISABLED)
save_button.pack()

root.bind("<Return>", on_return)

url_entry.focus_set()

root.mainloop()