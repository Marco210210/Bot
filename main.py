import signal
import sys
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, button, home_command, help_command, reset_command, suggerimento_command, conteggio_command

# Crea l'app Flask
app = Flask(__name__)

# Rende il bot accessibile su un endpoint
@app.route('/')
def home():
    return 'Bot is running!'

# Funzione per gestire la chiusura del bot
def handle_exit(signum, frame):
    print("\n🛑 Il bot è stato arrestato manualmente. Arrivederci!")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)

    # Crea il bot Telegram
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("home", home_command))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("reset", reset_command))
    telegram_app.add_handler(CommandHandler("suggerimento", suggerimento_command))
    telegram_app.add_handler(CommandHandler("conteggio", conteggio_command))
    telegram_app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot avviato!")

    # Avvia il bot in background
    telegram_app.run_polling(close_loop=False)

# Avvia il server Flask in parallelo
if __name__ == "__main__":
    from threading import Thread
    thread = Thread(target=main)
    thread.start()

    # Avvia il server Flask
    app.run(host='0.0.0.0', port=8080)  # Esegui su tutte le interfacce per essere accessibile su Replit
