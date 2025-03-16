from card import string_to_cards
from enum import IntEnum
import heapq

class HoldemHandType(IntEnum): 
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9

def is_royal_flush(cards, board):
    """
    Check if the given 2 cards + board is a royal flush.
    Returns (True, suit) if found, otherwise (False, None).
    suit ∈ {1=spades,2=hearts,3=diamonds,4=clubs}
    """
    all_cards = cards + board
    suits_bitmask = [0, 0, 0, 0]  # for spade, heart, diamond, club

    for card in all_cards:
        suits_bitmask[card.suit - 1] |= card.rank_mask()

    # We need bits for T,J,Q,K,A => ranks 10..14 => bits 8..12
    ROYAL_MASK = ((1 << (10 - 2)) | (1 << (11 - 2)) | 
                  (1 << (12 - 2)) | (1 << (13 - 2)) | (1 << (14 - 2)))
    # Check each suit
    for i, mask in enumerate(suits_bitmask):
        if (mask & ROYAL_MASK) == ROYAL_MASK:
            return True, i+1
    return False, None

def get_straight_flush_suit_and_rank(hole_cards, board_cards):
    """
    Returns (suit, top_rank) if there's a straight flush,
    or None if not found.

    suit ∈ {1=spades,2=hearts,3=diamonds,4=clubs}
    top_rank ∈ [5..14], with 5 = 5-high "wheel".
    """
    all_cards = hole_cards + board_cards
    suits_bitmask = [0, 0, 0, 0]

    for card in all_cards:
        rank_bit = 1 << (card.rank - 2)
        suits_bitmask[card.suit - 1] |= rank_bit

    best_suit = None
    best_top_rank = 0

    for suit_index, rank_mask in enumerate(suits_bitmask):
        top_rank = _get_best_straight_in_mask(rank_mask)
        if top_rank is not None and top_rank > best_top_rank:
            best_top_rank = top_rank
            best_suit = suit_index + 1

    return (best_suit, best_top_rank) if best_suit else None

def _get_best_straight_in_mask(rank_mask):
    """
    Given a 13-bit mask of ranks for a single suit,
    return the highest rank of any 5-consecutive run, else None.
    Handles wheel (A-2-3-4-5) => returns 5 if present.
    """
    def has_rank(r):
        return (rank_mask & (1 << (r - 2))) != 0

    # Check normal straights from Ace(14) down to 5
    for high_card in range(14, 4, -1):
        if all(has_rank(high_card - off) for off in range(5)):
            return high_card

    # Wheel check: A(14),2,3,4,5
    if all(has_rank(r) for r in [14, 2, 3, 4, 5]):
        return 5
    return None

def four_of_a_kind_and_kicker(hole_cards, board_cards):
    """
    Returns (quad_rank, kicker_rank) if 4-of-a-kind is found,
    otherwise None.
    quad_rank, kicker_rank ∈ [2..14].
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13

    for card in all_cards:
        rank_count[card.rank - 2] += 1

    quad_rank = None
    for i, c in enumerate(rank_count):
        if c >= 4:
            quad_rank = i + 2
            break
    if quad_rank is None:
        return None

    # find best kicker (highest other rank)
    kicker = None
    for i in reversed(range(13)):
        if i+2 != quad_rank and rank_count[i] > 0:
            kicker = i + 2
            break
    return (quad_rank, kicker)

def get_best_full_house(hole_cards, board_cards):
    """
    Returns (triple_rank, pair_rank) for the best full house
    among the 7 cards, or None if none.

    triple_rank, pair_rank ∈ [2..14], 14=Ace,
    "best" means highest triple, then highest pair.
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    triple_candidates = []
    pair_candidates = []
    for i, c in enumerate(rank_count):
        if c >= 3:
            triple_candidates.append(i)
        if c >= 2:
            pair_candidates.append(i)

    triple_candidates.sort(reverse=True)
    pair_candidates.sort(reverse=True)

    for t_i in triple_candidates:
        for p_i in pair_candidates:
            if p_i != t_i:
                return (t_i+2, p_i+2)
    return None

def get_flush_score_fast(hole_cards, board_cards):
    """
    Returns an integer 'score' for the best 5-card flush among the 7 cards.
    If no flush exists, returns None.
    Higher integer => better flush.
    """
    suit_buckets = [[] for _ in range(4)]
    for c in (hole_cards + board_cards):
        suit_buckets[c.suit - 1].append(c.rank)

    best_score = 0
    for ranks in suit_buckets:
        if len(ranks) >= 5:
            top5 = heapq.nlargest(5, ranks)
            score = 0
            # pack ranks in descending order into an integer
            for r in sorted(top5, reverse=True):
                score = (score << 4) | r
            if score > best_score:
                best_score = score

    return best_score if best_score > 0 else None

