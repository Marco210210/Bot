# Mappa dei valori Wong Halves per ogni carta
WONG_HALVES_VALUES = {
    "2": 0.5,
    "3": 1,
    "4": 1,
    "5": 1.5,
    "6": 1,
    "7": 0.5,
    "8": 0,
    "9": -0.5,
    "10": -1,
    "A": -1
}

def reset_counting_state(context):
    """Inizializza/resetta il conteggio delle carte nel context."""
    context.user_data["running_count"] = 0
    #context.user_data["num_decks"] = None
    #context.user_data["num_players"] = None
    context.user_data["cards_seen"] = 0

def set_counting_parameters(context, num_players, num_decks):
    """Imposta i parametri iniziali per il conteggio."""
    context.user_data["num_players"] = num_players
    context.user_data["num_decks"] = num_decks

def update_running_count(context, card: str, count_card=True):
    value = WONG_HALVES_VALUES.get(card, 0)
    if count_card:
        context.user_data["running_count"] += value
        context.user_data["cards_seen"] += 1
        print(f"Card: {card}, Value: {value}, Running Count: {context.user_data['running_count']}, Cards Seen: {context.user_data['cards_seen']}")

def get_running_count(context):
    return round(context.user_data.get("running_count", 0), 2)

def get_true_count(context):
    """Restituisce il true count arrotondato in base ai mazzi rimanenti."""
    decks_total = context.user_data.get("num_decks", 1)
    cards_seen = context.user_data.get("cards_seen", 0)
    cards_per_deck = 52
    decks_remaining = max(decks_total - (cards_seen / cards_per_deck), 0.1)  # Limite al minimo di 0.1 per evitare divisioni per 0

    # Log per il calcolo dei mazzi rimanenti
    print(f"Total Decks: {decks_total}, Cards Seen: {cards_seen}, Decks Remaining: {decks_remaining}")

    true_count = context.user_data.get("running_count", 0) / decks_remaining
    return round(true_count, 2)

def reset_counting_state(context):
    """Inizializza/resetta il conteggio delle carte nel context."""
    context.user_data["running_count"] = 0
    context.user_data["cards_seen"] = 0  # Reset dei contatori

def get_practical_message(true_count: float) -> str:
    if true_count >= 4:
        return "🟢 Fortemente favorito! Punta alto! 🚀"
    elif 2 <= true_count < 4:
        return "🟩 Favorito. Buon momento per puntare più alto. 💪"
    elif 1 <= true_count < 2:
        return "🟡 Leggermente favorito. Punta con moderazione. 🙂"
    elif 0 <= true_count < 1:
        return "⚪️ Mazzo neutro. Nessun vantaggio particolare. 😐"
    elif -1 <= true_count < 0:
        return "🟠 Leggermente sfavorito. Mantieni puntate basse. ⚠️"
    elif -3 <= true_count < -1:
        return "🔴 Situazione sfavorevole! Punta il minimo. ❌"
    else:  # true_count < -3
        return "🚩 Molto sfavorevole. Meglio non puntare. 🛑"
