import os
import time
import json
import random
import datetime
from playwright.sync_api import sync_playwright

base_path = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_path, "user_data")
tasks_path = os.path.join(base_path, "tasks.json")

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open("activity_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(message)

def human_type(element, text):
    for char in text:
        element.type(char)
        time.sleep(random.uniform(0.05, 0.15))

def switch_profile(page, profile_name):
    log_event(f"Attempting to switch to: {profile_name}")
    try:
        profile_menu = page.locator('//div[@aria-label="Your profile" or @aria-label="ملف الشخصي" or @aria-label="Account"]')
        profile_menu.click()
        time.sleep(2)
        
        quick_target = page.get_by_text(profile_name, exact=True).first

        if quick_target.is_visible():
            quick_target.click()
        else:
            see_all = page.get_by_text("See all profiles") or page.get_by_text("عرض كل الملفات الشخصية")
            if see_all.is_visible():
                see_all.click()
                time.sleep(2)
                page.get_by_text(profile_name, exact=True).first.click()
            else:
                log_event(f"FAILED: Switcher button for {profile_name} not found.")
                page.keyboard.press("Escape")
                return False

        time.sleep(8)
        log_event(f"Successfully switched to {profile_name}")
        return True
            
    except Exception as e:
        log_event(f"ERROR: Switching failed for {profile_name}: {e}")
        page.keyboard.press("Escape")
        return False

def run_automation():
    with open('tasks.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
        
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
            time.sleep(4)
            
            try:
                current_id = page.locator('//div[@aria-label="Your profile" or @aria-label="Account"]').get_attribute('aria-label')
                if task['profile_name'].lower() in str(current_id).lower():
                    log_event(f"Already on {task['profile_name']}. Skipping switch.")
                else:
                    switch_profile(page, task['profile_name'])
            except:
                switch_profile(page, task['profile_name'])
            
            page.goto(task['post_url'])
            page.wait_for_load_state('domcontentloaded')
            time.sleep(5)
            
            try:
                like_btn = page.get_by_label("Like", exact=False).first or page.get_by_label("أعجبني", exact=False).first
                if like_btn and like_btn.is_visible():
                    like_btn.click()
                    log_event(f"SUCCESS: Liked for {task['profile_name']}")
                
                comment_box = page.get_by_role("textbox", name="Comment as ") or page.get_by_role("textbox", name="تعليق باسم")
                if comment_box and comment_box.is_visible():
                    comment_box.click()
                    human_type(comment_box, task['comment_text'])
                    comment_box.press("Enter")
                    log_event(f"SUCCESS: Commented as {task['profile_name']}")
                else:
                    log_event(f"WARNING: Comment box missing for {task['profile_name']}")

            except Exception as e:
                log_event(f"ERROR: Task interaction failed: {e}")
            
            log_event(f"Waiting {task['delay']}s before next task...")
            time.sleep(task['delay'])
        
        log_event("--- All Tasks Completed ---")
        context.close()
   
if __name__ == "__main__":
    run_automation()