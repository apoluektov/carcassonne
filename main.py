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
    def __init__(self, sides):
        self.sides = sides[:]

    def code(self):
        return 'r'


class CastleFragment:
    def __init__(self, sides, shield=False):
        self.sides = sides[:]
        self.shield = shield

    def code(self):
        return 'c'


class MeadowFragment:
    def __init__(self, sides):
        self.sides = sides[:]

    def code(self):
        return 'm'


class MonasteryFragment:
    def code(self):
        return 'M'


class Monastery:
    def __init__(self, cell):
        self.cell = cell
        self.adjacent = []
        self.tokens = []

    def code(self):
        return 'M'

    def score(self):
        return 1 + len(self.adjacent)

    def contains(self, xy):
        return self.cell == xy

    def is_closed(self):
        return self.score() == 9


class Road:
    def __init__(self, id_, cell, sides):
        self.id_ = id_
        self.parent_id = id_ # for find-union
        self.cells = set([cell])
        self.sides = sides[:]
        self.tokens = []

    @classmethod
    def from_fragment(cls, fragment, xy):
        sides = [(xy,s) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, cell=xy, sides=sides)

    def code(self):
        return 'r'

    def score(self):
        return len(self.cells)

    def contains(self, xy):
        return xy in self.cells

    def is_closed(self):
        return not self.sides

    # FIXME: I'm really unhappy that merging is now split between objects and Graph
    # FIXME: actually, I see it as a sign that maybe sides really belong to Graph
    def merge_into(self, dest):
        dest.cells = dest.cells.union(self.cells)
        dest.tokens += self.tokens


class Castle:
    def __init__(self, id_, cell, sides, shield=False):
        self.id_ = id_
        self.parent_id = id_
        self.cells = set([cell])
        self.sides = sides
        self.shields = int(shield)
        self.tokens = []

    @classmethod
    def from_fragment(cls, fragment, xy):
        sides = [(xy,s) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, cell=xy, sides=sides, shield=fragment.shield)

    def code(self):
        return 'c'

    def score(self):
        m = 2 if self.is_closed() else 1
        return m * (len(self.cells) + self.shields)

    def contains(self, xy):
        return xy in self.cells

    def is_closed(self):
        return not self.sides

    def merge_into(self, dest):
        dest.cells = dest.cells.union(self.cells)
        dest.tokens += self.tokens
        dest.shields += self.shields


class Meadow:
    def __init__(self, id_, cell, sides, castle_graph):
        self.id_ = id_
        self.parent_id = id_
        self.cells = set([cell])
        self.sides = sides
        self.tokens = []

        self.castle_graph = castle_graph
        self.castle_ids = set()
        for s in self.adjacent_sides():
            c = self.castle_graph.find_root_id(cell, s)
            if c:
                self.castle_ids.add(c)

    @classmethod
    def from_fragment(cls, fragment, xy, castle_graph):
        sides = [(xy,s) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, cell=xy, sides=sides, castle_graph=castle_graph)

    def adjacent_sides(self):
        # FIXME: exclude the sides that belong to this meadow itself
        # FIXME: handle meadows split into
        result = set()
        for s in self.sides:
            # FIXME: shit ugly!
            if s[1] == 'w' or s[1] == 'e':
                result.add('n')
                result.add('s')
            if s[1] == 'n' or s[1] == 's':
                result.add('e')
                result.add('w')
        return list(result)

    def code(self):
        return 'm'

    def score(self):
        result = 0
        for c in self.castle_ids:
            castle = self.castle_graph.find(*c)
            if not castle:
                raise ValueError('No castle: something went wrong')
            if castle.is_closed():
                result += 3
        return result

    def contains(self, xy):
        return xy in self.cells

    def is_closed(self):
        return False

    def merge_into(self, dest):
        dest.cells = dest.cells.union(self.cells)
        dest.tokens += self.tokens
        new_castles = set()
        for c in self.castle_ids:
            new_castles.add(self.castle_graph.find_root_id(*c))
        for c in dest.castle_ids:
            new_castles.add(self.castle_graph.find_root_id(*c))

        dest.castles = new_castles


