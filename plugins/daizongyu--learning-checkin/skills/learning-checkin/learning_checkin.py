#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Check-in Skill
A skill to help users build daily learning habits through check-ins and reminders.
"""

import os
import sys

# Fix Windows console encoding for UTF-8
if sys.platform == "win32":
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import json
import datetime
import threading
import time
import re
import urllib.request
import urllib.error
import locale


def get_user_language():
    """Detect user's preferred language based on system locale."""
    try:
        # Get system locale
        system_lang = locale.getdefaultlocale()[0] or "en_US"
        # Check if it starts with Chinese
        if system_lang.lower().startswith("zh"):
            return "zh"
        return "en"
    except Exception:
        return "en"

# Configuration
VERSION = "3.0.1"
GITHUB_REPO = "daizongyu/learning-checkin"

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Data will be stored in a 'data' subfolder next to the script
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
RULE_FILE = os.path.join(DATA_DIR, "rule.md")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
VERSION_FILE = os.path.join(DATA_DIR, "version.txt")
REMINDER_LOG_FILE = os.path.join(DATA_DIR, "reminder_log.json")

# Default reminder times (24-hour format)
DEFAULT_REMINDER_TIMES = ["09:00", "17:00", "20:00"]

# Multi-language messages
MESSAGES = {
    "zh": {
        # Welcome message (Chinese)
        "welcome": """🎉 欢迎开启学习之旅！

很高兴你决定培养每日学习的习惯！这是一个很棒的决定 👏

🌟 多么简单：
   每天学习完成后，告诉我"我完成了"就行！

🔥 连续打卡：
   我会帮你记录连续学习的天数
   一天不打卡，连续记录就会重置哦

⏰ 温柔提醒：
   如果你忘记打卡，我会在这三个时间提醒你：
   • 早上 9 点 ☀️
   • 下午 5 点 🌤️
   • 晚上 8 点 🌙

准备好了吗？让我们开始第一次打卡吧！""",

        # Check-in success messages
        "checkin_first": "🎉 太棒了！第一天打卡完成！这是个好开始！",
        "checkin_week": "🌟 一周了！连续7天学习，你太厉害了！",
        "checkin_month": "🏆 一个月！30天连续学习，你是超级学霸！",
        "checkin_100": "👑 100天！你是学习王者！膜拜！",
        "checkin_success": [
            "✅ 打卡成功！连续 {streak} 天了！继续加油！💪",
            "✨ 今日学习已完成！连续 {streak} 天，保持住！",
            "🎯 第 {streak} 天！每一天的坚持都值得尊敬！"
        ],

        # Already checked in today
        "already_checked": [
            "你今天已经打过卡了！太棒了！保持这个势头！🔥",
            "今天的你已经很优秀了！明天继续加油！💪",
            "又一天坚持下来了！为你骄傲！⭐"
        ],

        # Status messages
        "status_done": "✅ 今天的卡已经打过了！",
        "status_not_done": "⏳ 今天的还没打卡哦～",
        "status_streak": " 连续 {streak} 天了！",
        "status_no_streak": " 开始你的连续打卡之旅吧！",

        # Reminder messages
        "reminder_09": [
            "☀️ 早上好！今天的的学习完成了吗？开始一天的学习吧！",
            "🌅 新的一天！记得今天的打卡哦～",
            "📚 早晨提醒：学习是每天的小目标，完成后告诉我吧！"
        ],
        "reminder_17": [
            "🌤️ 下午好！今天的任务完成了吗？",
            "💪 一天过半了！学习进度怎么样？",
            "⏰ 提醒一下：今天的打卡还没有记录哦！"
        ],
        "reminder_20": [
            "🌙 晚上好！别忘了今天的打卡，连续记录很重要！",
            "🔥 最后提醒：今天还没打卡呢，别让连续记录断掉！",
            "⭐ 今天的你学习了吗？告诉我'完成了'，我们一起保持 streak！"
        ]
    },
    "en": {
        # Welcome message (English)
        "welcome": """🎉 Welcome to Your Learning Journey!

I'm so glad you've decided to build a daily learning habit! That's a great decision 👏

🌟 How Simple It Is:
   Just tell me "I'm done" or "I finished my learning" when you're done for the day!

🔥 Streak Tracking:
   I'll help you track your consecutive learning days
   Miss a day, and the streak resets (but that's okay, just start again!)

⏰ Gentle Reminders:
   If you forget to check in, I'll remind you at these times:
   • 9:00 AM ☀️
   • 5:00 PM 🌤️
   • 8:00 PM 🌙

Ready? Let's start your first check-in!""",

        # Check-in success messages
        "checkin_first": "🎉 Awesome! First day check-in complete! Great start!",
        "checkin_week": "🌟 One week! 7 days in a row, you're amazing!",
        "checkin_month": "🏆 One month! 30 days of continuous learning, you're a superstar!",
        "checkin_100": "👑 100 days! You're the learning champion!",
        "checkin_success": [
            "✅ Check-in successful! {streak} days in a row! Keep it up! 💪",
            "✨ Today's learning complete! {streak} days streak, keep it going!",
            "🎯 Day {streak}! Every day of consistency deserves respect!"
        ],

        # Already checked in today
        "already_checked": [
            "You've already checked in today! Great job! Keep up the momentum! 🔥",
            "You're already done for today! See you tomorrow! 💪",
            "Another day completed! So proud of you! ⭐"
        ],

        # Status messages
        "status_done": "✅ You've checked in today!",
        "status_not_done": "⏳ Haven't checked in yet today~",
        "status_streak": " {streak} days in a row!",
        "status_no_streak": " Start your streak journey!",

        # Reminder messages
        "reminder_09": [
            "☀️ Good morning! Have you completed your learning today? Let's start!",
            "🌅 A new day! Remember to check in~",
            "📚 Morning reminder: Learning is a daily goal. Let me know when done!"
        ],
        "reminder_17": [
            "🌤️ Good afternoon! Finished your tasks today?",
            "💪 Half day passed! How's your learning going?",
            "⏰ Reminder: No check-in recorded yet today!"
        ],
        "reminder_20": [
            "🌙 Good evening! Don't forget today's check-in, the streak matters!",
            "🔥 Final reminder: Haven't checked in today. Don't break the streak!",
            "⭐ Did you learn today? Tell me "done" to keep the streak going!"
        ]
    }
}


