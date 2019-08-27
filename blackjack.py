#!/usr/bin/env python
import typing
import pprint
import random


class Dealer(object):
    def __init__(self):
        self.deck = self.make_deck()
        self.hand = []

    def make_deck(self):
        suits = {"Spades", "Clubs", "Hearts", "Diamonds"}

        faces = {"King", "Queen", "Jack", "Ace"}
        
        deck = []

        for suit in suits:
            for face in faces:
                deck.append("%s of %s" % (face, suit))

            for i in range(8):
                deck.append("%i of %s" % (i+2, suit))

        return deck

    def deal(self, recipient):
        if not self.deck:
            print("No more cards left. Game Over.")
            raise SystemExit
        random.shuffle(self.deck)
        card = self.deck.pop()
        if recipient == self:
            print("The dealer was dealt a %s." % card)
        recipient.hand.append(card)

    def __repr__(self):
        return "Dealer with %i cards left in the deck." % len(self.deck)

class Player(object):
    def __init__(self, balance=50.0):
        self.hand    = []
        self.balance = balance
        self.stake   = 0.00

    def update_stake(self):
        print("Updating the stakes for %s." % self)
        success = False
        while success == False:
            try:
                new_stake = float(input("New stake: "))
                if new_stake > self.balance:
                    raise Exception
            except Exception:
                print("Please enter a numeric value lower than %.2f." % self.balance)
            success = True
        self.balance -= new_stake
        self.stake = new_stake 
        print("Updated the stakes for %s." % self)

    def to_currency(self, value: typing.Union[float, int]):
        return "£%s" % format(value, ",")

    def __repr__(self):
        return "Player at %s with %i cards. Balance: %s. Stake: %s" % \
            (hex(id(self)), len(self.hand), self.to_currency(self.balance),
            self.to_currency(self.stake))

class BlackjackEnv(object):
    def __init__(self, dealer, *players):
        self.dealer  = dealer
        self.players = list(players)
        self.playing = False

    def lookup_card_value(self, card: str) -> int:
        word = card.split()[0].lower()
        if word.isdigit():
            return int(word)
        if word == "ace":
            return 11
        return 10

    def evaluate_hand(self, entity) -> int:
        return sum([self.lookup_card_value(card) for card in entity.hand])

    def print_hand(self, entity):
        print("\n%s\n" % pprint.pformat(entity.hand))

    @property
    def stats(self):
        output = str(self.dealer) + "\n"
        for player in self.players:
            output += str(player) + "\n"

    def step(self):
        dealer_value = self.evaluate_hand(self.dealer)

        while dealer_value < 17 and dealer_value < 22:
            self.dealer.deal(self.dealer)
            dealer_value = self.evaluate_hand(self.dealer)
            if dealer_value > 21:
                for player in self.players:
                    player.balance += player.stake * 2
                    player.stake   = 0
                print("The dealer went bust. All hands remunerated.")
                return True

        for player in self.players.copy():

            print("%s has the following hand:" % player)

            self.print_hand(player)

            dealing = True
            while dealing:
                while 1:
                    player_input = input("Would %s like to [S]tand/[S]tick, [H]it/[T]wist or [N]either? > " % player).lower()
                    if len(player_input) and player_input[0] in {"s", "h", "t", "n"}:
                        break
                        
                if player_input[0] == "s":
                    dealing = False

                elif player_input[0] in {"h", "t"}:
                    self.dealer.deal(player)
                    self.print_hand(player)

            player_value = self.evaluate_hand(player)

            if player_value == 21:
                player.balance = player.balance * 2.5
                print("%s got a natural Blackjack! Their balance has been increased by 2.5x." % player)
                continue
           
        for player in self.players.copy():
            player_value = self.evaluate_hand(player)
            if player_value > dealer_value and player_value < 22:
                print("%s fared better than the dealer and is being remunerated." % player)
                player.balance += player.stake * 2
                player.stake = 0
            else:
                print("%s fared worse than the dealer (Player:%i, Dealer: %i) and is losing their wager." % \
                    (player, player_value, dealer_value))
                player.stake = 0
                if not player.balance:
                    self.players.remove(player)
                    if not self.players:
                        return False
        return True 

    def loop(self):
        # Signal that play has started, set the stakes, deal initial hands and
        # enter gameplay loop

        self.playing = True

        for player in self.players:
            player.update_stake()

        for i in range(2):
            for player in self.players:
                self.dealer.deal(player)

        self.dealer.deal(self.dealer)

        while self.playing:
            self.playing = self.step()
            for player in self.players:
                player.hand = []
                player.update_stake()
            for i in range(2):
                for player in self.players:
                    self.dealer.deal(player)
            self.dealer.hand = []
            self.dealer.deal(self.dealer)

        print("Game Over.")

if __name__ == "__main__":
    dealer = Dealer()
    player = Player()
    env    = BlackjackEnv(dealer, player)

    try:
        env.loop()
    
    except KeyboardInterrupt:
        print(env.stats)
        print("Bye.")