def close(resource):
    if resource.tokens:
        d = defaultdict(int)
        for t in resource.tokens:
            d[t] += 1
        owners = sorted([(v,k) for k,v in d.items()], reverse=True)
        max_num_tokens = owners[0][0]
        for num_tokens,player in owners:
            if num_tokens == max_num_tokens:
                player.score += resource.score()
            else:
                break
    resource.tokens = []


class Card:
    # resources is the list of resources
    def __init__(self, resources):
        self.resources = resources
        self.sides = defaultdict(list)
        for i,r in enumerate(self.resources):
            c = r.code()
            if c == 'M':
                pass
            else:
                for s in r.sides:
                    self.sides[s].append(c)


    # FIXME: this is crappy code
    @staticmethod
    def rotated(card, orient):
        sides = 'wsen'
        map_sides = dict(zip(sides, rotate(sides, orient)))
        result_resources = list()
        for cr in card.resources:
            # FIXME: this becomes annoying!
            if cr.code() == 'M':
                continue

            f = None
            if cr.code() == 'r':
                new_sides = []
                for s in cr.sides:
                    new_sides.append(map_sides.get(s))
                result_resources.append(RoadFragment(new_sides))
            if cr.code() == 'c':
                new_sides = []
                for s in cr.sides:
                    new_sides.append(map_sides.get(s))
                result_resources.append(CastleFragment(new_sides, shield=cr.shield))
            if cr.code() == 'm':
                new_sides = []
                for s in cr.sides:
                    new_sides.append(map_sides.get(s))
                result_resources.append(MeadowFragment(new_sides))
        return Card(result_resources)


def rotate(l,n):
    return l[n:] + l[:n]


class Graph:
    def __init__(self):
        # ((x,y),s) -> id
        self.ids = dict()
        # id -> obj
        self.objects = dict()

    def add(self, obj):
        for s in obj.sides:
            self.ids[s] = obj.id_

        self.objects[obj.id_] = obj

        for s in obj.sides[:]:
            self.maybe_merge(*s)


    def find_root_id(self, xy, s):
        x1y1s1 = xy,s
        while True:
            x1y1s1 = self.ids.get((xy,s))
            if not x1y1s1:
                return None
            if x1y1s1 == (xy,s):
                return x1y1s1
            xy,s = x1y1s1


    def find(self, xy, s):
        root_id = self.find_root_id(xy, s)
        r = self.objects.get(root_id)
        return r


    def maybe_merge(self, xy, side):
        # FIXME: not very optimal: should we pass r0 as a param here?
        obj0 = self.find(xy,side)
        if not obj0:
            raise ValueError('No object at ' + str(xy) + ' ' + side)
        obj1 = self.find(*adjacent(xy,side))
        if not obj1:
            return

        if obj0 == obj1:
            return

        self.merge(obj0, obj1)


    def merge(self, obj, destObj):
        obj.merge_into(destObj)

        # FIXME: use optimized find-union (ranking + compacting)
        self.ids[obj.parent_id] = destObj.parent_id

        new_sides = []

        i,j = 0,0
        while i < len(obj.sides):
            s0 = obj.sides[i]
            while j < len(destObj.sides):
                s1 = destObj.sides[j]
                if s0 == adjacent(*s1):
                    del obj.sides[i]
                    del destObj.sides[j]
                    # FIXME: fucking ugly!!!
                    i -= 1
                    break
                else:
                    j += 1
            i += 1

        destObj.sides += obj.sides

        del self.objects[obj.id_]


def adjacent((x,y), side):
    # FIXME: const static data; move so that it is only initialized once
    sides = 'enws'
    adj_sides = 'wsen'
    deltas = [(1,0), (0,1), (-1,0), (0,-1)]
    d = dict(zip(sides, range(0,4)))

    idx = d[side]
    dx,dy = deltas[idx]
    return ((x+dx,y+dy), adj_sides[idx])