# -------------------------------------------------------------------------
# ADDITIONAL HELPERS FOR STRAIGHT, TRIPS, TWO PAIR, HIGH CARD
# -------------------------------------------------------------------------

def get_best_straight_rank(hole_cards, board_cards):
    """
    Returns the top rank (in [5..14]) of the best 5-card straight
    among these 7 cards, or None if no straight.
    Handles the A-2-3-4-5 wheel (returns 5 in that case).
    """
    all_cards = hole_cards + board_cards
    # Build a bitmask of *all* ranks present (ignoring suit).
    rank_mask = 0
    for c in all_cards:
        rank_mask |= (1 << (c.rank - 2))

    def has_rank(r):
        return (rank_mask & (1 << (r - 2))) != 0

    # Check from Ace(14) down to 5
    for high_card in range(14, 4, -1):
        if all(has_rank(high_card - off) for off in range(5)):
            return high_card

    # Wheel check
    if all(has_rank(r) for r in [14, 2, 3, 4, 5]):
        return 5

    return None

def get_three_of_a_kind_rank(hole_cards, board_cards):
    """
    Returns the highest rank for which count >= 3,
    or None if no three-of-a-kind exists.
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    # check from Ace down to 2
    for i in reversed(range(13)):
        if rank_count[i] >= 3:
            return i + 2
    return None

def get_two_pair_ranks(hole_cards, board_cards):
    """
    If the 7 cards contain at least two distinct ranks with count>=2,
    return a tuple (top_pair_rank, second_pair_rank).
    Otherwise None.
    Example: If you have ranks A,A,K,K,9,... => returns (14,13).
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    pairs = []
    # Check from Ace=12 down to 2=0
    for i in reversed(range(13)):
        if rank_count[i] >= 2:
            pairs.append(i+2)
        if len(pairs) == 2:
            # Found at least two pairs
            return (pairs[0], pairs[1])
    return None

def get_high_card_rank(hole_cards, board_cards):
    """
    Returns the single highest rank among the 7 cards (2..14).
    """
    all_cards = hole_cards + board_cards
    max_rank = 0
    for c in all_cards:
        if c.rank > max_rank:
            max_rank = c.rank
    return max_rank

# -------------------------------------------------------------------------
def holdem_eval(card, board):
    """
    Evaluate a 7-card Texas Hold'em holding (2 in 'card', 5 in 'board').
    Returns a tuple (hand_type, tiebreak_info).
    'hand_type' is one of HoldemHandType enum.
    'tiebreak_info' is an int or tuple providing more detail (e.g. rank).
    """

    if len(board) != 5 or len(card) != 2:
        raise ValueError("Invalid board or card input.")

    # 1) Royal Flush?
    is_royal, suit = is_royal_flush(card, board)
    if is_royal:
        # Return (ROYAL_FLUSH, suit)
        return (HoldemHandType.ROYAL_FLUSH, suit)

    # 2) Straight Flush?
    sf = get_straight_flush_suit_and_rank(card, board)
    if sf is not None:
        suit_sf, rank_sf = sf
        return (HoldemHandType.STRAIGHT_FLUSH, rank_sf)

    # 3) Four of a Kind?
    foak = four_of_a_kind_and_kicker(card, board)
    if foak is not None:
        quad_rank, kicker_rank = foak
        return (HoldemHandType.FOUR_OF_A_KIND, (quad_rank, kicker_rank))

    # 4) Full House?
    fh = get_best_full_house(card, board)
    if fh is not None:
        triple_rank, pair_rank = fh
        return (HoldemHandType.FULL_HOUSE, (triple_rank, pair_rank))

    # 5) Flush? (Any 5+ in same suit)
    flush_score = get_flush_score_fast(card, board)
    if flush_score is not None:
        # Return flush score so we can compare flush v flush
        return (HoldemHandType.FLUSH, flush_score)

    # 6) Straight?
    straight_rank = get_best_straight_rank(card, board)
    if straight_rank is not None:
        return (HoldemHandType.STRAIGHT, straight_rank)

    # 7) Three of a Kind?
    trips_rank = get_three_of_a_kind_rank(card, board)
    if trips_rank is not None:
        return (HoldemHandType.THREE_OF_A_KIND, trips_rank)

    # 8) Two Pair?
    tp = get_two_pair_ranks(card, board)
    if tp is not None:
        # tp is (top_pair_rank, second_pair_rank)
        return (HoldemHandType.TWO_PAIR, tp)

    # 9) Pair?
    # We didn't implement a direct function above, but let's do it inline quickly:
    all_cards = card + board
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    pair_rank = None
    # check highest pair
    for i in reversed(range(13)):
        if rank_count[i] >= 2:
            pair_rank = i+2
            break
    if pair_rank is not None:
        return (HoldemHandType.PAIR, pair_rank)

    # 10) High Card
    high_card = get_high_card_rank(card, board)
    return (HoldemHandType.HIGH_CARD, high_card)

