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

    def __repr__(self):
        return '<road-fragment: ' + self.begin + '->' + self.end + ' >'


class Road:
    def __init__(self, id_, cell, begin, end):
        self.id_ = id_
        self.cells = set([cell])
        self.begin = begin
        self.end = end
        self.tokens = []

    def code(self):
        return 'r'

    def contains(self, xy):
        return xy in self.cells


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
        # FIXME: don't need it anymore
        self.cards = dict()

        # ((x,y),s) -> Road
        self.roads = dict()
        self.last = None

    def add_card(self, card, xy):
        # xy already ocupied
        if self.cards.get(xy):
            return False

        x,y = xy
        sides = 'enws'

        has_neighbor = False
        for s in sides:
            (x1,y1),s1 = self.adjacent(xy,s)
            neighbor = self.cards.get((x1,y1))
            if neighbor:
                has_neighbor = True
                side = card.sides[s]
                adj_side = self.find_resources((x1,y1),s1)

                if not self.do_sides_match(side, adj_side):
                    return False

        if not has_neighbor and self.cards:
            return False

        self.cards[xy] = card
        self.last = xy

        for r in card.resources:
            if r.code() == 'r':
                road = Road(id_=(xy,r.begin), cell=xy, begin=r.begin, end=r.end)
                self.roads[(xy,r.begin)] = road

                if r.end:
                    self.roads[(xy, r.end)] = road

        return True


    def find_resources(self, xy, side):
        result = []
        r = self.roads.get((xy,side))
        if r:
            result.append(r.code())
        return result


    def adjacent(self, (x,y), side):
        # FIXME: const static data; move so that it is only initialized once
        sides = 'enws'
        adj_sides = 'wsen'
        deltas = [(1,0), (0,1), (-1,0), (0,-1)]        
        d = dict(zip(sides, range(0,4)))

        idx = d[side]
        dx,dy = deltas[idx]
        return ((x+dx,y+dy), adj_sides[idx])


    def put_token(self, resource, player):
        if not resource:
            return False
        if not resource.contains(self.last):
            return False
        if resource.tokens:
            return False
        resource.tokens.append(player)
        return True

    def do_sides_match(self, side1, side2):
        # FIXME: at least at the moment
        return sorted(side1) == sorted(side2)

    def find_road(self, xy, s):
        r = self.roads.get((xy,s))
        return r


class CarcassoneTest(unittest.TestCase):

    def testFirst(self):
        # TODO: keyword param
        # 2 is num of players
        game = Game(2)
        # FIXME: should create board with init piece at center
        board = Board(game)
        # FIXME: also, should get a card from the suffled deck

        p0 = game.players[0]
        p1 = game.players[1]

        # put a card and don't claim any resource
        # the card should be put
        # the score should not change
        card0 = Card([RoadFragment('n', 's')])
        status = board.add_card(card0, (0,0))
        self.assertTrue(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        # put another card to the same position
        # the card should not be put there
        # the score should not change
        card1 = Card([RoadFragment('n', 's')])
        status = board.add_card(card1, (0,0))
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        # put a card so that it is not adjacent to any card
        card = Card([RoadFragment('n', 's')])
        status = board.add_card(card, (2,0))
        self.assertFalse(status)

        card2 = Card([RoadFragment('n', 's')])
        status = board.add_card(Card.rotated(card2,1), (1,0))
        # card2 doesn't combine with card0 with this orientation
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.add_card(Card.rotated(card2,2), (1,0))
        self.assertTrue(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.find_road((1,0), 'e'), p0)
        # there is no road at given coords
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.find_road((0,0), 'n'), p0)
        # (0,0) was not the last turn
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.find_road((1,0), 'n'), p0)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card3 = Card([RoadFragment('e', 'w')])
        status = board.add_card(Card.rotated(card3,1), (2,0))
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card4 = Card([RoadFragment('e', 'w')])
        status = board.add_card(Card.rotated(card4, 3), (0,-1))
        self.assertTrue(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.find_road((0,-1), 'n'), p1)
        # road already claimed by p0
#        self.assertFalse(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)


if __name__ == '__main__':
    unittest.main()
