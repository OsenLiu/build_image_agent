import telebot
import subprocess
import os
from ruamel.yaml import YAML

# Fetch configurations from Environment Variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USER_ID = os.getenv('ALLOWED_USER_ID') 

YAML_PATH = '/home/jenkins/Work/mybuild/wave4-platform-builder/platforms/w4duvel/platform.yaml' 
BUILD_CWD = '/home/jenkins/Work/mybuild/wave4-platform-builder'
BUILD_CMD = 'bash platforms/w4duvel/run.sh 2>&1 | tee build.log'
LOG_FILE = os.path.join(BUILD_CWD, 'build.log')

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

bot = telebot.TeleBot(TOKEN)
yaml = YAML()
yaml.preserve_quotes = True

def find_and_update(data, target_name, new_rev):
    """
    Recursively searches for a dictionary with 'name': target_name 
    and updates its 'revision'.
    """
    found = False
    if isinstance(data, dict):
        # Check if this dict is the target
        if data.get('name') == target_name:
            data['revision'] = new_rev
            return True
        # Otherwise, search in values
        for v in data.values():
            if find_and_update(v, target_name, new_rev):
                found = True
    elif isinstance(data, list):
        # Search in list items
        for item in data:
            if find_and_update(item, target_name, new_rev):
                found = True
    return found

def update_revisions_safely(extra_rev, apk_rev):
    if not os.path.exists(YAML_PATH):
        return False, f"File not found: {YAML_PATH}"

    with open(YAML_PATH, 'r') as f:
        data = yaml.load(f)
    
    # Attempt to update both
    found_extra = find_and_update(data, 'mdep-devicesetupwizard-extra-screens', extra_rev)
    found_apk = find_and_update(data, 'mdep-devicesetupwizard-apk', apk_rev)
    
    if found_extra and found_apk:
        with open(YAML_PATH, 'w') as f:
            yaml.dump(data, f)
        return True, "Success: Both modules updated in YAML."
    else:
        error_msg = "Targets not found: "
        if not found_extra: error_msg += "[extra-screens] "
        if not found_apk: error_msg += "[apk] "
        return False, error_msg

def check_build_result():
    if not os.path.exists(LOG_FILE):
        return False, "Error: build.log not found."
    
    with open(LOG_FILE, 'r') as f:
        content = f.read()
        
    if "Fetching signed w4duvel_ota tar file" in content:
        return True, "✅ Build Successful: OTA signed files fetched."
    else:
        return False, "❌ Build Failed: Success signature not found in logs."

@bot.message_handler(commands=['build'])
def handle_build(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        bot.reply_to(message, "🚫 Unauthorized.")
        return

    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Usage: `/build [extra-rev] [apk-rev]`")
            return

        extra_rev, apk_rev = args[1], args[2]

        # 1. Update with recursive search
        success, status_text = update_revisions_safely(extra_rev, apk_rev)
        
        if not success:
            bot.send_message(message.chat.id, f"❌ Aborted: {status_text}")
            return

        # 2. Build process
        bot.send_message(message.chat.id, "🛠 YAML updated. Starting build...")
        
        # Execute shell command
        subprocess.run(BUILD_CMD, shell=True, cwd=BUILD_CWD)

        # 3. Final Report
        result_ok, report = check_build_result()
        bot.send_message(message.chat.id, report)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Agent Error: {str(e)}")

if __name__ == '__main__':
    print("Agent started. Listening for commands...")
    bot.polling()