class Board:
    def __init__(self, game):
        self.game = game
        # (x,y) -> Card
        # FIXME: don't need it anymore
        self.cards = dict()

        # (x,y) -> Monastery
        self.monasteries = dict()

        self.roads = Graph()
        self.castles = Graph()
        self.meadows = Graph()

        self.last = None

    def add_card(self, card, xy):
        # xy already ocupied
        if self.cards.get(xy):
            return False

        x,y = xy
        sides = 'enws'

        has_neighbor = False
        for s in sides:
            (x1,y1),s1 = adjacent(xy,s)
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

        # handle adjacent monasteries
        for x1y1 in self.neighbors(xy):
            m = self.find_monastery(x1y1)
            if m:
                m.adjacent.append(xy)

        for r in card.resources:
            if r.code() == 'M':
                self.monasteries[xy] = Monastery(xy)
            elif r.code() == 'r':
                road = Road.from_fragment(r, xy)
                self.roads.add(road)
            elif r.code() == 'c':
                castle = Castle.from_fragment(r, xy)
                self.castles.add(castle)
            elif r.code() == 'm':
                meadow = Meadow.from_fragment(r, xy, self.castles)
                self.meadows.add(meadow)

        return True


    def handle_closed(self):
        roads = []
        castles = []
        monasteries = []

        for side in 'enws':
            r = self.roads.find(self.last, side)
            if r:
                roads.append(r)

            c = self.castles.find(self.last, side)
            if c:
                castles.append(c)

        cells = self.neighbors(self.last)
        cells.append(self.last)
        for c in cells:
            m = self.find_monastery(c)
            if m:
                monasteries.append(m)

        for r in roads:
            if r.is_closed():
                close(r)

        for c in castles:
            if c.is_closed():
                close(c)

        for m in monasteries:
            if m.is_closed():
                close(m)


    def find_resources(self, xy, side):
        result = []
        r = self.roads.find(xy,side)
        if r:
            result.append(r.code())
        c = self.castles.find(xy,side)
        if c:
            result.append(c.code())
        m = self.meadows.find(xy,side)
        if m:
            result.append(m.code())
        return result


#    def merge_to_neighbors(self, res):
#        sides = res.sides[:]
        

    def neighbors(self, (x, y)):
        return [(x-1,y-1), (x,y-1), (x+1,y-1), (x-1,y), (x+1,y), (x-1,y+1), (x,y+1), (x+1,y+1)]


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

    def find_monastery(self, xy):
        return self.monasteries.get(xy)


