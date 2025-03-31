from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

def build_card_keyboard(prefix: str = ""):
    """Genera una tastiera per carte da A a 10 con callback personalizzabile."""
    keyboard = [
        [InlineKeyboardButton("A", callback_data=f"{prefix}A"), InlineKeyboardButton("2", callback_data=f"{prefix}2"), InlineKeyboardButton("3", callback_data=f"{prefix}3")],
        [InlineKeyboardButton("4", callback_data=f"{prefix}4"), InlineKeyboardButton("5", callback_data=f"{prefix}5"), InlineKeyboardButton("6", callback_data=f"{prefix}6")],
        [InlineKeyboardButton("7", callback_data=f"{prefix}7"), InlineKeyboardButton("8", callback_data=f"{prefix}8"), InlineKeyboardButton("9", callback_data=f"{prefix}9")],
        [InlineKeyboardButton("10", callback_data=f"{prefix}10")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_player_cards_keyboard():
    return build_card_keyboard()

def get_new_card_keyboard():
    return build_card_keyboard("extra_")

def get_dealer_cards_keyboard():
    return build_card_keyboard("dealer_")

def get_new_card_keyboard_with_stand():
    base_keyboard = [
        [InlineKeyboardButton("A", callback_data="extra_A"), InlineKeyboardButton("2", callback_data="extra_2"), InlineKeyboardButton("3", callback_data="extra_3")],
        [InlineKeyboardButton("4", callback_data="extra_4"), InlineKeyboardButton("5", callback_data="extra_5"), InlineKeyboardButton("6", callback_data="extra_6")],
        [InlineKeyboardButton("7", callback_data="extra_7"), InlineKeyboardButton("8", callback_data="extra_8"), InlineKeyboardButton("9", callback_data="extra_9")],
        [InlineKeyboardButton("10", callback_data="extra_10")],
        [InlineKeyboardButton("🛑 Stai", callback_data="stand")]
    ]
    return InlineKeyboardMarkup(base_keyboard)

async def send_dealer_card_selection(update: Update):
    """Mostra la tastiera per selezionare la carta del banco."""
    reply_markup = get_dealer_cards_keyboard()

    if update.callback_query:
        await update.callback_query.message.reply_text("Seleziona la carta del banco:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Seleziona la carta del banco:", reply_markup=reply_markup)

def get_player_count_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"players_{i}") for i in range(1, 8)]
    ])

def get_deck_count_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"decks_{i}") for i in range(2, 9)]
    ])
