from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from camelcalc.camelup import Color, Game, LegBetCard


def generate_outcomes(game: Game) -> List[Game]:
    """
    Given a game, generate and return a list of
    all possible roll outcomes
    """

    # Note: using a list to return the possible games is actually
    # faster than using a DoublyLinkedList
    if len(game.die_remaining) == 0:
        return [game]
    outcomes = []
    for color in game.die_remaining:
        for roll in range(1, 4):
            g = deepcopy(game)
            g.move_camel(color, roll)
            g.die_remaining.discard(color)
            outcomes.extend(generate_outcomes(g))
    return outcomes


def calculate_best_leg_bet(game: Game) -> Tuple[Color, float]:
    """
    Determine which camel is the best option to make a
    leg bet on given the current game
    """

    expected_payoffs: Dict[Color, int] = {c: 0 for c in Color}
    payoffs: Dict[Color, Optional[LegBetCard]] = {
        c: game.leg_bet_cards[c][0] if len(game.leg_bet_cards[c]) > 0 else None
        for c in game.leg_bet_cards
    }
    outcomes: List[Game] = generate_outcomes(game)
    for outcome in outcomes:
        positions = outcome.get_positions()
        for c in Color:
            payoff = payoffs[c]
            if payoff is not None:
                expected_payoffs[c] += payoff.get_payoff(positions[c])
    best_bet: Color = max(expected_payoffs, key=expected_payoffs.get)  # type: ignore[type-var]
    expected_payoff = expected_payoffs[best_bet] / len(outcomes)
    return (best_bet, expected_payoff)
