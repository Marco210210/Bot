from keyboards import get_new_card_keyboard_with_stand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Funzione per calcolare il valore della mano, gestendo correttamente gli assi
def hand_value(cards):
    """Calcola il valore della mano, trattando gli Assi come 11 o 1 per non sballare."""
    values = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10}
    total = sum(values[c] for c in cards)
    num_aces = cards.count("A")

    while total > 21 and num_aces > 0:
        total -= 10
        num_aces -= 1

    return total

async def suggest_move(query, context: ContextTypes.DEFAULT_TYPE):
    # Recuperiamo le informazioni dal context
    player_hand = context.user_data.get("player_hand", [])
    dealer_card = context.user_data.get("dealer_card", None)

    # Se il giocatore non ha selezionato carte o il dealer non ha scelto una carta, fermiamo tutto
    if not player_hand or dealer_card is None:
        await query.message.reply_text("Errore: Seleziona prima le tue carte e la carta del banco.")
        return

    # Calcoliamo i valori delle mani
    player_total = hand_value(player_hand)

    #Se il giocatore ha raggiunto 21, il turno è concluso
    if player_total == 21:
        await query.message.reply_text("🃏 BLACKJACK! Hai fatto 21! Vittoria 💥", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Nuova mano", callback_data="new_hand")],
            [InlineKeyboardButton("🔙 Menu principale", callback_data="main_menu")]
        ]))
        return

    dealer_value = hand_value([dealer_card]) if dealer_card else 0
    allow_double = len(player_hand) == 2 and not context.user_data.get("has_doubled")
    action = "CARTA"

    # **Gestione della strategia di base**
    
    # Se il giocatore ha una coppia (PAIR SPLITTING)
    if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
        if context.user_data.get("has_split"):
            action = "CARTA"
        else:
            pair = player_hand[0]
            if pair == "A":
                action = "SPLIT"
            elif pair == "10":
                action = "STAI"
            elif pair == "9":
                action = "SPLIT" if dealer_value in [2, 3, 4, 5, 6, 8, 9] else "STAI"
            elif pair == "8":
                action = "SPLIT"
            elif pair == "7":
                action = "SPLIT" if dealer_value in [2, 3, 4, 5, 6, 7] else "CARTA"
            elif pair == "6":
                if dealer_value in [3,4,5,6]:
                    action = "SPLIT"
                elif dealer_value == 2:
                    action = "Splitta se dopo è permesso il raddoppio altrimenti NO"
                else:
                    action = "CARTA"
            elif pair == "5":
                action = "DOPPIO" if dealer_value in [2, 3, 4, 5, 6, 7, 8, 9] else "CARTA"
            elif pair == "4":
                if dealer_value in [5, 6]:
                    action = "Splitta se dopo è permesso il raddoppio altrimenti NO"
                else:
                    action = "CARTA"
            elif pair in ["2", "3"]:
                if dealer_value in [4,5,6,7]:
                    action = "SPLIT"
                elif dealer_value in [2,3]:
                    action = "Splitta se dopo è permesso il raddoppio altrimenti NO"
                else:
                    action = "CARTA"

    #Se il giocatore ha una mano con un Asso (SOFT HAND)
    elif "A" in player_hand and len(player_hand) == 2 and hand_value(player_hand) <= 21:
        second_card = player_hand[1] if player_hand[0] == "A" else player_hand[0]
        soft_hand_actions = {
            "9": "STAI",
            "8": "Doppio se consentito oppure STAI" if dealer_value == 6 else "STAI",
            "7": "Doppio se consentito oppure STAI" if dealer_value in [2, 3, 4, 5, 6] else ("STAI" if dealer_value in [7, 8] else "CARTA"),
            "6": "DOPPIO" if dealer_value in [3, 4, 5, 6] else "CARTA",
            "5": "DOPPIO" if dealer_value in [4, 5, 6] else "CARTA",
            "4": "DOPPIO" if dealer_value in [4, 5, 6] else "CARTA",
            "3": "DOPPIO" if dealer_value in [5, 6] else "CARTA",
            "2": "DOPPIO" if dealer_value in [5, 6] else "CARTA"
        }
        action = soft_hand_actions.get(second_card, "CARTA")

    #Se il giocatore ha una somma normale
    else:
        total_actions = {
            8: "CARTA",
            9: "DOPPIO" if dealer_value in [3, 4, 5, 6] else "CARTA",
            10: "DOPPIO" if dealer_value in [2, 3, 4, 5, 6, 7, 8, 9] else "CARTA",
            11: "DOPPIO",
            12: "STAI" if dealer_value in [4, 5, 6] else "CARTA",
            13: "STAI" if dealer_value in [2, 3, 4, 5, 6] else "CARTA",
            14: "STAI" if dealer_value in [2, 3, 4, 5, 6] else "CARTA",
            15: "STAI" if dealer_value in [2, 3, 4, 5, 6] else ("Arrenditi se consentito (50% della puntata)" if dealer_value == 10 else "CARTA"),
            16: "STAI" if dealer_value in [2, 3, 4, 5, 6] else ("Arrenditi se consentito (50% della puntata)" if dealer_value in [9,10,11] else "CARTA"),
            17: "STAI", 
            18: "STAI", 
            19: "STAI", 
            20: "STAI", 
            21: "🃏 BLACKJACK!"
        }
        action = total_actions.get(player_total, "CARTA")

    #Se doppio non è più permesso, cambia l'azione in CARTA
    if action == "DOPPIO" and not allow_double:
        action = "CARTA"

    #Messaggio di risposta con il suggerimento
    await query.message.reply_text(f"💡Suggerimento: {action}, la tua mano è {player_total}")

    # Gestione dei bottoni per casi speciali
    if action in ["Doppio se consentito oppure STAI", "Splitta se dopo è permesso il raddoppio altrimenti NO", "Arrenditi se consentito (50% della puntata)"]:
        if action == "Doppio se consentito oppure STAI":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Raddoppia", callback_data="double")],
                [InlineKeyboardButton("📥 Chiama Carta", callback_data="extra")],
                [InlineKeyboardButton("🛑 Stai", callback_data="stand")]
            ])
            await query.message.reply_text("💰Vuoi raddoppiare la puntata? Riceverai una sola carta!", reply_markup=reply_markup)
            return

        elif action == "Splitta se dopo è permesso il raddoppio altrimenti NO":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔀 Effettua lo Split", callback_data="split")],
                [InlineKeyboardButton("📥 Chiama Carta", callback_data="extra")],
                [InlineKeyboardButton("🛑 Stai", callback_data="stand")]
            ])
            await query.message.reply_text("🔀 Vuoi splittare la coppia? Considera se dopo è permesso il raddoppio.", reply_markup=reply_markup)
            return

        elif action == "Arrenditi se consentito (50% della puntata)":
            reply_markup = get_new_card_keyboard_with_stand()
            await query.message.reply_text("🏳️ Puoi arrenderti (se consentito) o continuare a giocare:", reply_markup=reply_markup)
            return

    #Se il suggerimento è SPLIT
    if action == "SPLIT":
        keyboard = [
            [InlineKeyboardButton("🔀 Effettua lo Split", callback_data="split")],
            [InlineKeyboardButton("📥 Chiama Carta", callback_data="extra")],
            [InlineKeyboardButton("🛑 Stai", callback_data="stand")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"💡Suggerimento: {action}, la tua mano è {player_total}.", reply_markup=reply_markup)
        return

    if action == "DOPPIO":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Raddoppia", callback_data="double")],
            [InlineKeyboardButton("📥 Chiama Carta", callback_data="extra")],
            [InlineKeyboardButton("🛑 Stai", callback_data="stand")]
        ])
        await query.message.reply_text("💰Vuoi raddoppiare la puntata? Riceverai una sola carta!", reply_markup=reply_markup)
        return
    
    #Se il suggerimento è "CARTA", chiediamo se il giocatore vuole pescare un'altra carta
    if action == "CARTA":
        reply_markup = get_new_card_keyboard_with_stand()
        await query.message.reply_text("Seleziona la carta ricevuta o scegli di stare:", reply_markup=reply_markup)
        return
    
    #Se il giocatore supera 21, mostriamo le opzioni per ricominciare
    if player_total > 21:
        keyboard = [
            [InlineKeyboardButton("🔄 Nuova mano", callback_data="new_hand")],
            [InlineKeyboardButton("🔙 Menu principale", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("💣Boom! Hai superato 21... è uno sballo. Ritenta?", reply_markup=reply_markup)

    #Se il giocatore deve stare, mostriamo il menu
    elif action == "STAI":
        keyboard = [
            [InlineKeyboardButton("🔄 Nuova mano", callback_data="new_hand")],
            [InlineKeyboardButton("🔙 Menu principale", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("✅Fine turno! Pronto per una nuova mano o torni al menu?", reply_markup=reply_markup)
