**Facebook Multi-Profile Automator 🤖**

A robust, identity-aware automation tool built with Python and Playwright. This tool manages multiple Facebook identities (Profiles and Pages) to automate interactions such as liking and commenting on specific posts while mimicking human behavior.

**🌟 Features**
- Smart Identity Switching: Automatically detects the currently logged-in profile and switches only when necessary.
- Support for Pages & Profiles: Seamlessly navigates Facebook's "New Pages Experience" to switch between main accounts and sub-pages.
- Human-Like Interaction: Uses variable typing speeds and randomized delays to reduce the risk of bot detection.
- Comprehensive Logging: Generates a detailed activity_log.txt to track successes, warnings, and errors in real-time.
- Bilingual Support: Compatible with both Arabic and English Facebook UI layouts.
- Persistent Session: Saves login data in a local directory, so users only need to log in once.

**🛠️ Tech Stack**
- Language: Python 3.12+
- Automation Framework: Playwright (Chromium)
- Data Format: JSON (for task management)

**🚀 Installation & Setup**
1. Clone the repository:
   ```
   git clone https://github.com/ShiekhWeso/fb_automation.git
   cd fb_automation
   ```
2. Install dependencies:
   ```
   pip install playwright
   playwright install chromium
   ```
3. Initial Login:
   Run the script once to log into your main Facebook account manually. This creates the necessary session data in the `./user_data` folder.

**📋 How to Use**
1. Configure Tasks
   Edit the `tasks.json` file to define which accounts should perform which actions:
   ```
   [
    {
      "profile_name": "Account Name",
      "post_url": "https://web.facebook.com/photo/...",
      "comment_text": "Your automated comment here!",
      "delay": 30
    }
   ]
   ```
2. Run the Script
   You can launch the automation via the terminal:
   ```
   python main.py
   ```
   Or, if you are on Windows, simply double-click the provided `run_bot.bat` file.

**📂 Project Structure**
- `main.py`: The core automation logic including the Smart Switcher.
- `tasks.json`: Configuration file for accounts, URLs, and comments.
- `activity_log.txt`: Automatically generated report of all bot actions.
- `run_bot.bat`: Windows batch script for easy execution.
- `user_data/`: Directory where browser cookies and sessions are stored.


**⚠️ Disclaimer**
This tool is for educational purposes only. Automated interaction with Facebook may violate their Terms of Service. Use responsibly and at your own risk.
