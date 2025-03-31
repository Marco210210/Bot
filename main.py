import signal
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, button, get_player_cards

def handle_exit(signum, frame):
    print("\n🛑 Il bot è stato arrestato manualmente. Arrivederci!")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("player_cards", get_player_cards))
    print("🚀 Bot avviato!")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
