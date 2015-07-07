import unittest
from collections import defaultdict

class Player:
    def __init__(self):
        self.score = 0


class Game:
    def __init__(self, num_of_players):
        self.players = [Player() for i in range(num_of_players)]

# represents road fragment on a card
class RoadFragment:
    # begin, end - one letter 'n' 'e' 's' 'w'
    # if end is None, that means that roads ends here
    def __init__(self, begin, end=None):
        self.begin = begin
        self.end = end

    def code(self):
        return 'r'


class Card:
    # resources is the list of resources
    def __init__(self, resources):
        self.resources = resources
        self.sides = defaultdict(list)
        for i,r in enumerate(self.resources):
            c = r.code()
            if c == 'r':
                self.sides[r.begin].append('r')
                if r.end:
                    self.sides[r.end].append('r')
            elif c:
                raise ValueError('Only roads are supported at the moment')

    # FIXME: this is crappy code
    @staticmethod
    def rotated(card, orient):
        sides = 'wsen'
        map_sides = dict(zip(sides, rotate(sides, orient)))
        result_resources = list()
        for cr in card.resources:
            # FIXME: this becomes annoying!
            if cr.code() == 'r':
                begin = map_sides.get(cr.begin)
                end = map_sides.get(cr.end)
            result_resources.append(RoadFragment(begin,end))
        return Card(result_resources)
        
        

def rotate(l,n):
    return l[n:] + l[:n]

class Board:
    def __init__(self, game):
        self.game = game
        # (x,y) -> Card
        self.cards = dict()

    def add_card(self, card, xy):
        # xy already ocupied
        if self.cards.get(xy):
            return False

        x,y = xy
        neighbor_coords = [(x+1, y), (x, y+1), (x-1, y), (x, y-1)]
        neighbor_adjacent_sides = "wsen"
        adjacent_sides = "enws"

        # FIXME: long!
        for ((x1,y1),s0,s1) in zip(neighbor_coords, adjacent_sides, neighbor_adjacent_sides):
            neighbor = self.cards.get((x1,y1))
            if neighbor:
                side = card.sides[s0]
                neighbor_side = neighbor.sides[s1]

                if not self.do_sides_match(side, neighbor_side):
                    return False
                
        self.cards[xy] = card

        return True

    def do_sides_match(self, side1, side2):
        # FIXME: at least at the moment
        return sorted(side1) == sorted(side2)


class CarcassoneTest(unittest.TestCase):

    def testFirst(self):
        # TODO: keyword param
        # 2 is num of players
        game = Game(2)
        # FIXME: should create board with init piece at center
        board = Board(game)
        # FIXME: what card?
        # FIXME: also, should get a card from the suffled deck

        # put a card and don't claim any resource
        # the card should be put
        # the score should not change
        card0 = Card([RoadFragment('n', 's')])
        status = board.add_card(card0, (0,0))
        self.assertTrue(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        # put another card to the same position
        # the card should not be put there
        # the score should not change
        card1 = Card([RoadFragment('n', 's')])
        status = board.add_card(card1, (0,0))
        self.assertFalse(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        card2 = Card([RoadFragment('n', 's')])
        status = board.add_card(Card.rotated(card2,1), (1,0))
        # card2 doesn't combine with card0 with this orientation
        self.assertFalse(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        # let's try
        status = board.add_card(Card.rotated(card2,2), (1,0))
        self.assertTrue(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        card3 = Card([RoadFragment('e', 'w')])
        status = board.add_card(Card.rotated(card3,1), (2,0))
        self.assertTrue(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        card4 = Card([RoadFragment('e', 'w')])
        status = board.add_card(Card.rotated(card4, 3), (0,-1))
        self.assertTrue(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)
                     

if __name__ == '__main__':
    unittest.main()