def get_message(key, lang=None):
    """Get message in user's preferred language."""
    if lang is None:
        lang = get_user_language()
    return MESSAGES.get(lang, MESSAGES.get("en", {})).get(key, MESSAGES["en"].get(key, ""))


def get_reminder_message(time_slot, lang=None):
    """Get reminder message for specific time slot."""
    if lang is None:
        lang = get_user_language()

    # Try to load custom messages from rule.md
    rules = load_rules()
    if rules:
        lines = rules.split("\n")
        in_reminder_section = False
        custom_messages = []
        for line in lines:
            if "message" in line.lower() or "reminder" in line.lower():
                in_reminder_section = True
            elif in_reminder_section and line.strip():
                if line.startswith("-") or line.startswith("*"):
                    custom_messages.append(line.lstrip("-* ").strip())
                elif line.startswith("#"):
                    break
        if custom_messages:
            import random
            return random.choice(custom_messages)

    # Use default messages based on time slot and language
    time_key = f"reminder_{time_slot.split(':')[0]}"
    messages = MESSAGES.get(lang, MESSAGES["en"]).get(time_key, MESSAGES["en"].get(time_key, []))
    import random
    return random.choice(messages) if messages else MESSAGES["en"]["reminder_20"][0]


def ensure_dir():
    """Ensure data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_records():
    """Load check-in records."""
    if not os.path.exists(RECORDS_FILE):
        return {"checkins": []}
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"checkins": []}


def save_records(records):
    """Save check-in records."""
    ensure_dir()
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def load_rules():
    """Load user rules from rule.md."""
    if not os.path.exists(RULE_FILE):
        return None
    try:
        with open(RULE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return None


def load_reminder_log():
    """Load reminder log."""
    if not os.path.exists(REMINDER_LOG_FILE):
        return {}
    try:
        with open(REMINDER_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_reminder_log(log_data):
    """Save reminder log."""
    ensure_dir()
    with open(REMINDER_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)


def get_today():
    """Get today's date string."""
    return datetime.datetime.now().strftime("%Y-%m-%d")


def is_checked_in_today():
    """Check if user has already checked in today."""
    records = load_records()
    today = get_today()
    for checkin in records.get("checkins", []):
        if checkin.get("date") == today:
            return True
    return False


