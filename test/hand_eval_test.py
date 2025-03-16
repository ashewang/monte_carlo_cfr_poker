import unittest

from src.card import Card, string_to_cards
from src.hand_eval import (
    HoldemHandType,
    holdem_eval
)

class TestHoldemEval(unittest.TestCase):
    def test_holdem_eval_royal_flush(self):
        hole_cards = string_to_cards("TsAs")
        board_cards = string_to_cards("JsQsKs2h4d")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.ROYAL_FLUSH)
        self.assertEqual(detail, 1)

    def test_holdem_eval_high_card(self):
        hole_cards = string_to_cards("3s5h")
        board_cards = string_to_cards("7hJh9sKd2h")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.HIGH_CARD)
        self.assertEqual(detail, 13)  # highest rank is K(13)

    def test_holdem_eval_two_pair(self):
        hole_cards = string_to_cards("7s7d")
        board_cards = string_to_cards("5h5s2dKh9s")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.TWO_PAIR)
        self.assertEqual(detail, (7, 5))

    def test_holdem_eval_four_of_kind(self):
        """Four Aces plus some kicker."""
        hole_cards = string_to_cards("AsAh")
        board_cards = string_to_cards("AdAc9s2h3d")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.FOUR_OF_A_KIND)
        self.assertEqual(detail[0], 14)  # quad Aces
        self.assertEqual(detail[1], 9)   # kicker is 9

if __name__ == "__main__":
    unittest.main()
