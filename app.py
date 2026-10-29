import os
import re
import random
import time
import threading
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [776941096] 
FORCE_CHANNEL = "@AmirDarkChannel" 
BANNED_WORDS = ["سبام", "scam", "نصب", "bot", "قمار"]

# ==========================================
# [ الردود التلقائية - لأي شخص ]
# ==========================================
AUTO_REPLIES = {
    "مرحبا": "أهلاً وسهلاً بك في درع الظلام 🛡️ كيف أقدر أساعدك؟",
    "هاني": "• Use ↤ [✖️ هاني ✖️]\n• Bio ↤ البعد عن الناس راحة، وأنا أحبيت...",
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته 🌸",
    "صباح الخير": "صباح النور والسرور 🌸",
    "مساء الخير": "مساء الفل والياسمين 🌿",
    "كيفكم": "بخير الحمد لله، أنت كيف حالك؟ 🥰",
    "صلي على النبي": "عليه أفضل الصلاة والسلام ☘️",
    "شكرا": "العفو يا طيب، في خدمتك دائماً 🤍",
    "السعر": "سعر تركيب البوت 15$ فقط (USDT). للتواصل: @AmirDarkDev",
    "hello": "Hello! Welcome to Dark Shield 🛡️",
    "thanks": "You're welcome! 🤍",
}

MENTION_REPLIES = [
    "نعم يا طيب؟ أنا درع الظلام، تحت أمرك 🛡️",
    "أنا هنا لحماية المجموعة، كيف أقدر أساعدك؟",
    "أرسل /help عشان تشوف كل الأوامر اللي أقدر أسويها.",
    "Yes? I'm Dark Shield, here to protect the group 🛡️",
    "How can I help you? Type /help for features."
]

