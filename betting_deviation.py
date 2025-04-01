# betting_deviation.py

def calculate_betting_deviation(true_count, betting_unit, min_bet, max_bet):
    """Calcola la puntata in base al True Count, alla Betting Unit e alla puntata minima."""
    # Se il True Count è negativo o pari a zero, si mantiene la puntata minima
    if true_count <= 0:
        bet = min_bet
    else:
        # La puntata aumenta con il True Count
        bet = min_bet + (true_count * betting_unit)
    
    # Limita la puntata massima
    if bet > max_bet:
        bet = max_bet
    
    return bet

def get_betting_deviation_message(true_count, betting_unit, min_bet, max_bet):
    """Genera un messaggio con il suggerimento della puntata basata sul True Count."""
    bet = calculate_betting_deviation(true_count, betting_unit, min_bet, max_bet)
    return f"💡 Con un True Count di {true_count}, la tua puntata suggerita è: {bet}€"

def get_betting_unit(bankroll, risk_level):
    """Calcola la Betting Unit in base al bankroll e alla propensione al rischio."""
    if risk_level == "alta":
        return bankroll * 0.05  # Puntata più alta per rischio alto
    elif risk_level == "media":
        return bankroll * 0.03  # Puntata media
    else:
        return bankroll * 0.01  # Puntata bassa per rischio basso
