import os
import re
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [776941096] 
FORCE_CHANNEL = "@AmirDarkChannel" 
BANNED_WORDS = ["سبام", "scam", "نصب"]

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_EXTERNAL_URL') + '/' + BOT_TOKEN)
    return "Webhook set!", 200

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.is_bot: continue
        welcome_text = f"أهلاً بك {member.first_name} في المجموعة! 🎉\n⚠️ تنبيه: يجب عليك الانضمام إلى قناتنا أولاً:\n{FORCE_CHANNEL}"
        bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_messages(message):
    # هذا السطر راح يطبع لنا كل رسالة تدخل البوت عشان نتأكد
    print(f"[DEBUG] Received message from {message.from_user.id}: {message.text}")

    if message.from_user.id in ADMIN_IDS: 
        print(f"[*] Admin message - Ignored.")
        return
    
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, message.from_user.id)
        if member.status in ['left', 'kicked']:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"@{message.from_user.username}، عذراً يجب عليك الانضمام للقناة أولاً: {FORCE_CHANNEL}")
            print(f"[+] Deleted message: User not in channel.")
            return
    except Exception as e:
        print(f"[!] Force Join Error: {e}") 
    
    link_regex = r'(https?://|t\.me/|www\.)'
    if re.search(link_regex, message.text, re.IGNORECASE):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚫 @{message.from_user.username}، إرسال الروابط ممنوع!")
            print(f"[+] Deleted message: Link detected.")
        except Exception as e:
            print(f"[!] Delete Link Error: {e}")
        return

    for word in BANNED_WORDS:
        if word.lower() in message.text.lower():
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f"🚫 @{message.from_user.username}، يرجى الالتزام بآداب الحوار!")
                print(f"[+] Deleted message: Banned word detected.")
            except Exception as e:
                print(f"[!] Delete Word Error: {e}")
            return

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
