SUIT_INDEX = {
        "s": 1,
        "h": 2,
        "d": 3,
        "c": 4
    }

CARD_INDEX = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

class Card:
    """Inspired from pycfr card.py"""
    SUIT_STRING = {
        1: "s",
        2: "h",
        3: "d",
        4: "c"
    }
    CARD_STRING = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "T",
        11: "J",
        12: "Q",
        13: "K",
        14: "A"
    }
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return '{}{}'.format(self.CARD_STRING[self.rank], self.SUIT_STRING[self.suit])

    def __eq__(self, card):
        return card.rank == self.rank and self.suit == card.suit

    def __lt__(self, card):
        return self.rank < card.rank

    def __hash__(self):
        return hash(repr(self))
    
    def __int__(self):
        return self.rank + self.suit * 14
    
    def suit_mask(self):
        """Calculate the suit bitmask for this card."""
        return 1 << (self.suit - 1)  # Spades=1, Hearts=2, Diamonds=3, Clubs=4

    def rank_mask(self):
        """Calculate the rank bitmask for this card."""
        return 1 << (self.rank - 2)  # Rank 2 maps to bit 0, Rank 3 to bit 1, ..., Rank 14 to bit 12

def string_to_card(card_str):
    """
    Convert a string to a card, e.g. "As" -> Card(14, 1), "3h" -> Card(3, 2)
    """
    return Card(CARD_INDEX[card_str[0]], SUIT_INDEX[card_str[1]])

def string_to_cards(card_str):
    """
    Convert a string to a list of cards, e.g. "As3h" -> [Card(14, 1), Card(3, 2)]
    """
    return [string_to_card(card_str[i:i+2]) for i in range(0, len(card_str), 2)]
