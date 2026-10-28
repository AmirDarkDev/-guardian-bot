import os
import re
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ==========================================
# [ مسحنا رقمك عشان تختبر بنفسك ]
# ==========================================
ADMIN_IDS = [] 
FORCE_CHANNEL = "@AmirDarkChannel" 
BANNED_WORDS = ["سبام", "scam", "نصب"]
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    print(f"[RAW_JSON] {json_string}", flush=True) 
    
    update = telebot.types.Update.de_json(json_string)
    
    if update.message and update.message.text:
        message = update.message
        print(f"[DEBUG] Message caught! Text: {message.text}", flush=True)

        # 1. استثناء المشرفين (الحين فاضي)
        if message.from_user.id in ADMIN_IDS: 
            print("[*] Admin message - Ignored.", flush=True)
        else:
            # 2. فحص الروابط
            link_regex = r'(https?://|t\.me/|www\.)'
            if re.search(link_regex, message.text, re.IGNORECASE):
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, f"🚫 @{message.from_user.username}، إرسال الروابط ممنوع!")
                    print(f"[+] Deleted message: Link detected.", flush=True)
                except Exception as e:
                    print(f"[!] Delete Error: {e}", flush=True)
            
            # 3. فحص الكلمات الممنوعة
            elif any(word.lower() in message.text.lower() for word in BANNED_WORDS):
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, f"🚫 @{message.from_user.username}، يرجى الالتزام بآداب الحوار!")
                    print(f"[+] Deleted message: Banned word.", flush=True)
                except Exception as e:
                    print(f"[!] Delete Error: {e}", flush=True)
            
            # 4. فحص الانضمام الإجباري
            else:
                try:
                    member = bot.get_chat_member(FORCE_CHANNEL, message.from_user.id)
                    if member.status in ['left', 'kicked']:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, f"@{message.from_user.username}، عذراً يجب عليك الانضمام للقناة أولاً: {FORCE_CHANNEL}")
                        print(f"[+] Deleted message: User not in channel.", flush=True)
                except Exception as e:
                    print(f"[!] Force Join Error: {e}", flush=True)

    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_EXTERNAL_URL') + '/' + BOT_TOKEN, allowed_updates=['message', 'channel_post'])
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
