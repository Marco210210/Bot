import signal
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, button, get_player_cards, help_command, reset_command

def handle_exit(signum, frame):
    print("\n🛑 Il bot è stato arrestato manualmente. Arrivederci!")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)
    app = Application.builder().token(TOKEN).build()
    # Comandi esistenti
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("player_cards", get_player_cards))
    
    # Nuovi comandi
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))
    
    # Callback dei bottoni
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot avviato!")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
