from enum import Enum, auto
from random import randint
from typing import Dict, List, Optional, Set, Tuple

from camelcalc.linkedlist import DoublyLinkedList, Node
from camelcalc.utils import multiline_concat_list, to_string


# There are 16 spots on the board in Camel Up (zero indexed)
BOARD_SPOTS = 15


class InvalidMoveException(Exception):
    """
    An exception representing an invalid move
    """

    pass


def roll_dice() -> int:
    """
    A roll of a die in Camel Up. Camels can move 1, 2, or 3 spaces
    """

    return randint(1, 3)


class Color(Enum):
    """
    Enum defining the different colors of camels
    """

    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    YELLOW = "yellow"
    WHITE = "white"

    def __str__(self) -> str:
        return self.name.capitalize()


class TeamName(Enum):
    """
    Enum defining the different team names
    """

    A = 0
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()
    G = auto()
    H = auto()

    def __str__(self) -> str:
        return self.name


class Camel:
    color: Color
    pos: int

    def __init__(self, color: Color, pos: int) -> None:
        """
        A camel in Camel Up
        """

        self.color = color
        self.pos = pos

    def __str__(self) -> str:
        return str(self.color)


class LegBetCard:
    color: Color
    max_payoff: int

    def __init__(self, color: Color, max_payoff: int) -> None:
        """
        A card representing a bet that the `color` camel will win the
        current leg and has a max payoff of `max_payoff`
        """

        self.color = color
        self.max_payoff = max_payoff

    def get_payoff(self, place: int) -> int:
        """
        Given that the camel being bet on finishes the leg in
        `place` place, return the payoff of this bet.
        """

        if place == 1:
            return self.max_payoff
        elif place == 2:
            return 1
        else:
            return -1

    def __str__(self) -> str:
        return f"{self.color}: max {self.max_payoff}"


class MovementCard:
    team: TeamName
    forward: bool

    def __init__(self, team: TeamName, forward: bool = False) -> None:
        """
        A card, that when placed, will move any camels that land on that
        spot either forward or backward one spot.
        """

        self.team = team
        self.forward = forward

    def __str__(self) -> str:
        direction = "+" if self.forward else "-"
        return f"{self.team.name}: {direction}"


def generate_initial_leg_bet_cards() -> Dict[Color, List[LegBetCard]]:
    """
    Generate the initial 2D array of LegBetCards such that each color
    has cards with max payoff 5, 3, 2, and 2
    """

    bets: Dict[Color, List[LegBetCard]] = {}
    for color in Color:
        max_values = [5, 3, 2]
        bets[color] = list(map(lambda v: LegBetCard(color, v), max_values))
    return bets


class Team:
    name: TeamName
    coins: int
    leg_bet_cards: Set[LegBetCard]
    placed_movement_card: bool
    overall_bets_made: Set[Color]

    def __init__(self, name: TeamName) -> None:
        """
        Represents a team playing Camel Up
        """

        self.name = name
        self.coins = 3
        self.leg_bet_cards = set()
        self.placed_movement_card = False
        self.overall_bets_made = set()

    def __str__(self) -> str:
        team_string = f"Team {self.name.name}:"
        coins_string = f"Coins: {self.coins}"
        movement_card_string_literal = "Yes" if self.placed_movement_card else "No"
        movement_card_string = f"Placed MCard: {movement_card_string_literal}"
        leg_bets_string_literal = (
            "None"
            if len(self.leg_bet_cards) == 0
            else "\n".join(to_string(self.leg_bet_cards))
        )
        leg_bets_string = f"Leg Bets:\n{leg_bets_string_literal}"
        return (
            f"{team_string}\n{coins_string}\n{movement_card_string}\n{leg_bets_string}"
        )


class Spot:
    position: int
    camels: DoublyLinkedList[Camel]
    movement_card: Optional[MovementCard]

    def __init__(self, position: int) -> None:
        """
        Represents a spot that a camel (or multiple camels) can occupy
        """

        self.position = position
        self.camels = DoublyLinkedList()
        self.movement_card = None

    def __str__(self) -> str:
        movement_card_string = (
            "" if self.movement_card is None else str(self.movement_card)
        )
        return f"{self.camels}\n{self.position}\n{movement_card_string}"


def generate_initial_board() -> Tuple[List[Spot], Dict[Color, Camel]]:
    """
    Generate the initial board at the start of the game
    """

    spots: List[Spot] = []
    camels: Dict[Color, Camel] = {}
    for i in range(BOARD_SPOTS + 1):
        spots.append(Spot(i))
    for c in Color:
        roll = roll_dice() - 1
        camel = Camel(c, roll)
        camels[c] = camel
        spots[roll].camels.insert_single_head(camel)
    return spots, camels


class OverallBetCard:
    color: Color
    team: TeamName

    def __init__(self, color: Color, team: TeamName) -> None:
        self.color = color
        self.team = team


