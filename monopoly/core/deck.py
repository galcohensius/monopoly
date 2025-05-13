from monopoly.cards.card import Card


class Deck:
    """ Parent for Community Chest and Chance cards """

    def __init__(self, cards):
        # List of cards
        self.cards = cards
        # Pointer to the next card to draw
        self.pointer = 0

    def draw(self):
        """ Draw one card from the deck and put it underneath.
        Actually, we don't manipulate cards, just shuffle them once
        and then move the pointer through the deck.
        """
        drawn_card = self.cards[self.pointer]
        self.pointer += 1
        if self.pointer == len(self.cards):
            self.pointer = 0
        return drawn_card

    def remove_card(self, card_to_remove):
        """ Remove a card based on its text (for GOOJF). """
        for i, card in enumerate(self.cards):
            if isinstance(card, Card) and card.text == card_to_remove.text:
                self.cards.pop(i)
                if self.pointer > i:
                    self.pointer -= 1
                elif self.pointer == len(self.cards):
                    self.pointer = 0
                return


    def add_card(self, card_to_add):
        """ Add a card to the bottom of the deck. (after playing GOOJF) """
        self.cards.append(card_to_add)
