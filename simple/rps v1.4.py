import os
import sys
import random
import time
import inspect
import rich

if os.name == "nt":
    import msvcrt
else:
    import select
    import termios
    import tty

VERSION = "1.4"
DELAY = 3

BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
CHOICES = list(BEATS)

ALIASES = {
    "a": "rock", "1": "rock", "rock": "rock",
    "b": "paper", "2": "paper", "paper": "paper",
    "c": "scissors", "3": "scissors", "scissors": "scissors",
}

EMPTY_STATS = {"wins": 0, "draws": 0, "losses": 0, "streak": 0, "best_streak": 0}

cls = lambda: os.system("cls" if os.name == "nt" else "clear")


def setup_terminal():
    if os.name == "nt":
        os.system(f"title rps game v{VERSION} made by splars#1252")


def wait(seconds=DELAY):
    rich.print("\n[bright_black]Press any key to continue...[/]")

    if os.name == "nt":
        end = time.time() + seconds
        while time.time() < end:
            if msvcrt.kbhit():
                msvcrt.getwch()
                return
            time.sleep(0.02)
        return

    if not sys.stdin.isatty():
        time.sleep(seconds)
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ready, _, _ = select.select([sys.stdin], [], [], seconds)
        if ready:
            os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def win_ratio(stats):
    decided = stats["wins"] + stats["losses"]
    return f"{stats['wins'] / decided:.0%}" if decided else "0%"


def get_result(player, computer):
    if player == computer:
        return "draw"
    return "win" if BEATS[player] == computer else "loss"


def update_stats(stats, result):
    if result == "win":
        stats["wins"] += 1
        stats["streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["streak"])
    elif result == "draw":
        stats["draws"] += 1
    else:
        stats["losses"] += 1
        stats["streak"] = 0


def show_menu(stats, last_choice):
    total = stats["wins"] + stats["draws"] + stats["losses"]
    repeat_hint = f"   Enter: {last_choice.capitalize()} again" if last_choice else ""
    cls()
    rich.print(inspect.cleandoc(f"""
        [bold red]rps game v{VERSION}[/]

        [bright_white]Wins:[/] [bold green]{stats['wins']}[/] [bright_black]|[/] [bright_white]Draws:[/] [bold yellow]{stats['draws']}[/] [bright_black]|[/] [bright_white]Losses:[/] [bold red]{stats['losses']}[/]
        [bright_white]Total:[/] [bold cyan]{total}[/]   [bright_white]Win ratio:[/] [bold cyan]{win_ratio(stats)}[/]   [bright_white]Streak:[/] [bold cyan]{stats['streak']}[/] [bright_black](best {stats['best_streak']})[/]

        [bold cyan]A:[/] [bright_white]Rock[/]
        [bold cyan]B:[/] [bright_white]Paper[/]
        [bold cyan]C:[/] [bright_white]Scissors[/]

        [bright_black]R: Reset stats   Q: Quit{repeat_hint}[/]
    """), end="\n\n")


def play_round(stats, player):
    computer = random.choice(CHOICES)
    result = get_result(player, computer)
    update_stats(stats, result)

    message = {
        "win": f"[bold green]You win![/] [bright_white]{player.capitalize()} beats {computer}.[/]",
        "draw": f"[bold yellow]Draw.[/] [bright_white]You both picked {player}.[/]",
        "loss": f"[bold red]You lose.[/] [bright_white]{computer.capitalize()} beats {player}.[/]",
    }[result]

    print()
    rich.print(inspect.cleandoc(f"""
        [bright_white]You:[/] [bold cyan]{player}[/]
        [bright_black]vs.[/]
        [bright_white]Computer:[/] [bold magenta]{computer}[/]

        {message}
    """))
    wait()


def main():
    setup_terminal()
    stats = dict(EMPTY_STATS)
    last_choice = None

    try:
        while True:
            show_menu(stats, last_choice)
            try:
                rich.print("[bold cyan]>>[/] ", end="")
                choice = input().strip().lower()
            except EOFError:
                break

            if not choice:
                if not last_choice:
                    continue
                choice = last_choice

            if choice in ("q", "quit", "exit"):
                break
            if choice in ALIASES:
                last_choice = ALIASES[choice]
                play_round(stats, last_choice)
            elif choice in ("r", "reset"):
                stats = dict(EMPTY_STATS)
            else:
                rich.print("\n[bold red]Error:[/] [yellow]That's not a valid choice.[/]")
                wait()
    except KeyboardInterrupt:
        print()

    rich.print(f"\n[bright_white]Thanks for playing! Final win ratio:[/] [bold cyan]{win_ratio(stats)}[/]")


if __name__ == "__main__":
    main()
