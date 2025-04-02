from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_logic import suggest_move, hand_value
from keyboards import get_player_cards_keyboard, get_new_card_keyboard, send_dealer_card_selection, get_player_count_keyboard, get_deck_count_keyboard
from card_count import reset_counting_state
from card_count_handlers import (
    start_card_counting,
    handle_player_count_selection,
    handle_position_selection,
    handle_deck_count_selection,
    handle_card_selection,
    handle_playcard_selection,
    handle_nextplayer,
    show_card_keyboard
)

from betting_deviation_handlers import ask_bankroll, handle_bankroll, ask_min_bet, handle_min_bet, ask_bet_increase, handle_bet_increase, ask_risk_level, handle_risk_level

def get_end_options_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Nuova mano", callback_data="new_hand")],
        [InlineKeyboardButton("🔙 Menu principale", callback_data="main_menu")]
    ])

def reset_game_state(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["player_hand"] = []
    context.user_data["dealer_card"] = None

# Funzione di start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Inizializza le variabili nel context se non esistono
    context.user_data.setdefault("player_hand", [])
    context.user_data.setdefault("dealer_card", None)

    keyboard = [
        [InlineKeyboardButton("Conteggio Carte", callback_data='count_cards')],
        [InlineKeyboardButton("Suggerimenti di Gioco", callback_data='game_advice')],
        [InlineKeyboardButton("Entrambe", callback_data='both')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Controlliamo se è un comando normale o una callback query
    if update.message:
        await update.message.reply_text("🎰 Benvenuto al tavolo di Black Jack! Scegli il tipo di assistenza che desideri:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text("🎰 Benvenuto al tavolo di Black Jack! Scegli il tipo di assistenza che desideri:", reply_markup=reply_markup)

async def get_player_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra la tastiera per selezionare la prima carta del giocatore."""
    reply_markup = get_player_cards_keyboard()

    if update.callback_query:
        await update.callback_query.message.reply_text("🃏 Qual è la tua prima carta?", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🃏 Qual è la tua prima carta?", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    player_hand = context.user_data.setdefault("player_hand", [])

    if query.data.startswith("players_"):
        await handle_player_count_selection(update, context)
        return

    if query.data.startswith("position_"):
        await handle_position_selection(update, context)
        return

    if query.data.startswith("decks_"):
        await handle_deck_count_selection(update, context)
        return

    if query.data.startswith("card_"):
        await handle_card_selection(update, context)
        return
    
    if query.data.startswith("playcard_"):
        await handle_playcard_selection(update, context)
        return

    if query.data == "nextplayer":
        await handle_nextplayer(update, context)
        return

    if query.data == "game_advice":
        await query.edit_message_text("Modalità Suggerimenti di Gioco attivata! Ora seleziona le tue carte.")
        await get_player_cards(update, context)
        return
    
    if query.data == "count_cards":
        await start_card_counting(update, context)
        return

    if query.data in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        player_hand.append(query.data)

        if len(player_hand) == 1:
            await query.edit_message_text(f"Prima carta scelta: {player_hand[0]}\nOra seleziona la seconda carta.")
            await query.message.reply_text("Seleziona la seconda carta:", reply_markup=get_player_cards_keyboard())
        elif len(player_hand) == 2:
            await query.edit_message_text(f"Le tue carte sono: {player_hand[0]} e {player_hand[1]}\nOra seleziona la carta del banco.")
            await send_dealer_card_selection(update)
        return

    if query.data.startswith("dealer_"):
        context.user_data["dealer_card"] = query.data.split("_")[1]
        await query.edit_message_text(f"Il banco ha {context.user_data['dealer_card']}.")
        await suggest_move(query, context)
        return

    if query.data == "split":
        context.user_data["has_split"] = True
        card1, card2 = context.user_data["player_hand"]
        context.user_data["hand1"] = [card1]
        context.user_data["hand2"] = [card2]
        context.user_data["current_hand"] = 1
        context.user_data["player_hand"] = []
        await query.edit_message_text("Hai scelto di splittare! Seleziona la carta per la mano 1:")
        await query.message.reply_text("Seleziona la carta:", reply_markup=get_new_card_keyboard())
        return
    
    if query.data == "double":
        context.user_data["has_doubled"] = True
        await query.edit_message_text("Hai scelto di raddoppiare! Seleziona la carta che hai ricevuto:")
        await query.message.reply_text("Seleziona la carta:", reply_markup=get_new_card_keyboard())
        return

    if query.data == "new_hand":
        reset_game_state(context)
        await query.edit_message_text("Inizia una nuova mano!")
        await query.message.reply_text("🃏 Qual è la tua prima carta?", reply_markup=get_player_cards_keyboard())
        return

    if query.data == "main_menu":
        reset_game_state(context)
        await start(update.callback_query, context)
        return
    
    if query.data == "extra":
        # Il giocatore rifiuta doppio o split, continua come mano normale
        context.user_data["has_doubled"] = False
        context.user_data["has_split"] = False
        await query.edit_message_text("Hai scelto di chiamare carta normalmente.")
        await query.message.reply_text("Inserisci la carta ricevuta:", reply_markup=get_new_card_keyboard())
        return

    if query.data == "stand":
        await query.message.reply_text("🛑Hai scelto di stare. Vediamo come va a finire...", reply_markup=get_end_options_keyboard())
        return

    if query.data.startswith("extra_"):
        new_card = query.data.split("_")[1]

        # Se siamo in modalità split
        if "current_hand" in context.user_data:
            current_hand = context.user_data["current_hand"]

            if current_hand == 1:
                context.user_data["hand1"].append(new_card)
                player_total = hand_value(context.user_data["hand1"])
                hand_label = "Mano 1"
            else:
                context.user_data["hand2"].append(new_card)
                player_total = hand_value(context.user_data["hand2"])
                hand_label = "Mano 2"

            await query.edit_message_text(f"Hai pescato: {new_card}. {hand_label} è ora {player_total}.")

            if player_total > 21:
                if current_hand == 1:
                    context.user_data["hand1_busted"] = True
                    context.user_data["current_hand"] = 2
                    await query.message.reply_text("💥 Hai sballato! Passiamo alla seconda mano.")
                    await query.message.reply_text("Seleziona la carta per la seconda mano:", reply_markup=get_new_card_keyboard())
                else:
                    if context.user_data.get("hand1_busted"):
                        msg = "💥 Hai sballato entrambe le mani! Turno completato."
                    else:
                        msg = "💥 Hai sballato nella seconda mano! Turno completato."
                    await query.message.reply_text(msg)
                    await query.message.reply_text("Scegli un'opzione:", reply_markup=get_end_options_keyboard())
                return

            if player_total >= 17 or (player_total >= 12 and context.user_data["dealer_card"] in ["4", "5", "6"]):
                if current_hand == 1:
                    context.user_data["current_hand"] = 2
                    await query.message.reply_text(f"🛑 Stai con {player_total}. Passiamo alla seconda mano.")
                    await query.message.reply_text("Seleziona la carta per la seconda mano:", reply_markup=get_new_card_keyboard())
                    return
                else:
                    await query.message.reply_text(f"🛑 Stai con {player_total}. Turno completato.")
                    await query.message.reply_text("Scegli un'opzione:", reply_markup=get_end_options_keyboard())
                    return

            # Mostra il suggerimento per la mano corrente (usando suggest_move)
            temp_hand = context.user_data["hand1"] if current_hand == 1 else context.user_data["hand2"]
            context.user_data["player_hand"] = temp_hand
            await suggest_move(query, context)
            return

        # Caso normale (no split)
        player_hand = context.user_data.setdefault("player_hand", [])
        player_hand.append(new_card)
        player_total = hand_value(player_hand)
        await query.edit_message_text(f"Hai inserito: {new_card}.")

        if context.user_data.get("has_doubled"):
            await query.message.reply_text(f"Hai raddoppiato, ora hai {player_total}. Non puoi ricevere altre carte.")
            await query.message.reply_text("Scegli un'opzione:", reply_markup=get_end_options_keyboard())
            return

        if player_total > 21:
            await query.message.reply_text("💣 Boom! Hai superato 21... è uno sballo. Ritenta?", reply_markup=get_end_options_keyboard())
            return

        if 17 <= player_total <= 21:
            await query.message.reply_text(f"💡Suggerimento: STAI, la tua mano è {player_total}. Turno completato.")
            await query.message.reply_text(f"Scegli un'opzione:", reply_markup=get_end_options_keyboard())
            return

        # MODIFICA QUI: Assicurati di aggiornare sempre la mano corrente
        context.user_data["player_hand"] = player_hand

        await suggest_move(query, context)
        return
    
    if query.data == "continue_same":
        context.user_data["current_player"] = 1
        context.user_data["phase"] = "initial"
        context.user_data["temp_cards"] = []
        context.user_data["dealer_cards"] = []
        context.user_data["players_cards"] = {}
        await query.edit_message_text("🔁 Si riparte! Inserisci le 2 carte del giocatore 1.")
        await show_card_keyboard(update, context)
        return

    if query.data == "change_players":
        await query.edit_message_text("👥 Seleziona il nuovo numero di giocatori:", reply_markup=get_player_count_keyboard())
        return

    if query.data == "reset_counting":
        reset_game_state(context)
        reset_counting_state(context)
        await start(update, context)
        return

# Comando /home
async def home_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("Conteggio Carte", callback_data='count_cards')],
        [InlineKeyboardButton("Suggerimenti di Gioco", callback_data='game_advice')],
        [InlineKeyboardButton("Entrambe", callback_data='both')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🏠 Sei tornato al menu principale. Cosa vuoi fare ora?", reply_markup=reply_markup)

# Comando /suggerimento
async def suggerimento_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🃏 Modalità Suggerimenti di Gioco attivata! Inserisci le tue carte:")
    await update.message.reply_text("Qual è la tua prima carta?", reply_markup=get_player_cards_keyboard())

# Comando /conteggio
async def conteggio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_counting_state(context)
    await update.message.reply_text("🧮 Modalità Conteggio Carte attivata!")
    await update.message.reply_text("Quanti giocatori ci sono al tavolo?", reply_markup=get_player_count_keyboard())

# Comando /reset
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🔄 Partita resettata! Usa /start per ricominciare.")

# Comando /help (migliorato)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 <b>Aiuto e istruzioni</b>\n\n"
        "Benvenuto nel <b>BlackJack Assistant Bot</b>! Ecco come utilizzarmi al meglio:\n\n"
        "🎲 <b>/start</b> - Avvia il bot e scegli la modalità desiderata\n"
        "🏠 <b>/home</b> - Torna rapidamente al menu principale\n"
        "🃏 <b>/suggerimento</b> - Accedi ai suggerimenti strategici di gioco\n"
        "🧮 <b>/conteggio</b> - Attiva la modalità conteggio carte (Sistema Wong Halves)\n"
        "🔄 <b>/reset</b> - Resetta tutte le impostazioni della partita corrente\n\n"
        "<i>In ogni momento puoi usare questi comandi per navigare velocemente tra le varie sezioni. Buon divertimento! 🎉</i>"
    )
    await update.message.reply_html(help_text)

# Funzione per gestire la risposta del comando /entrambi
async def both(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Iniziamo chiedendo il bankroll
    await ask_bankroll(update, context)