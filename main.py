import sys
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import asyncio
from config import TOKEN
from handlers import start, button, home_command, help_command, reset_command, suggerimento_command, conteggio_command

# Crea un'app Flask
app = Flask(__name__)

# Funzione di start per il bot
def start_bot():
    # Avvia il bot normalmente
    app = Application.builder().token(TOKEN).build()

    # Aggiungi i comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("home", home_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("suggerimento", suggerimento_command))
    app.add_handler(CommandHandler("conteggio", conteggio_command))

    # Aggiungi i CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot avviato!")
    app.run_polling(close_loop=False)

# Definisci il tuo endpoint Flask
@app.route('/')
def home():
    return 'Il bot è attivo e funzionante!'

if __name__ == "__main__":
    from threading import Thread

    # Esegui il bot in un thread separato
    bot_thread = Thread(target=start_bot)
    bot_thread.start()

    # Esegui Flask nella thread principale
    app.run(host="0.0.0.0", port=8080)