class Game:
    teams: Dict[TeamName, Team]
    active_team: TeamName
    die_remaining: Set[Color]
    camels: Dict[Color, Camel]
    spots: List[Spot]
    leg_bet_cards: Dict[Color, List[LegBetCard]]
    overall_winner_cards: List[OverallBetCard]
    overall_loser_cards: List[OverallBetCard]
    playing: bool
    winners: Optional[Set[TeamName]]

    def __init__(self, number_of_teams: int = 8) -> None:
        """
        Represents the current game state in Camel Up
        """
        if number_of_teams < 2 or number_of_teams > 8:
            raise ValueError("number_of_teams must be between 2-8 inclusive")
        self.teams = {name: Team(name) for name in list(TeamName)[:number_of_teams]}
        self.active_team = next(iter(self.teams))
        self.die_remaining = {c for c in Color}
        self.leg_bet_cards = generate_initial_leg_bet_cards()
        self.spots, self.camels = generate_initial_board()
        self.overall_winner_cards = []
        self.overall_loser_cards = []
        self.playing = True
        self.winners = None

    def __str__(self) -> str:
        current_team_string = f"Current Team: {self.active_team.name}"
        die_remaining_string_literal = ", ".join(to_string(self.die_remaining))
        die_remaining_string = f"Die remaining this leg: {die_remaining_string_literal}"
        leg_bet_cards_remaining = list(
            map(
                lambda c: str(self.leg_bet_cards[c][0])
                if len(self.leg_bet_cards[c]) > 0
                else f"{c}: None",
                self.leg_bet_cards,
            )
        )
        leg_bet_cards_string_literal = "\n".join(leg_bet_cards_remaining)
        leg_bet_cards_string = (
            f"Leg Bet cards remaining:\n{leg_bet_cards_string_literal}"
        )
        team_string = multiline_concat_list(to_string(self.teams.values()), False)
        board_string = multiline_concat_list(to_string(self.spots))
        return (
            f"{current_team_string}\n{die_remaining_string}\n"
            + f"{leg_bet_cards_string}\n\n{team_string}\n\n{board_string}"
        )

    def is_playing(self) -> bool:
        """
        Is the game currently being played?
        (has no camel finished yet)
        """

        return self.playing

    def get_winners(self) -> Set[TeamName]:
        """
        Return a set containing the names of
        the winning team(s).

        Raises:
            ValueError: if the game is still
            being played
        """
        if self.playing:
            raise ValueError("Game is still being played")
        assert self.winners is not None
        return self.winners

    def finish_game(self) -> None:
        """
        Finishes a game by awarding final coins.
        Also calculates the winning team(s)
        """

        # Award leg coins
        self.finish_leg()

        # Overall winner/loser bets
        positions = self.get_positions()
        payoffs = [8, 5, 3, 2, 1]
        index = 0
        for card in self.overall_winner_cards:
            if positions[card.color] == 1:
                if index < len(payoffs):  # Only first 5 correct bets receive money
                    self.teams[card.team].coins += payoffs[index]
                    index += 1
            else:
                self.teams[card.team].coins -= 1
        index = 0
        for card in self.overall_loser_cards:
            if positions[card.color] == 5:
                if index < len(payoffs):  # Only first 5 correct bets receive money
                    self.teams[card.team].coins += payoffs[index]
                    index += 1
            else:
                self.teams[card.team].coins -= 1

        # Determine winners
        max_coins = max(map(lambda x: x.coins, self.teams.values()))
        self.winners = {t.name for t in self.teams.values() if t.coins == max_coins}

        # Mark game as finished
        self.playing = False

    def update_camel_positions(self, node: Node[Camel], new_pos: int) -> None:
        """
        Update camel position pointers after they move
        """

        curr: Optional[Node[Camel]] = node
        while curr is not None:
            curr.data.pos = new_pos
            curr = curr.next

    def move_camel(self, color: Color, spots: int) -> None:
        """
        Given a color, move that camel `spots` number of spots
        """

        if spots == 0:
            return
        camel = self.camels[color]
        spot = self.spots[camel.pos]
        temp_node = spot.camels.head
        while temp_node is not None and temp_node.data != camel:
            temp_node = temp_node.next
        camel_node = temp_node
        assert camel_node is not None  # Force not None in mypy
        top_camel = spot.camels.tail
        assert top_camel is not None  # Force not None in mypy
        new_pos = camel.pos + spots
        if spots > 0:
            if new_pos > BOARD_SPOTS:
                self.move_camel(color, BOARD_SPOTS - camel.pos)
                self.finish_game()
                return
            self.update_camel_positions(camel_node, new_pos)
            spot.camels.remove_chain(camel_node)
            self.spots[new_pos].camels.insert_chain_tail(camel_node, top_camel)
        else:
            self.update_camel_positions(camel_node, new_pos)
            spot.camels.remove_chain(camel_node)
            self.spots[new_pos].camels.insert_chain_head(camel_node, top_camel)

        # Handle additional movement card movement
        movement_card = self.spots[new_pos].movement_card
        if movement_card is not None:
            self.teams[movement_card.team].coins += 1
            offset = 1 if movement_card.forward else -1
            self.move_camel(color, offset)

    def get_positions(self) -> Dict[Color, int]:
        """
        Returns a dictionary of camel color to position
        (first through fifth)
        """

        place: int = 1
        index: int = 15
        results: Dict[Color, int] = {}
        while place < 6:
            curr: Optional[Node[Camel]] = self.spots[index].camels.tail
            while curr is not None:
                results[curr.data.color] = place
                place += 1
                curr = curr.prev
            index -= 1
        return results

    def finish_leg(self) -> None:
        """
        Reset board state after a leg has been finished
        """

        # Mark all die as unused
        self.die_remaining = {c for c in Color}

        # Update each team's coins based on their leg bets
        positions = self.get_positions()
        for team in self.teams.values():
            for card in team.leg_bet_cards:
                team.coins += card.get_payoff(positions[card.color])
            team.leg_bet_cards.clear()

        # Reset the leg bet cards
        self.leg_bet_cards = generate_initial_leg_bet_cards()

        # Reset movement cards
        for team in self.teams.values():
            team.placed_movement_card = False
        for spot in self.spots:
            spot.movement_card = None

    def finish_turn(self) -> None:
        """
        Finish a team's turn and mark the next team as active
        """

        self.active_team = TeamName((self.active_team.value + 1) % len(self.teams))

    # Can a team make one of the following moves

    def can_bet_on_leg(self, color: Color) -> bool:
        """
        Can a leg bet be made on `color` camel
        """

        return len(self.leg_bet_cards[color]) > 0

    def can_place_movement_card(self, position: int) -> bool:
        """
        Can a movement card be placed in a given spot?
        """

        # Can only place a single movement card in this leg
        if self.teams[self.active_team].placed_movement_card:
            return False

        # Can only place a movement card from the second to last spot
        if position < 1 or position > BOARD_SPOTS:
            return False

        # Can only place a movement card if the spot behind doesn't have one
        if self.spots[position - 1].movement_card is not None:
            return False

        # Can only place a movement card if the spot ahead doesn't have one
        if (
            position < BOARD_SPOTS
            and self.spots[position + 1].movement_card is not None
        ):
            return False

        # Can only place a movement card if the spot doesn't have one
        if self.spots[position].movement_card is not None:
            return False

        # Can only place a movement card if the spot is empty
        if self.spots[position].camels.head is not None:
            return False
        return True

    def can_make_overall_bet(self, color: Color) -> bool:
        """
        Can a team make an overall winner/loser bet of color `color`
        """

        return color not in self.teams[self.active_team].overall_bets_made

    # Actions each team can choose from on their turn

    def roll_dice(self) -> Tuple[Color, int]:
        """
        Team `team` rolls the dice
        """

        self.teams[self.active_team].coins += 1
        color = self.die_remaining.pop()
        move = roll_dice()
        self.move_camel(color, move)
        if len(self.die_remaining) == 0:
            self.finish_leg()
        self.finish_turn()
        return color, move

    def bet_on_leg(self, color: Color) -> int:
        """
        Team `team` bets on `color` camel winning the leg

        Raises:
            InvalidMoveException: if a leg bet can't be
            made with the given inputs
        """

        if not self.can_bet_on_leg(color):
            raise InvalidMoveException()
        card = self.leg_bet_cards[color].pop(0)
        self.teams[self.active_team].leg_bet_cards.add(card)
        self.finish_turn()
        return card.max_payoff

    def place_movement_card(self, direction: bool, position: int) -> None:
        """
        Place a movement card in the `direction` direction
        at position `position`

        Raises:
            InvalidMoveException: if a movement card can't be
            placed with the given inputs
        """
        if not self.can_place_movement_card(position):
            raise InvalidMoveException()

        self.spots[position].movement_card = MovementCard(self.active_team, direction)
        self.teams[self.active_team].placed_movement_card = True
        self.finish_turn()

    def make_overall_bet(self, winner: bool, color: Color) -> None:
        """
        Make a bet on the overall winner/loser.

        Raises:
            InvalidMoveException: if an overall bet can't be
            made with the given inputs
        """

        if not self.can_make_overall_bet(color):
            raise InvalidMoveException()

        self.teams[self.active_team].overall_bets_made.add(color)
        if winner:
            self.overall_winner_cards.append(OverallBetCard(color, self.active_team))
        else:
            self.overall_loser_cards.append(OverallBetCard(color, self.active_team))
