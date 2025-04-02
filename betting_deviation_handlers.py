from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# Funzione per chiedere il budget iniziale (Bankroll)
async def ask_bankroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica se l'update è una callback query o un messaggio
    if update.message:
        await update.message.reply_text("💰 Inserisci il tuo budget iniziale (Bankroll) in euro (solo numeri interi):")
    elif update.callback_query:
        await update.callback_query.message.reply_text("💰 Inserisci il tuo budget iniziale (Bankroll) in euro (solo numeri interi):")


# Funzione per gestire la risposta del budget iniziale
async def handle_bankroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bankroll = int(update.message.text)
        if bankroll <= 0:
            await update.message.reply_text("Il budget deve essere un numero positivo. Riprova.")
            return
        context.user_data["bankroll"] = bankroll
        await ask_min_bet(update, context)
    except ValueError:
        await update.message.reply_text("Per favore, inserisci un numero intero valido per il budget.")

# Funzione per chiedere la puntata minima
async def ask_min_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💸 Qual è la puntata minima che vuoi fare (in euro)?")

# Funzione per gestire la risposta della puntata minima
async def handle_min_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        min_bet = int(update.message.text)
        if min_bet <= 0:
            await update.message.reply_text("La puntata minima deve essere un numero positivo. Riprova.")
            return
        context.user_data["min_bet"] = min_bet
        await ask_bet_increase(update, context)
    except ValueError:
        await update.message.reply_text("Per favore, inserisci un numero intero valido per la puntata minima.")

# Funzione per chiedere l'incremento della puntata
async def ask_bet_increase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Qual è l'incremento della puntata che desideri applicare?")

# Funzione per gestire la risposta dell'incremento della puntata
async def handle_bet_increase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bet_increase = int(update.message.text)
        if bet_increase < 0:
            await update.message.reply_text("L'incremento della puntata non può essere negativo. Riprova.")
            return
        context.user_data["bet_increase"] = bet_increase
        await ask_risk_level(update, context)
    except ValueError:
        await update.message.reply_text("Per favore, inserisci un numero intero valido per l'incremento della puntata.")

# Funzione per chiedere la propensione al rischio
async def ask_risk_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Basso", callback_data="risk_low")],
        [InlineKeyboardButton("Medio", callback_data="risk_medium")],
        [InlineKeyboardButton("Alto", callback_data="risk_high")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎲 Quanto sei disposto a rischiare? Scegli il tuo livello di rischio:", reply_markup=reply_markup)

# Funzione per gestire la risposta della propensione al rischio
async def handle_risk_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    risk_level = query.data.split("_")[1]
    context.user_data["risk_level"] = risk_level

    # Una volta ricevuto il livello di rischio, si può proseguire con la fase successiva (es. numero di giocatori)
    #await ask_players(update, context)  # Questo è solo un esempio per la continuazione
