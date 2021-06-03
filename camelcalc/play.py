import curses
from typing import TYPE_CHECKING, List, Set, Tuple

from camelcalc.camelup import Color, Game, TeamName


# This workaround is horrific, but it works
if TYPE_CHECKING:
    from _curses import _CursesWindow

    Window = _CursesWindow
else:
    from typing import Any

    Window = Any


how_to_play = """Camel Up is a betting game based on a camel race.
Each team starts off with 3 coins and on each turn, they can perform one
of the following actions by typing that action into the terminal:
"""


WELCOME_LOCATION: int = 0
GAME_LOCATION: int = 3


# Define commands
class Command:
    keywords: Tuple[str, ...]
    commands: List["Command"] = []
    HELP_PADDING: int = 36

    def __init__(self, keywords: List[str]) -> None:
        self.keywords = tuple(keywords)
        Command.commands.append(self)

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        raise NotImplementedError()

    def help_text(self) -> str:
        raise NotImplementedError()

    def help_text_builder(self, command: str, description: str) -> str:
        command_string = f"{command}:"
        return f"{command_string:<{Command.HELP_PADDING}}{description} Alias {self.keywords[1]}"


class HelpCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["help", "h"])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        commands_string = "\n".join(map(lambda c: c.help_text(), Command.commands))
        return f"{how_to_play}\n{commands_string}"

    def help_text(self) -> str:
        return super().help_text_builder("help", "Show this help message.")


class LegBetCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["bet", "b "])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        color_name = input.split()[1]
        try:
            color = Color(color_name)
            if not game.can_bet_on_leg(color):
                return f"[Error] No leg bet cards remaining for {color}"
            val = game.bet_on_leg(color)
            return f"Team {team} bet on {color} with a max payoff of {val}"
        except ValueError:
            return "[Warning] Invalid color"

    def help_text(self) -> str:
        return super().help_text_builder(
            "bet <color>", "Bet on the <color> camel winning the leg."
        )


class OverallBetCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["overall", "o "])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        _, direction, color_name = input.split()
        try:
            color = Color(color_name)
            winner = direction in ["winner", "w"]
            if not game.can_make_overall_bet(color):
                return (
                    "[Error] Can't make bet on overall winner/loser. "
                    + "Already made an overall bet on that color."
                )
            game.make_overall_bet(winner, color)
            winner_string = "winner" if winner else "loser"
            return f"Team {team} bet on the overall {winner_string}"
        except ValueError:
            return "[Warning] Invalid color"

    def help_text(self) -> str:
        return super().help_text_builder(
            "overall <winner/loser> <color>",
            "Bet on <color> camel winning/losing the overall race",
        )


class PlaceCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["place", "p "])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        _, direction, position = input.split()
        forwards = direction in ["forward", "f"]
        spot = int(position)
        if not game.can_place_movement_card(spot):
            return f"[Error] Can't place a movement card on spot {spot}"
        game.place_movement_card(forwards, spot)
        direction = "+1" if forwards else "-1"
        return f"Team {team} placed a {direction} movement card on spot {spot}"

    def help_text(self) -> str:
        return super().help_text_builder(
            "place <forward/backward> <spot>",
            "Place a +1/-1 movement card on spot <spot>",
        )


class QuitCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["quit", "q"])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        screen.clear()
        screen.addstr(0, 0, "Are you sure you want to quit? [y/N]")
        confirm_raw = screen.getstr(1, 0)
        assert isinstance(confirm_raw, bytes)
        confirm = confirm_raw.decode().lower()
        if confirm in ["yes", "y"]:
            curses.endwin()
            exit(0)
        screen.clear()
        return ""

    def help_text(self) -> str:
        return super().help_text_builder("quit", "Quit the game.")


class RollCommand(Command):
    def __init__(self,) -> None:
        super().__init__(["roll", "r"])

    def process_input(
        self, input: str, game: Game, team: TeamName, screen: Window
    ) -> str:
        color, roll = game.roll_dice()
        return f"Team {team} rolled a {color} {roll}"

    def help_text(self) -> str:
        return super().help_text_builder("roll", "Roll the dice.")


# Register commands
HelpCommand()
LegBetCommand()
OverallBetCommand()
PlaceCommand()
QuitCommand()
RollCommand()


def play(screen: Window) -> None:
    curses.echo()
    while True:
        screen.addstr(0, 0, "Enter the number of teams:")
        screen.refresh()
        teams_raw = screen.getstr(1, 0)
        assert isinstance(teams_raw, bytes)
        try:
            teams = int(teams_raw.decode())
            assert teams > 1 and teams < 9
            screen.clear()
            break
        except (ValueError, AssertionError):
            screen.clear()
            screen.addstr(
                3,
                0,
                "Invalid number of teams. Please enter a number between 2 and 8, inclusive.",
            )
    game = Game(number_of_teams=teams)
    feedback_string: str = ""
    input_location: int = 30
    feedback_location: int = 32
    while game.is_playing():
        input_location = str(game).count("\n") + 6
        feedback_location = input_location + 3
        team = game.active_team
        screen.addstr(
            WELCOME_LOCATION,
            0,
            "Welcome to Camel Up!\nEnter 'help' to learn how to play\n",
        )
        screen.addstr(GAME_LOCATION, 0, str(game))
        screen.addstr(input_location - 1, 0, "Enter a command:")
        screen.addstr(feedback_location, 0, feedback_string)
        choice_raw = screen.getstr(input_location, 0)
        assert isinstance(choice_raw, bytes)
        choice = choice_raw.decode().lower()
        screen.clear()
        screen.addstr(
            WELCOME_LOCATION,
            0,
            "Welcome to Camel Up!\nEnter 'help' to learn how to play\n",
        )

        # Process commands
        found = False
        for command in Command.commands:
            if not found and choice.startswith(command.keywords):
                found = True
                feedback_string = command.process_input(choice, game, team, screen)
                break
        if not found:
            screen.addstr(feedback_location, 0, f"[Warning] Invalid input '{choice}'")
        screen.addstr(GAME_LOCATION, 0, str(game))
        screen.refresh()

    screen.addstr(feedback_location, 0, feedback_string)

    # Determine the winning team(s)
    winners: Set[str] = {t.name for t in game.get_winners()}
    max_coins = max(map(lambda x: x.coins, game.teams.values()))
    winner, verb = ("Winner", "is") if len(winners) == 1 else ("Winners", "are")
    screen.addstr(feedback_location + 2, 0, f"{winner} with {max_coins} coins {verb}:")
    screen.addstr(feedback_location + 3, 0, "\n".join(winners))
    screen.addstr(
        feedback_location + len(winners) + 4, 0, "Press any key to close the game"
    )
    screen.refresh()
    screen.getch()
    curses.endwin()


def main() -> None:
    curses.wrapper(play)


if __name__ == "__main__":
    main()
