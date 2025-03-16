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
    Given a 13-bit mask of ranks for one suit,
    return the highest rank of any 5-consecutive run, else None.
    Handles the A-2-3-4-5 wheel => returns 5 if present.
    """
    def has_rank(r):
        return (rank_mask & (1 << (r - 2))) != 0

    for high_card in range(14, 4, -1):  # 14 down to 5
        if all(has_rank(high_card - off) for off in range(5)):
            return high_card

    # Wheel check
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
    Higher integer => better flush (packed with 4 bits per rank).
    """
    suit_buckets = [[] for _ in range(4)]
    for c in (hole_cards + board_cards):
        suit_buckets[c.suit - 1].append(c.rank)

    best_score = 0
    for ranks in suit_buckets:
        if len(ranks) >= 5:
            top5 = heapq.nlargest(5, ranks)
            score = 0
            for r in sorted(top5, reverse=True):
                score = (score << 4) | r
            if score > best_score:
                best_score = score

    return best_score if best_score > 0 else None

def get_best_straight_rank(hole_cards, board_cards):
    """
    Returns the top rank (5..14) of the best 5-card straight
    among these 7 cards, or None if no straight.
    Handles A-2-3-4-5 => returns 5.
    """
    all_cards = hole_cards + board_cards
    rank_mask = 0
    for c in all_cards:
        rank_mask |= (1 << (c.rank - 2))

    def has_rank(r):
        return (rank_mask & (1 << (r - 2))) != 0

    # Descending check
    for high_card in range(14, 4, -1):
        if all(has_rank(high_card - off) for off in range(5)):
            return high_card

    # Wheel
    if all(has_rank(r) for r in [14, 2, 3, 4, 5]):
        return 5
    return None

# -------------------------------------------------------------------------
# Enhanced helpers for lower hands (3-of-a-kind, 2-pair, pair, high card)
# that also return kicker details.
# -------------------------------------------------------------------------

def get_three_of_a_kind_tiebreak(hole_cards, board_cards):
    """
    If there's a three-of-a-kind, return (trip_rank, kicker1, kicker2),
    all in descending rank order of the kickers.
    Otherwise None.

    This does NOT exclude quads/full-house (those are checked first in holdem_eval),
    so if count>=3, we treat it as "trips" for tie-break purposes.
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    # find the highest triple
    trip = None
    for i in reversed(range(13)):
        if rank_count[i] >= 3:
            trip = i + 2
            break
    if trip is None:
        return None

    # remove those 3 from the "pool" so we can pick the top 2 kickers
    rank_count[trip - 2] -= 3

    # gather leftover ranks
    leftover = []
    for i in reversed(range(13)):
        if rank_count[i] > 0:
            # if rank_count[i] = n, that means we have n cards of rank (i+2)
            # but for kicker, each rank only matters once in this scenario, so just add the rank once per card
            # However, typically you only need the top 2 distinct leftover ranks, but let's store them all
            leftover.extend([i+2]*rank_count[i])

    leftover.sort(reverse=True)
    # we only want top 2 as the kickers
    kicker1 = leftover[0] if len(leftover) > 0 else 0
    kicker2 = leftover[1] if len(leftover) > 1 else 0

    # restore
    rank_count[trip - 2] += 3

    return (trip, kicker1, kicker2)

def get_two_pair_tiebreak(hole_cards, board_cards):
    """
    If there's at least two distinct pairs, return (top_pair, second_pair, kicker).
    Otherwise None.
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    pairs = []
    # find all ranks that have at least 2
    for i in reversed(range(13)):
        if rank_count[i] >= 2:
            pairs.append(i+2)

    if len(pairs) < 2:
        return None

    # pick the top 2 pairs
    top_pair = pairs[0]
    second_pair = pairs[1]

    # remove these pairs from rank_count so we can find the kicker
    rank_count[top_pair - 2] -= 2
    rank_count[second_pair - 2] -= 2

    # now find the best leftover rank
    kicker = 0
    for i in reversed(range(13)):
        if rank_count[i] > 0:
            kicker = i + 2
            break

    # restore
    rank_count[top_pair - 2] += 2
    rank_count[second_pair - 2] += 2

    return (top_pair, second_pair, kicker)

