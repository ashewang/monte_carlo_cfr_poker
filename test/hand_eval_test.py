import unittest

from src.card import string_to_cards
from src.hand_eval import (
    HoldemHandType,
    holdem_eval
)

class TestHoldemEval(unittest.TestCase):
    def test_holdem_eval_royal_flush(self):
        hole_cards = string_to_cards("TsAs")       # T♠ A♠
        board_cards = string_to_cards("JsQsKs2h4d")# J♠ Q♠ K♠ 2♥ 4♦
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.ROYAL_FLUSH)
        # detail = suit, i.e. 1 if spades
        self.assertEqual(detail, 1)

    def test_holdem_eval_straight_flush(self):
        # Example: hole "8s9s", board "TsJsQs2h4d" => 8♠9♠T♠J♠Q♠ => Q-high straight flush
        hole_cards = string_to_cards("8s9s")
        board_cards = string_to_cards("TsJsQs2h4d")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.STRAIGHT_FLUSH)
        # detail is the top rank of the straight flush => Q = 12
        self.assertEqual(detail, 12)

    def test_holdem_eval_four_of_kind(self):
        """Four Aces plus some kicker."""
        hole_cards = string_to_cards("AsAh")
        board_cards = string_to_cards("AdAc9s2h3d")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.FOUR_OF_A_KIND)
        # detail should be (quad_rank, kicker_rank)
        self.assertEqual(detail[0], 14)  # quad Aces
        self.assertEqual(detail[1], 9)   # kicker is 9

    def test_holdem_eval_full_house(self):
        """Full house: AAA + KK."""
        hole_cards = string_to_cards("AsAd")        # A♠ A♦
        board_cards = string_to_cards("AhKcKd7s6s")   # A♥ K♣ K♦ 7♠
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.FULL_HOUSE)
        # detail should be (triple_rank, pair_rank)
        self.assertEqual(detail, (14, 13))  # Aces full of Kings

    def test_holdem_eval_flush(self):
        """Flush example: 5♠9♠, plus 3♠A♠T♠ in board => A-high flush."""
        hole_cards = string_to_cards("5s9s")
        board_cards = string_to_cards("3sAsTs4d2h")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.FLUSH)
        # detail is an integer 'flush_score' - we won't decode it fully here,
        # but we can confirm it's not None and > 0
        self.assertIsInstance(detail, int)
        self.assertTrue(detail > 0)

    def test_holdem_eval_straight(self):
        """Straight: 7-card set that forms 5 consecutive ranks (e.g. 5..9)."""
        hole_cards = string_to_cards("5h6d")
        board_cards = string_to_cards("7s8c9dAs2h") # 5,6,7,8,9 => 9-high straight
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.STRAIGHT)
        self.assertEqual(detail, 9)

    def test_holdem_eval_three_of_a_kind_kickers(self):
        """
        Example: 9-9-9 plus K and 7 as best kickers.
        We'll verify the returned detail = (9, 13, 7).
        """
        hole_cards = string_to_cards("9h9d")
        board_cards = string_to_cards("9sKh7d5s2s")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.THREE_OF_A_KIND)
        # detail = (trip_rank, kicker1, kicker2)
        self.assertEqual(detail, (9, 13, 7))

    def test_holdem_eval_two_pair_kicker(self):
        """
        E.g. we have pairs of 7s and 5s, plus a K kicker.
        With hole: 7s7d, board: 5h5s2dKh9s
        => detail = (7, 5, 13)
        """
        hole_cards = string_to_cards("7s7d")
        board_cards = string_to_cards("5h5s2dKh9s")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.TWO_PAIR)
        self.assertEqual(detail, (7, 5, 13))

    def test_holdem_eval_pair_with_kickers(self):
        """
        Example: One pair of Queens, plus A,9,7 as kickers (in descending order).
        Hole: Qh9s, Board: QdAh7c2s5h => pair of Q, leftover = A(14), 9, 7 => detail=(12,14,9,7)
        """
        hole_cards = string_to_cards("Qh9s")        # Q=12, 9=9
        board_cards = string_to_cards("QdAh7c2s5h") # Q=12, A=14, 7=7, 2=2, 5=5
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.PAIR)
        # pair is Q=12, leftover are A=14,9=9,7=7 => (12,14,9,7)
        self.assertEqual(detail, (12, 14, 9, 7))

    def test_holdem_eval_high_card_top5(self):
        """
        High card scenario: No pairs, no flush, no straight.
        We want detail = top 5 ranks in descending order.
        Example: hole = 3s5h, board = 7hJh9sKd2h
        => top 5: K=13, J=11, 9=9, 7=7, 5=5 => (13,11,9,7,5)
        """
        hole_cards = string_to_cards("3s5h")
        board_cards = string_to_cards("7hJh9sKd2h")
        hand_type, detail = holdem_eval(hole_cards, board_cards)
        self.assertEqual(hand_type, HoldemHandType.HIGH_CARD)
        self.assertEqual(detail, (13,11,9,7,5))

if __name__ == "__main__":
    unittest.main()