class CarcassoneTest(unittest.TestCase):

    # test roads and monasteries
    def test1(self):
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
        card0 = Card([RoadFragment(['s', 'n']), MonasteryFragment()])
        status = board.add_card(card0, (0,0))
        self.assertTrue(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        monastery = board.find_monastery((0,0))
        self.assertTrue(monastery)
        self.assertEqual(monastery.score(), 1)

        status = board.put_token(monastery, p0)
        self.assertTrue(status)

        # put another card to the same position
        # the card should not be put there
        # the score should not change
        card1 = Card([RoadFragment(['n', 's'])])
        status = board.add_card(card1, (0,0))
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        # put a card so that it is not adjacent to any card
        card = Card([RoadFragment(['n', 's'])])
        status = board.add_card(card, (2,0))
        self.assertFalse(status)

        card2 = Card([RoadFragment(['n', 's'])])
        status = board.add_card(Card.rotated(card2,1), (1,0))
        # card2 doesn't combine with card0 with this orientation
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.add_card(Card.rotated(card2,2), (1,0))
        self.assertTrue(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.find((1,0), 'e'), p0)
        # there is no road at given coords
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.find((0,0), 'n'), p0)
        # (0,0) was not the last turn
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.find((1,0), 'n'), p0)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card3 = Card([RoadFragment(['e', 'w'])])
        status = board.add_card(Card.rotated(card3,1), (2,0))
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card4 = Card([RoadFragment(['w'])])
        status = board.add_card(Card.rotated(card4, 3), (0,-1))
        self.assertTrue(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.find((0,-1), 'n'), p0)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)

        card = Card([RoadFragment(['s'])])
        status = board.add_card(card, (0,1))
        self.assertTrue(status)

        road1 = board.roads.find((0,-1), 'n')
        road2 = board.roads.find((0,0), 's')
        self.assertTrue(road1)
        self.assertEqual(road1, road2)
        self.assertEqual(road1.score(), 3)

        board.handle_closed()
        self.assertEqual(p0.score, 3)
        self.assertEqual(p1.score, 0)

        card = Card([RoadFragment(['s'])])
        board.add_card(card, (-1,1))
        status = board.put_token(board.roads.find((-1,1), 's'), p0)
        self.assertTrue(status)
        card = Card([RoadFragment(['n'])])
        board.add_card(card, (-1,-1))
        status = board.put_token(board.roads.find((-1,-1), 'n'), p1)
        self.assertTrue(status)
        # NB: merges to 2 other roads
        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (-1,0))

        board.handle_closed()
        road = board.roads.find((-1,0), 's')
        self.assertEqual(road.score(), 3)
        self.assertEqual(p0.score, 6)
        self.assertEqual(p1.score, 3)

        self.assertEqual(monastery.score(), 7)

        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (1,1))
        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (1,-1))

        board.handle_closed()
        self.assertTrue(monastery.is_closed())

        self.assertEqual(monastery.score(), 9)
        self.assertEqual(p0.score, 15)


    # add castles and meadows
    def test2(self):
        game = Game(2)
        board = Board(game)

        p0 = game.players[0]
        p1 = game.players[1]

        card = Card([CastleFragment(['e']), CastleFragment(['w']), MeadowFragment(['n', 's'])])
        status = board.add_card(card, (0,0))
        self.assertTrue(status)

        meadow1 = board.meadows.find((0,0), 'n')
        status = board.put_token(meadow1, p1)
        self.assertTrue(status)

        card = Card([CastleFragment(['n', 'w'], shield=True)])
        status = board.add_card(Card.rotated(card, 3), (-1,0))
        self.assertTrue(status)

        status = board.put_token(board.castles.find((-1,0), 'e'), p0)
        self.assertTrue(status)

        castle1 = board.castles.find((0,0), 'w')
        castle2 = board.castles.find((-1,0), 'e')
        self.assertTrue(castle1)
        self.assertEqual(castle1, castle2)
        self.assertFalse(castle1.is_closed())
        self.assertEqual(castle1.score(), 3)

        card = Card([CastleFragment(['s']), MeadowFragment(['n', 'e', 'w'])])
        status = board.add_card(card, (-1,1))
        self.assertTrue(status)
        self.assertTrue(castle1.is_closed())

        meadow2 = board.meadows.find((-1,1), 'w')
        self.assertTrue(meadow2)
        self.assertTrue(meadow1)
        self.assertNotEqual(meadow1, meadow2)
        self.assertEqual(meadow1.score(), 3)
        self.assertEqual(meadow2.score(), 3)

        status = board.put_token(meadow2, p1)
        self.assertTrue(status)

        board.handle_closed()

        self.assertEqual(p0.score, 8)
        self.assertEqual(p1.score, 0)

        card = Card([MeadowFragment(['w', 's', 'n', 'e'])])
        status = board.add_card(card, (0,1))
        self.assertTrue(status)

        meadow1 = board.meadows.find((0,0), 'n')
        meadow2 = board.meadows.find((-1,1), 'w')
        self.assertTrue(meadow2)
        self.assertTrue(meadow1)
        self.assertEqual(meadow1, meadow2)
        self.assertEqual(meadow1.score(), 3)


if __name__ == '__main__':
    unittest.main()
