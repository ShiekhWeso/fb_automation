import os
import sys
import time
import json
import random
import datetime
import tkinter as tk
from tkinter import messagebox
from playwright.sync_api import sync_playwright

base_path = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_path, "user_data")

profiles_path  = os.path.join(base_path, "profiles.txt")
urls_path      = os.path.join(base_path, "post_urls.txt")
comments_path  = os.path.join(base_path, "comments.txt")

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open("activity.log", "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(message)

def show_error_popup(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message)
    root.destroy()

def load_lines(filepath):
    """Read a text file and return a list of non-empty stripped lines."""
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def ensure_files_exist():
    """Create the 3 input files if they don't exist yet."""
    for path in (profiles_path, urls_path, comments_path):
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()
            log_event(f"Created missing file: {os.path.basename(path)}")

def switch_profile(page, profile_name):
    log_event(f"Attempting to switch to: {profile_name}")
    dont_repeat = False
    while not dont_repeat:
        try:
            profile_menu = page.get_by_role("button", name="Your profile").first
            profile_menu.dispatch_event("click")
            time.sleep(2)
        
            see_all = page.get_by_text("See all profiles")
            if see_all.is_visible():
                see_all.dispatch_event("click") 
                time.sleep(2)

                dont_repeat2 = False
                while not dont_repeat2:
                    try:
                        page.get_by_role("button", name=profile_name).first.dispatch_event("click")
                        dont_repeat2 = True
                    except:
                        see_more = page.get_by_text("See more profiles")
                        if see_more.is_visible():
                            see_all.dispatch_event("click") 

                dont_repeat = True
            else:
                log_event(f"FAILED: Switcher button for {profile_name} not found.")
                page.keyboard.press("Escape")
                raise Exception("Switcher button not found")

            time.sleep(2)
            log_event(f"Successfully switched to {profile_name}")
            return True
                
        except Exception as e:
            log_event(f"ERROR: {e}. Retrying switch for {profile_name}...")
            page.keyboard.press("Escape")
            time.sleep(3)

def run_automation():
    ensure_files_exist()

    profiles  = load_lines(profiles_path)
    post_urls = load_lines(urls_path)
    comments  = load_lines(comments_path)

    if not (len(profiles) == len(post_urls) == len(comments)):
        msg = (
            f"File length mismatch!\n\n"
            f"  profiles.txt  : {len(profiles)} line(s)\n"
            f"  post_urls.txt : {len(post_urls)} line(s)\n"
            f"  comments.txt  : {len(comments)} line(s)\n\n"
            "All three files must have the same number of lines."
        )
        log_event(f"ERROR: {msg}")
        show_error_popup(msg)
        sys.exit(1)

    tasks = [
        {"profile_name": p, "post_url": u, "comment_text": c}
        for p, u, c in zip(profiles, post_urls, comments)
    ]

    log_event("--- Script Started ---")
        
    with sync_playwright() as p:
        user_data_dir = "./user_data"
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--start-maximized"],
            no_viewport=True
        )
        
        page = context.pages[0]
            
        for task in tasks:
            log_event(f"Processing Task: {task['profile_name']}")
            
            page.goto("https://www.facebook.com")
            time.sleep(3)
            
            switch_profile(page, task['profile_name'])
            
            dont_repeat = False
            while not dont_repeat:
                try:
                    page.goto(task['post_url'])
                    page.wait_for_load_state('domcontentloaded')
                    dont_repeat = True
                except Exception as e:
                    log_event(f"ERROR: Failed to load {task['post_url']}: {e}. Retrying...")
                    time.sleep(1)
                    
            time.sleep(5)
            try:
                like_btn = page.get_by_role("button", name = "Like").first
                if like_btn and like_btn.is_visible():
                    like_btn.dispatch_event("click") 
                    log_event(f"SUCCESS: Liked for {task['profile_name']}")
                else:
                    log_event(f"WARNING: Like button box missing for {task['profile_name']}")
                
                if "/reel/" in task['post_url']:
                    comment_btn = page.get_by_role("button", name = "Comment").first
                    if comment_btn and comment_btn.is_visible():
                        comment_btn.dispatch_event("click") 
                        time.sleep(2)
                    else:
                        log_event(f"Error: Comment button missing for {task['profile_name']}")
                
                comment_box = page.get_by_role("textbox", name="Comment").first     
                if comment_box and comment_box.is_visible():
                    comment_box.fill(task['comment_text'])
                    comment_box.press("Enter")
                    log_event(f"SUCCESS: Commented as {task['profile_name']}")
                else:
                    log_event(f"WARNING: Comment box missing for {task['profile_name']}")

            except Exception as e:
                log_event(f"ERROR: Task interaction failed: {e}")
            
            time.sleep(5)
        
        log_event("--- All Tasks Completed ---")
        context.close()
   
if __name__ == "__main__":
    run_automation()
