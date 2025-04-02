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
    # Avvia il bot normalmente nel thread principale
    application = Application.builder().token(TOKEN).build()

    # Aggiungi i comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("home", home_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("suggerimento", suggerimento_command))
    application.add_handler(CommandHandler("conteggio", conteggio_command))

    # Aggiungi i CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot avviato!")
    # Avvia il bot in modalità polling nel thread principale
    application.run_polling()

# Definisci il tuo endpoint Flask
@app.route('/')
def home():
    return 'Il bot è attivo e funzionante!'

if __name__ == "__main__":
    # Esegui il server Flask in un thread separato
    from threading import Thread

    # Esegui Flask nella thread principale (non separata)
    flask_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
    flask_thread.start()

    # Esegui il bot nel thread principale
    start_bot()
