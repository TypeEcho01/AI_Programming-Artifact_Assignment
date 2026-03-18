#!/usr/bin/env python3
"""Terminal card game hub with multiple popular card games.

Games included:
1) Blackjack (player vs dealer)
2) War (player vs computer)
3) Go Fish (player vs computer)
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from collections import defaultdict
from typing import Iterable, List


SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUES = {rank: i + 2 for i, rank in enumerate(RANKS)}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()

    def draw_many(self, amount: int) -> List[Card]:
        return [self.draw() for _ in range(amount)]


# ----------------------------- Blackjack -----------------------------------
def blackjack_hand_value(cards: Iterable[Card]) -> int:
    total = 0
    aces = 0

    for card in cards:
        if card.rank in {"J", "Q", "K"}:
            total += 10
        elif card.rank == "A":
            total += 11
            aces += 1
        else:
            total += int(card.rank)

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


def play_blackjack() -> None:
    deck = Deck()
    player = deck.draw_many(2)
    dealer = deck.draw_many(2)

    print("\n=== Blackjack ===")

    while True:
        player_total = blackjack_hand_value(player)
        dealer_visible = str(dealer[0])

        print(f"Your hand: {', '.join(map(str, player))} (total: {player_total})")
        print(f"Dealer shows: {dealer_visible}")

        if player_total > 21:
            print("Bust! Dealer wins.")
            return

        move = input("Hit or stand? [h/s]: ").strip().lower()
        if move == "h":
            player.append(deck.draw())
        elif move == "s":
            break
        else:
            print("Please enter 'h' or 's'.")

    dealer_total = blackjack_hand_value(dealer)
    print(f"\nDealer hand: {', '.join(map(str, dealer))} (total: {dealer_total})")

    while dealer_total < 17:
        drawn = deck.draw()
        dealer.append(drawn)
        dealer_total = blackjack_hand_value(dealer)
        print(f"Dealer draws {drawn}. Dealer total is now {dealer_total}.")

    player_total = blackjack_hand_value(player)

    print(f"\nFinal hands:")
    print(f"You:    {', '.join(map(str, player))} (total: {player_total})")
    print(f"Dealer: {', '.join(map(str, dealer))} (total: {dealer_total})")

    if dealer_total > 21:
        print("Dealer busts. You win!")
    elif player_total > dealer_total:
        print("You win!")
    elif dealer_total > player_total:
        print("Dealer wins.")
    else:
        print("Push (tie).")


# ------------------------------- War ---------------------------------------
def compare_war_cards(player_card: Card, cpu_card: Card) -> int:
    pv = RANK_VALUES[player_card.rank]
    cv = RANK_VALUES[cpu_card.rank]
    return (pv > cv) - (pv < cv)


def play_war() -> None:
    deck = Deck()
    half = len(deck.cards) // 2
    player_stack = deck.cards[:half]
    cpu_stack = deck.cards[half:]

    rounds = 0
    print("\n=== War ===")

    while player_stack and cpu_stack:
        rounds += 1
        print(f"\nRound {rounds}")
        input("Press Enter to flip cards...")

        player_card = player_stack.pop(0)
        cpu_card = cpu_stack.pop(0)

        print(f"You played:      {player_card}")
        print(f"Computer played: {cpu_card}")

        result = compare_war_cards(player_card, cpu_card)

        if result > 0:
            player_stack.extend([player_card, cpu_card])
            print("You win the round.")
        elif result < 0:
            cpu_stack.extend([player_card, cpu_card])
            print("Computer wins the round.")
        else:
            print("War! Each side draws one hidden and one face-up card if possible.")
            war_pile = [player_card, cpu_card]

            while True:
                if len(player_stack) < 2:
                    print("You don't have enough cards for war. Computer wins the game.")
                    return
                if len(cpu_stack) < 2:
                    print("Computer doesn't have enough cards for war. You win the game!")
                    return

                war_pile.append(player_stack.pop(0))
                war_pile.append(cpu_stack.pop(0))

                player_war_card = player_stack.pop(0)
                cpu_war_card = cpu_stack.pop(0)
                war_pile.extend([player_war_card, cpu_war_card])

                print(f"War reveal -> You: {player_war_card} | Computer: {cpu_war_card}")
                war_result = compare_war_cards(player_war_card, cpu_war_card)

                if war_result > 0:
                    player_stack.extend(war_pile)
                    print("You win the war.")
                    break
                if war_result < 0:
                    cpu_stack.extend(war_pile)
                    print("Computer wins the war.")
                    break
                print("Another tie in war! Continuing...")

        print(f"Card counts -> You: {len(player_stack)} | Computer: {len(cpu_stack)}")

        if rounds >= 200:
            print("Reached round cap (200). Game ends in a draw to prevent infinite play.")
            return

    if player_stack:
        print("\nYou win the game of War!")
    else:
        print("\nComputer wins the game of War.")


# ------------------------------ Go Fish ------------------------------------
def deal_go_fish_hands(deck: Deck) -> tuple[list[Card], list[Card]]:
    return deck.draw_many(7), deck.draw_many(7)


def rank_counts(hand: Iterable[Card]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for card in hand:
        counts[card.rank] += 1
    return dict(counts)


def extract_books(hand: list[Card]) -> list[str]:
    counts = rank_counts(hand)
    books = [rank for rank, count in counts.items() if count >= 4]
    for rank in books:
        removed = 0
        for i in range(len(hand) - 1, -1, -1):
            if hand[i].rank == rank:
                hand.pop(i)
                removed += 1
                if removed == 4:
                    break
    return books


def transfer_rank_cards(source: list[Card], target: list[Card], rank: str) -> int:
    moved = [card for card in source if card.rank == rank]
    if moved:
        target.extend(moved)
        source[:] = [card for card in source if card.rank != rank]
    return len(moved)


def show_hand_summary(hand: list[Card]) -> str:
    counts = rank_counts(hand)
    parts = [f"{rank}x{counts[rank]}" for rank in RANKS if rank in counts]
    return ", ".join(parts) if parts else "(empty)"


def choose_player_rank(hand: list[Card]) -> str:
    valid = {card.rank for card in hand}
    while True:
        choice = input(f"Ask for a rank {sorted(valid)}: ").strip().upper()
        if choice in valid:
            return choice
        print("You can only ask for ranks currently in your hand.")


def choose_cpu_rank(cpu_hand: list[Card]) -> str:
    counts = rank_counts(cpu_hand)
    max_count = max(counts.values())
    candidates = [rank for rank, count in counts.items() if count == max_count]
    return random.choice(candidates)


def play_go_fish() -> None:
    deck = Deck()
    player, cpu = deal_go_fish_hands(deck)
    player_books: list[str] = []
    cpu_books: list[str] = []

    player_books.extend(extract_books(player))
    cpu_books.extend(extract_books(cpu))

    player_turn = True
    print("\n=== Go Fish ===")

    while deck.cards or player or cpu:
        if len(player_books) + len(cpu_books) == 13:
            break

        if player_turn:
            if not player and deck.cards:
                player.append(deck.draw())

            if not player:
                player_turn = False
                continue

            print(f"\nYour hand summary: {show_hand_summary(player)}")
            print(f"Books -> You: {len(player_books)} | Computer: {len(cpu_books)}")
            asked_rank = choose_player_rank(player)
            gained = transfer_rank_cards(cpu, player, asked_rank)

            if gained:
                print(f"Computer had {gained} card(s) of rank {asked_rank}. You go again.")
            else:
                print("Go fish!")
                if deck.cards:
                    drawn = deck.draw()
                    player.append(drawn)
                    print(f"You drew {drawn}.")
                    if drawn.rank == asked_rank:
                        print("Lucky draw! You go again.")
                    else:
                        player_turn = False
                else:
                    player_turn = False

            new_books = extract_books(player)
            if new_books:
                player_books.extend(new_books)
                print(f"You completed book(s): {', '.join(new_books)}")
        else:
            if not cpu and deck.cards:
                cpu.append(deck.draw())

            if not cpu:
                player_turn = True
                continue

            asked_rank = choose_cpu_rank(cpu)
            print(f"\nComputer asks: Do you have any {asked_rank}s?")
            gained = transfer_rank_cards(player, cpu, asked_rank)

            if gained:
                print(f"You gave {gained} card(s). Computer goes again.")
            else:
                print("Computer goes fishing.")
                if deck.cards:
                    drawn = deck.draw()
                    cpu.append(drawn)
                    if drawn.rank == asked_rank:
                        print("Computer drew what it asked for and goes again.")
                    else:
                        player_turn = True
                else:
                    player_turn = True

            new_books = extract_books(cpu)
            if new_books:
                cpu_books.extend(new_books)
                print(f"Computer completed book(s): {', '.join(new_books)}")

    print("\nFinal score (books):")
    print(f"You: {len(player_books)} ({', '.join(player_books) if player_books else 'none'})")
    print(f"Computer: {len(cpu_books)} ({', '.join(cpu_books) if cpu_books else 'none'})")

    if len(player_books) > len(cpu_books):
        print("You win Go Fish!")
    elif len(cpu_books) > len(player_books):
        print("Computer wins Go Fish.")
    else:
        print("Go Fish ends in a tie.")


# ------------------------------ Main Menu ----------------------------------
def show_menu() -> None:
    print("\n=== Card Game Hub ===")
    print("1) Blackjack")
    print("2) War")
    print("3) Go Fish")
    print("4) Quit")


def main() -> None:
    random.seed()
    print("Welcome to Card Game Hub!")

    while True:
        show_menu()
        choice = input("Choose a game [1-4]: ").strip()

        if choice == "1":
            play_blackjack()
        elif choice == "2":
            play_war()
        elif choice == "3":
            play_go_fish()
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
