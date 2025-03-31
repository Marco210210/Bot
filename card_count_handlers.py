from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards import get_player_count_keyboard, get_deck_count_keyboard, build_card_keyboard
from card_count import reset_counting_state, set_counting_parameters, update_running_count, get_running_count, get_true_count, get_practical_message

# Avvio della modalità conteggio carte
def get_position_keyboard(num_players):
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"position_{i}") for i in range(1, num_players + 1)]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_card_counting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_counting_state(context)
    await update.callback_query.message.edit_text("Quanti giocatori ci sono al tavolo?", reply_markup=get_player_count_keyboard())

# Gestione della scelta del numero di giocatori
async def handle_player_count_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    num_players = int(query.data.split("_")[1])
    context.user_data["num_players"] = num_players

    await query.edit_message_text(
        text="In che posizione sei seduto al tavolo?",
        reply_markup=get_position_keyboard(num_players)
    )

# Gestione della scelta della posizione del giocatore
async def handle_position_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    position = int(query.data.split("_")[1])
    context.user_data["player_position"] = position

    await query.edit_message_text(
        text="Quanti mazzi vengono utilizzati?",
        reply_markup=get_deck_count_keyboard()
    )

# Gestione della scelta del numero di mazzi
async def handle_deck_count_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reset_counting_state(context)
    num_decks = int(query.data.split("_")[1])
    num_players = context.user_data["num_players"]

    context.user_data["num_decks"] = num_decks
    context.user_data["num_players"] = num_players
    context.user_data["current_player"] = 1
    context.user_data["card_log"] = []
    context.user_data["phase"] = "initial"

    set_counting_parameters(context, num_players, num_decks)

    await query.edit_message_text("Inizio inserimento carte. Inserisci le 2 carte del giocatore 1:")
    await show_card_keyboard(update, context)