def get_one_pair_tiebreak(hole_cards, board_cards):
    """
    If there's at least one pair, return (pair_rank, kicker1, kicker2, kicker3).
    Otherwise None.
    """
    all_cards = hole_cards + board_cards
    rank_count = [0]*13
    for c in all_cards:
        rank_count[c.rank - 2] += 1

    pair_rank = None
    for i in reversed(range(13)):
        if rank_count[i] >= 2:
            pair_rank = i + 2
            break
    if pair_rank is None:
        return None

    # remove those 2
    rank_count[pair_rank - 2] -= 2

    # gather leftover ranks
    leftover = []
    for i in reversed(range(13)):
        while rank_count[i] > 0:
            leftover.append(i + 2)
            rank_count[i] -= 1

    # leftover now sorted descending
    # pick top 3 as kickers
    kicker1 = leftover[0] if len(leftover) > 0 else 0
    kicker2 = leftover[1] if len(leftover) > 1 else 0
    kicker3 = leftover[2] if len(leftover) > 2 else 0

    return (pair_rank, kicker1, kicker2, kicker3)

def get_high_card_tiebreak(hole_cards, board_cards):
    """
    Return the top 5 ranks in descending order as a tuple.
    If fewer than 5 cards, fill with 0, but we always have 7, so that won't happen.
    """
    all_cards = hole_cards + board_cards
    ranks = sorted([c.rank for c in all_cards], reverse=True)

    # top 5
    top5 = ranks[:5] if len(ranks) >= 5 else ranks
    # pad if needed, but typically not for 7-card
    while len(top5) < 5:
        top5.append(0)

    return tuple(top5)

# -------------------------------------------------------------------------
def holdem_eval(card, board):
    """
    Evaluate a 7-card Texas Hold'em holding (2 in 'card', 5 in 'board').
    Returns a tuple (hand_type, tiebreak_info).
      - hand_type is one of HoldemHandType
      - tiebreak_info can be an integer or a tuple of integers

    The order in which we check is from best to worst:
      Royal Flush -> Straight Flush -> Four of a Kind -> Full House ->
      Flush -> Straight -> Three of a Kind -> Two Pair -> Pair -> High Card
    Now for the lower types we incorporate kicker information as well.
    """

    if len(board) != 5 or len(card) != 2:
        raise ValueError("Invalid board or card input.")

    # 1) Royal Flush
    is_royal, suit = is_royal_flush(card, board)
    if is_royal:
        return (HoldemHandType.ROYAL_FLUSH, suit)

    # 2) Straight Flush
    sf = get_straight_flush_suit_and_rank(card, board)
    if sf is not None:
        suit_sf, rank_sf = sf
        return (HoldemHandType.STRAIGHT_FLUSH, rank_sf)

    # 3) Four of a Kind
    foak = four_of_a_kind_and_kicker(card, board)
    if foak is not None:
        quad_rank, kicker_rank = foak
        return (HoldemHandType.FOUR_OF_A_KIND, (quad_rank, kicker_rank))

    # 4) Full House
    fh = get_best_full_house(card, board)
    if fh is not None:
        triple_rank, pair_rank = fh
        return (HoldemHandType.FULL_HOUSE, (triple_rank, pair_rank))

    # 5) Flush
    flush_score = get_flush_score_fast(card, board)
    if flush_score is not None:
        # For flush vs flush, we already have a big integer comparison
        return (HoldemHandType.FLUSH, flush_score)

    # 6) Straight
    straight_rank = get_best_straight_rank(card, board)
    if straight_rank is not None:
        return (HoldemHandType.STRAIGHT, straight_rank)

    # 7) Three of a Kind (with kickers)
    three_tiebreak = get_three_of_a_kind_tiebreak(card, board)
    if three_tiebreak is not None:
        # e.g. (trip_rank, kicker1, kicker2)
        return (HoldemHandType.THREE_OF_A_KIND, three_tiebreak)

    # 8) Two Pair (with kicker)
    two_pair_tiebreak = get_two_pair_tiebreak(card, board)
    if two_pair_tiebreak is not None:
        # e.g. (top_pair, second_pair, kicker)
        return (HoldemHandType.TWO_PAIR, two_pair_tiebreak)

    # 9) One Pair (with 3 kickers)
    one_pair_tiebreak = get_one_pair_tiebreak(card, board)
    if one_pair_tiebreak is not None:
        return (HoldemHandType.PAIR, one_pair_tiebreak)

    # 10) High Card (top 5 ranks)
    high_card_tuple = get_high_card_tiebreak(card, board)
    return (HoldemHandType.HIGH_CARD, high_card_tuple)