user_warnings = {}
warn_cooldown = {}

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def unmute_user_after_delay(chat_id, user_id):
    time.sleep(600)
    try:
        bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
        bot.send_message(chat_id, "🔊 تم فك الكتم تلقائياً بعد 10 دقائق. يمكنك المشاركة الآن | User has been unmuted.")
    except: pass

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot: continue
            welcome_text = f"🇾🇪 أهلاً وسهلاً بك {member.first_name} في درع الظلام 🛡️\n\n⚠️ للتمكن من المشاركة، يرجى الانضمام إلى قناتنا الرسمية أولاً:\n👉 {FORCE_CHANNEL}\n\n🇬🇧 Welcome {member.first_name} to Dark Shield 🛡️\n⚠️ You must join our channel to chat:\n👉 {FORCE_CHANNEL}"
            try: bot.send_message(update.message.chat.id, welcome_text)
            except: pass
        return "!", 200

    if update.message and update.message.text:
        message = update.message
        text_lower = message.text.lower()
        user_id = message.from_user.id
        chat_id = message.chat.id
        user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        
        # 1. لوحة التحكم
        if message.text == '/start' or message.text == '/help':
            markup = InlineKeyboardMarkup()
            btn_add = InlineKeyboardButton("➕ أضفني لمجموعتك | Add to Group", url="https://t.me/ameraldlembot?startgroup=true")
            btn_contact = InlineKeyboardButton("👨‍💻 المطور | Developer", url="https://t.me/AmirDarkDev")
            markup.add(btn_add, btn_contact)
            help_text = "🛡️ *أهلاً بك في بوت درع الظلام* 🛡️\n\n✨ *المميزات:*\n🚫 حذف الروابط\n🛑 منع الكلمات الممنوعة\n🔒 الانضمام الإجباري\n⚠️ نظام إنذارات (3 إنذارات = كتم 10 دقائق)\n🤖 ردود تلقائية لأي شخص (عربي/إنجليزي)\n💬 رد فوري عند المنشن\n🤫 *ميزة الهمس:* رد على رسالة الشخص واكتب `/whisper رسالتك`\n\n🛠️ *أوامر الإدارة:*\n`/ban` - طرد\n`/mute` - كتم\n`/unmute` - فك كتم\n`/resetwarn` - مسح إنذارات\n\n💵 *السعر:* 15$ | 📩 @AmirDarkDev"
            try: bot.send_message(chat_id, help_text, parse_mode='Markdown', reply_markup=markup)
            except: pass
            return "!", 200

        # 2. أوامر الإدارة
        if user_id in ADMIN_IDS:
            if message.text.startswith('/whisper') or message.text.startswith('/همس'):
                if message.reply_to_message:
                    target_id = message.reply_to_message.from_user.id
                    target_name = message.reply_to_message.from_user.first_name
                    whisper_text = message.text.replace('/whisper', '').replace('/همس', '').strip()
                    if not whisper_text:
                        bot.reply_to(message, "⚠️ يرجى كتابة نص الهمسة بعد الأمر. مثال: `/whisper مرحباً`")
                        return "!", 200
                    try:
                        bot.send_message(target_id, f"🤫 *همسة من الإدارة:*\n\n{whisper_text}", parse_mode='Markdown')
                        try: bot.delete_message(chat_id, message.message_id)
                        except: pass
                    except Exception:
                        bot.reply_to(message, f"❌ لم أتمكن من إرسال الهمسة إلى {target_name}. تأكد أنه ضغط على Start في البوت أولاً.")
                    return "!", 200

            if message.text.startswith('/ban') and message.reply_to_message:
                try: bot.ban_chat_member(chat_id, message.reply_to_message.from_user.id)
                except: pass
                try: bot.reply_to(message, "✅ تم طرد العضو | User banned.")
                except: pass
                return "!", 200
            elif message.text.startswith('/mute') and message.reply_to_message:
                try: bot.restrict_chat_member(chat_id, message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=False))
                except: pass
                try: bot.reply_to(message, "🔇 تم كتم العضو | User muted.")
                except: pass
                return "!", 200
            elif message.text.startswith('/unmute') and message.reply_to_message:
                try: bot.restrict_chat_member(chat_id, message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
                except: pass
                try: bot.reply_to(message, "🔊 تم فك الكتم | User unmuted.")
                except: pass
                return "!", 200
            elif message.text.startswith('/resetwarn') and message.reply_to_message:
                user_warnings[message.reply_to_message.from_user.id] = 0
                warn_cooldown[message.reply_to_message.from_user.id] = 0
                try: bot.reply_to(message, "🔄 تم مسح إنذارات العضو | Warnings reset.")
                except: pass
                return "!", 200

        # 3. الردود التلقائية لأي شخص
        for trigger, response in AUTO_REPLIES.items():
            if trigger.lower() in text_lower:
                try: bot.reply_to(message, response)
                except: pass

        # 4. الرد على المنشن
        if f"@{bot.get_me().username}" in message.text or (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id):
            if user_id not in ADMIN_IDS:
                try: bot.reply_to(message, random.choice(MENTION_REPLIES))
                except: pass
                return "!", 200

        if user_id in ADMIN_IDS: 
            return "!", 200

        # 5. فلترة الرسائل والإنذارات
        violation = False
        warning_msg = ""

        try:
            member = bot.get_chat_member(FORCE_CHANNEL, user_id)
            if member.status in ['left', 'kicked']:
                violation = True
                warning_msg = f"⚠️ {user_mention}، يجب عليك الانضمام للقناة أولاً: {FORCE_CHANNEL}"
        except: pass

        if re.search(r'(https?://|t\.me/|www\.)', message.text, re.IGNORECASE):
            violation = True
            warning_msg = f"🚫 {user_mention}، إرسال الروابط ممنوع!"
        elif any(word.lower() in text_lower for word in BANNED_WORDS):
            violation = True
            warning_msg = f"🚫 {user_mention}، يرجى الالتزام بآداب الحوار!"

        if violation:
            try: bot.delete_message(chat_id, message.message_id)
            except: pass

            current_time = time.time()
            if user_id in warn_cooldown and current_time - warn_cooldown[user_id] < 60:
                return "!", 200
            
            warn_cooldown[user_id] = current_time
            user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
            
            if user_warnings[user_id] >= 3:
                try:
                    bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False))
                    bot.send_message(chat_id, f"🔇 {user_mention} تم كتمه لمدة 10 دقائق لتجاوزه 3 إنذارات.\n🔇 {user_mention} has been muted for 10 minutes (3 warnings).")
                    user_warnings[user_id] = 0
                    threading.Thread(target=unmute_user_after_delay, args=(chat_id, user_id)).start()
                except: pass
            else:
                try: bot.send_message(chat_id, f"{warning_msg}\n⚠️ إنذار {user_warnings[user_id]}/3 | Warning {user_warnings[user_id]}/3")
                except: pass
            return "!", 200

    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_EXTERNAL_URL') + '/' + BOT_TOKEN, allowed_updates=['message', 'channel_post'])
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