# Mostra tastiera per inserimento carta
async def show_card_keyboard(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    phase = context.user_data.get("phase")
    current_player = context.user_data.get("current_player")
    player_position = context.user_data.get("player_position")
    card_num = len(context.user_data.get("temp_cards", [])) + 1
    dealer_cards = context.user_data.get("dealer_cards", [])

    # Messaggio e tastiera per il dealer
    if phase == "dealer":
        msg = "Inserisci la carta scoperta del dealer:"
        keyboard = build_card_keyboard("card_")
    elif phase == "dealer_play":
        if len(dealer_cards) == 0:
            msg = "Inserisci la seconda carta del dealer:"
            keyboard = build_card_keyboard("card_")
        else:
            msg = "Inserisci una carta per il dealer o premi ⏭️ se ha deciso di stare:"
            keyboard = get_play_keyboard()
    else:
        # Messaggio e tastiera per i giocatori
        if current_player == player_position:
            msg = f"Inserisci la tua {'prima' if card_num == 1 else 'seconda'} carta:"
        else:
            msg = f"Inserisci la carta {card_num} per il giocatore {current_player}:"
        keyboard = build_card_keyboard("card_")

    if update_or_query.message:
        await update_or_query.message.reply_text(msg, reply_markup=keyboard)
    elif update_or_query.callback_query:
        await update_or_query.callback_query.message.reply_text(msg, reply_markup=keyboard)

async def handle_card_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    card = query.data.split("_")[1]
    phase = context.user_data.get("phase", "initial")

    # Conta la carta SOLO se la fase è 'initial', 'dealer' oppure 'dealer_play'
    if phase in ["initial", "dealer", "dealer_play"]:
        update_running_count(context, card)
        context.user_data["card_log"].append(card)

    if phase == "dealer":
        context.user_data["dealer_card"] = card
        context.user_data["phase"] = "playing"
        await query.edit_message_text(f"Il dealer ha ricevuto: {card}.")
        await start_player_actions(query, context)
        return

    if phase == "dealer_play":
        dealer_cards = context.user_data.setdefault("dealer_cards", [])
        dealer_cards.append(card)
        await query.edit_message_text(f"Il dealer ha pescato: {card}.")
        return await show_card_keyboard(update, context)

    temp_cards = context.user_data.setdefault("temp_cards", [])
    temp_cards.append(card)

    if len(temp_cards) == 2:
        player = context.user_data["current_player"]
        context.user_data.setdefault("players_cards", {})[player] = temp_cards.copy()
        context.user_data["temp_cards"] = []

        if player == context.user_data.get("player_position"):
            await query.edit_message_text(f"Tu hai: {', '.join(temp_cards)}.")
        else:
            await query.edit_message_text(f"Giocatore {player} ha ricevuto: {', '.join(temp_cards)}.")

        await advance_player_flow(query, context)
    else:
        await show_card_keyboard(update, context)

# Gestisce il passaggio al prossimo giocatore o al dealer
async def advance_player_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = context.user_data["current_player"]
    total = context.user_data["num_players"]
    player_position = context.user_data.get("player_position")

    if current < total:
        context.user_data["current_player"] += 1
        next_player = context.user_data["current_player"]

        if next_player == player_position:
            await update.message.reply_text("Inserisci le tue carte:")
        else:
            await update.message.reply_text(f"Inserisci le carte del giocatore {next_player}:")

        await show_card_keyboard(update, context)
    else:
        context.user_data["phase"] = "dealer"
        context.user_data["dealer_card_inserted"] = False
        await update.message.reply_text("Inserisci la carta scoperta del dealer:")
        await show_card_keyboard(update, context)

def get_play_keyboard():
    keyboard = [
        [InlineKeyboardButton("A", callback_data="playcard_A"), InlineKeyboardButton("2", callback_data="playcard_2"), InlineKeyboardButton("3", callback_data="playcard_3")],
        [InlineKeyboardButton("4", callback_data="playcard_4"), InlineKeyboardButton("5", callback_data="playcard_5"), InlineKeyboardButton("6", callback_data="playcard_6")],
        [InlineKeyboardButton("7", callback_data="playcard_7"), InlineKeyboardButton("8", callback_data="playcard_8"), InlineKeyboardButton("9", callback_data="playcard_9")],
        [InlineKeyboardButton("10", callback_data="playcard_10")],
        [InlineKeyboardButton("⏭️ Prossimo", callback_data="nextplayer")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_player_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_player"] = 1
    await show_player_turn(update, context)

async def show_player_turn(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    current = context.user_data["current_player"]
    num_players = context.user_data["num_players"]
    player_pos = context.user_data["player_position"]

    if current > num_players:
        context.user_data["phase"] = "dealer_play"
        await update_or_query.message.reply_text("🃏 È il turno del dealer. Inserisci le carte del dealer una alla volta:")
        await show_card_keyboard(update_or_query, context)
        return

    if current == player_pos:
        running = get_running_count(context)
        true = get_true_count(context)
        await update_or_query.message.reply_text(
            f"🧮 È il tuo turno!\n🔢 Running Count: {running}\n📊 True Count: {true}"
        )

    await update_or_query.message.reply_text(
        f"🎯 Turno del giocatore {current}. Inserisci una carta o vai al prossimo giocatore:",
        reply_markup=get_play_keyboard()
    )

async def handle_playcard_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    card = query.data.split("_")[1]
    phase = context.user_data.get("phase")

    # Conta la carta SOLO se la fase è 'dealer_play' o 'playing' (carte aggiuntive dopo la distribuzione iniziale)
    if phase in ["dealer_play", "playing"]:
        update_running_count(context, card)
        context.user_data["card_log"].append(card)

    if phase == "dealer_play":
        dealer_cards = context.user_data.setdefault("dealer_cards", [])
        dealer_cards.append(card)
        await query.edit_message_text(f"Il dealer ha pescato: {card}.")
        await show_card_keyboard(query, context)
        return

    player = context.user_data["current_player"]
    context.user_data.setdefault("extra_cards", {}).setdefault(player, []).append(card)

    await query.edit_message_text(f"Giocatore {player} ha pescato: {card}.")
    await show_player_turn(query, context)

async def handle_nextplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("phase") == "dealer_play":
        await query.edit_message_text("🛑 Il dealer ha deciso di stare.")
        await finish_dealer_turn(query, context)
    else:
        context.user_data["current_player"] += 1
        await show_player_turn(query, context)


async def finish_dealer_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    running = get_running_count(context)
    true = get_true_count(context)
    practical_message = get_practical_message(true)

    await update.message.reply_text(
        f"✅ Fine turno del dealer!\n"
        f"🔢 Running Count: {running}\n"
        f"📊 True Count: {true}\n\n"
        f"{practical_message}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Continua con stessi giocatori", callback_data="continue_same")],
            [InlineKeyboardButton("👥 Modifica numero giocatori", callback_data="change_players")],
            [InlineKeyboardButton("🧼 Ripristina conteggio", callback_data="reset_counting")]
        ])
    )