def get_streak():
    """Calculate current check-in streak."""
    records = load_records()
    checkins = records.get("checkins", [])

    if not checkins:
        return 0

    # Sort by date descending
    sorted_checkins = sorted(checkins, key=lambda x: x.get("date", ""), reverse=True)

    streak = 0
    today = datetime.datetime.now()
    expected_date = today.strftime("%Y-%m-%d")

    # Check if checked in today
    if sorted_checkins and sorted_checkins[0].get("date") == expected_date:
        streak = 1
        expected_date = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Count consecutive days
    for checkin in sorted_checkins[1:]:
        checkin_date = checkin.get("date", "")
        if checkin_date == expected_date:
            streak += 1
            expected_date = (datetime.datetime.strptime(expected_date, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            break

    return streak


def do_checkin():
    """Perform check-in."""
    lang = get_user_language()

    if is_checked_in_today():
        streak = get_streak()
        messages = get_message("already_checked", lang)
        import random
        return {
            "success": False,
            "message": random.choice(messages),
            "streak": streak,
            "language": lang
        }

    now = datetime.datetime.now()
    checkin_record = {
        "date": now.strftime("%Y-%m-%d"),
        "timestamp": now.isoformat()
    }

    records = load_records()
    records["checkins"].append(checkin_record)
    save_records(records)

    streak = get_streak()

    # Return different celebration messages based on streak
    if streak == 1:
        message = get_message("checkin_first", lang)
    elif streak == 7:
        message = get_message("checkin_week", lang)
    elif streak == 30:
        message = get_message("checkin_month", lang)
    elif streak == 100:
        message = get_message("checkin_100", lang)
    else:
        messages = get_message("checkin_success", lang)
        message = random.choice(messages).format(streak=streak)

    return {
        "success": True,
        "message": message,
        "streak": streak,
        "date": checkin_record["date"]
    }


def get_status():
    """Get current check-in status."""
    today_checked = is_checked_in_today()
    streak = get_streak()
    records = load_records()
    total_checkins = len(records.get("checkins", []))
    lang = get_user_language()

    # Generate friendly status message in user's language
    if today_checked:
        status_message = get_message("status_done", lang)
    else:
        status_message = get_message("status_not_done", lang)

    if streak > 0:
        status_message += get_message("status_streak", lang).format(streak=streak)
    else:
        status_message += get_message("status_no_streak", lang)

    return {
        "checked_in_today": today_checked,
        "streak": streak,
        "total_checkins": total_checkins,
        "today": get_today(),
        "message": status_message,
        "language": lang
    }


def check_version_async(callback):
    """Check for new version in background."""
    def _check():
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "Learning-Checkin-Skill"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                latest_version = data.get("tag_name", "").strip("v")
                if latest_version and compare_versions(latest_version, VERSION) > 0:
                    callback({
                        "has_update": True,
                        "latest_version": latest_version,
                        "url": data.get("html_url", "")
                    })
                    return
        except Exception:
            pass
        callback({"has_update": False})

    thread = threading.Thread(target=_check)
    thread.daemon = True
    thread.start()


def compare_versions(v1, v2):
    """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
    def parse_version(v):
        return [int(x) for x in re.findall(r'\d+', v)]

    parts1 = parse_version(v1)
    parts2 = parse_version(v2)

    for p1, p2 in zip(parts1, parts2):
        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1

    return 0


def get_welcome_message(lang=None):
    """Get the friendly welcome message for first-time users."""
    if lang is None:
        lang = get_user_language()
    return get_message("welcome", lang)


def init_skill():
    """Initialize the skill - create data directory and default files."""
    ensure_dir()
    lang = get_user_language()

    # Create default rule.md if not exists
    if not os.path.exists(RULE_FILE):
        default_rule = get_welcome_message(lang)
        with open(RULE_FILE, "w", encoding="utf-8") as f:
            f.write(default_rule)

    # Create empty records if not exists
    if not os.path.exists(RECORDS_FILE):
        save_records({"checkins": []})

    # Save current version
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(VERSION)

    return {
        "success": True,
        "message": get_welcome_message(lang),
        "data_dir": DATA_DIR,
        "first_time": True,
        "language": lang
    }


def get_reminder_message_main(time_slot):
    """Get reminder message for specific time slot (CLI entry point)."""
    return get_reminder_message(time_slot, None)


def should_send_reminder(time_slot):
    """Check if reminder should be sent for this time slot today."""
    reminder_log = load_reminder_log()
    today = get_today()
    key = f"{today}_{time_slot}"

    # Already reminded today at this time
    if reminder_log.get(key):
        return False

    # Check if already checked in today
    if is_checked_in_today():
        return False

    return True


def log_reminder_sent(time_slot):
    """Log that reminder was sent."""
    reminder_log = load_reminder_log()
    today = get_today()
    key = f"{today}_{time_slot}"
    reminder_log[key] = {"timestamp": datetime.datetime.now().isoformat()}
    save_reminder_log(reminder_log)


# CLI Interface
def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python learning_checkin.py <command> [args]")
        print("Commands:")
        print("  init              - Initialize the skill (first time setup)")
        print("  checkin           - Record a check-in")
        print("  status            - Get current status")
        print("  streak            - Get current streak")
        print("  version           - Get current version")
        print("  check-version     - Check for updates")
        print("  reminder <time>   - Check if reminder should be sent (e.g., 09:00)")
        print("  message <time>    - Get reminder message for time slot")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "init":
        result = init_skill()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "checkin":
        result = do_checkin()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "status":
        result = get_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "streak":
        print(json.dumps({"streak": get_streak()}, ensure_ascii=False, indent=2))

    elif command == "version":
        print(json.dumps({"version": VERSION}, ensure_ascii=False, indent=2))

    elif command == "check-version":
        def on_result(result):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        check_version_async(on_result)
        # Wait a bit for async result
        time.sleep(6)

    elif command == "reminder":
        if len(sys.argv) < 3:
            print("Usage: python learning_checkin.py reminder <time_slot>")
            sys.exit(1)
        time_slot = sys.argv[2]
        result = {
            "should_send": should_send_reminder(time_slot),
            "checked_in": is_checked_in_today()
        }
        if result["should_send"]:
            log_reminder_sent(time_slot)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "message":
        if len(sys.argv) < 3:
            print("Usage: python learning_checkin.py message <time_slot>")
            sys.exit(1)
        time_slot = sys.argv[2]
        message = get_reminder_message_main(time_slot)
        print(json.dumps({"message": message}, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()