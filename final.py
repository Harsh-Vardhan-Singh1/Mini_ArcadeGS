import random
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('TkAgg') # Fix for graph display
import matplotlib.pyplot as plt

# =========================
# PLAYER CLASS
# =========================
class Player:
    def __init__(self, username):
        self.username = username
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.best_score_guessing = 0
        self.best_score_hangman = 0
        self.last_played = None

    def record_win(self, score, game):
        self.games_played += 1
        self.wins += 1
        self.last_played = str(datetime.now())

        if game == "guessing":
            self.best_score_guessing = max(self.best_score_guessing, score)
        elif game == "hangman":
            self.best_score_hangman = max(self.best_score_hangman, score)

    def record_loss(self):
        self.games_played += 1
        self.losses += 1
        self.last_played = str(datetime.now())

    def display_stats(self):
        print("\n===== STATS =====")
        print("Username:", self.username)
        print("Games Played:", self.games_played)
        print("Wins:", self.wins)
        print("Losses:", self.losses)
        print("Best Guessing Score:", self.best_score_guessing)
        print("Best Hangman Score:", self.best_score_hangman)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        player = Player(data["username"])
        player.__dict__.update(data)
        return player


# =========================
# STORAGE
# =========================
BASE = "profiles"

def get_path(username):
    return os.path.join(BASE, f"{username}.json")

def save_profile(player):
    os.makedirs(BASE, exist_ok=True)
    path = get_path(player.username)

    if os.path.exists(path):
        backup_profile(path)

    with open(path, "w") as f:
        json.dump(player.to_dict(), f, indent=4)

def load_profile(username):
    path = get_path(username)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
            return Player.from_dict(data)
    except:
        print("Corrupted profile file!")
        return None

def backup_profile(file):
    try:
        with open(file, "r") as f:
            data = f.read()
        with open(file + ".bak", "w") as f:
            f.write(data)
    except:
        print("Backup failed")


# =========================
# UTILS
# =========================
def validate_int_input(msg):
    while True:
        try:
            return int(input(msg))
        except:
            print("Invalid input! Enter number.")

def validate_username(username):
    username = username.strip()
    return username if username else "guest"


# =========================
# GAMES
# =========================
def calculate_score(attempts, max_attempts):
    return max(0, (max_attempts - attempts + 1) * 10)


def start_guessing_game(player, difficulty):
    levels = {
        "easy": (1, 10, 5),
        "medium": (1, 50, 7),
        "hard": (1, 100, 10)
    }

    low, high, max_attempts = levels.get(difficulty, levels["easy"])
    number = random.randint(low, high)

    print(f"\nGuess a number between {low} and {high}")

    for attempt in range(1, max_attempts + 1):
        try:
            guess = int(input("Enter guess: "))
        except:
            print("Invalid input!")
            continue

        if guess == number:
            print("Correct!")
            score = calculate_score(attempt, max_attempts)
            player.record_win(score, "guessing")
            return
        elif guess < number:
            print("Too low")
        else:
            print("Too high")

    print("You lost! Number was:", number)
    player.record_loss()


def start_hangman_game(player):
    try:
        with open("wordlist.txt") as f:
            words = f.read().split()
    except:
        words = ["python", "arcade", "hangman"]

    word = random.choice(words)
    guessed = set()
    display = ["_"] * len(word)
    attempts = 6

    while attempts > 0 and "_" in display:
        print("\nWord:", " ".join(display))
        guess = input("Enter letter: ").lower()

        if guess in guessed:
            print("Already guessed")
            continue

        guessed.add(guess)

        if guess in word:
            for i in range(len(word)):
                if word[i] == guess:
                    display[i] = guess
        else:
            attempts -= 1
            print("Wrong! Attempts left:", attempts)

    if "_" not in display:
        print("You won!")
        player.record_win(attempts * 10, "hangman")
    else:
        print("You lost! Word was:", word)
        player.record_loss()


# =========================
# ANALYTICS + GRAPHS
# =========================
def load_all_players():
    players = []
    if not os.path.exists(BASE):
        return players

    for file in os.listdir(BASE):
        username = file.replace(".json", "")
        p = load_profile(username)
        if p:
            players.append(p)
    return players


def show_leaderboard():
    players = load_all_players()

    if not players:
        print("No data available!")
        return

    data = []
    for p in players:
        data.append({
            "username": p.username,
            "games": p.games_played,
            "wins": p.wins,
            "losses": p.losses,
            "score": p.best_score_guessing + p.best_score_hangman
        })

    df = pd.DataFrame(data)
    df["win_ratio"] = df["wins"] / df["games"]
    df = df.sort_values(by="score", ascending=False)

    print("\n===== LEADERBOARD =====")
    print(df)

    # -------- BAR CHART --------
    plt.figure()
    plt.bar(df["username"], df["score"])
    plt.title("Leaderboard (Score)")
    plt.xlabel("Players")
    plt.ylabel("Score")
    plt.show(block=True)

    # -------- PIE CHART --------
    plt.figure()
    plt.pie(df["games"], labels=df["username"], autopct="%1.1f%%")
    plt.title("Game Distribution")
    plt.show(block=True)

    # -------- LINE GRAPH --------
    plt.figure()
    plt.plot(df["username"], df["wins"])
    plt.title("Wins Trend")
    plt.xlabel("Players")
    plt.ylabel("Wins")
    plt.show(block=True)


# =========================
# MAIN
# =========================
def main():
    print("🎮 MINI ARCADE 🎮")

    username = validate_username(input("Enter username: "))
    player = load_profile(username)

    if not player:
        print("Creating new profile...")
        player = Player(username)

    while True:
        print("\n===== MENU =====")
        print("1. Guessing Game")
        print("2. Hangman")
        print("3. View Stats")
        print("4. Leaderboard + Graphs")
        print("5. Exit")

        choice = validate_int_input("Enter choice: ")

        if choice == 1:
            diff = input("Difficulty (easy/medium/hard): ").lower()
            start_guessing_game(player, diff)

        elif choice == 2:
            start_hangman_game(player)

        elif choice == 3:
            player.display_stats()

        elif choice == 4:
            show_leaderboard()

        elif choice == 5:
            save_profile(player)
            print("Progress saved. Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
