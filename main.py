import unittest
from collections import defaultdict

class Player:
    def __init__(self, token_count):
        self.score = 0
        self.token_count = token_count
        self.claimed_resource_ids = []


class Game:
    def __init__(self, players, board):
        self.players = players
        self.board = board

    def find_claimed_resources(self):
        result = set()
        for p in self.players:
            for res_id in p.claimed_resource_ids:
                res = self.board.find_resource(res_id)
                result.add(res)
        return list(result)

    # FIXME: name is crap
    def find_largest_owners(self, res):
        result = []
        if res.tokens:
            d = defaultdict(int)
            for t in res.tokens:
                d[t] += 1
            owners = sorted([(v,k) for k,v in d.items()], reverse=True)
            max_num_tokens = owners[0][0]
            for num_tokens,player in owners:
                if num_tokens == max_num_tokens:
                    result.append(player)
                else:
                    break
        return result


    def on_turn_end(self):
        resources = [r for r in self.find_claimed_resources() if r.is_closed()]
        for res in resources:
            owners = self.find_largest_owners(res)
            for p in owners:
                p.score += res.score()
            for p in res.tokens:
                p.token_count += 1

            self._hack_unclaim_resource(res)


    def on_game_end(self):
        resources = self.find_claimed_resources()
        for res in resources:
            owners = self.find_largest_owners(res)
            for p in owners:
                p.score += res.score()
            for p in res.tokens:
                p.token_count += 1

            # FIXME: brute force: using it here leads to O(R^2) behavior (where R is number of claimed resources)
            # FIXME: fortunately R is quite small for Carcassonne
            self._hack_unclaim_resource(res)


    def _hack_unclaim_resource(self, res):
        # FIXME: HACK: 'when in doubt, use brute force' (c)
        for p in self.players:
            for res_id in p.claimed_resource_ids:
                res2 = self.board.find_resource(res_id)
                if res2 == res:
                    p.claimed_resource_ids.remove(res_id)


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
    def __init__(self):
        self.sides = []

    def code(self):
        return 'M'


class Monastery:
    def __init__(self, xy):
        self.id_ = xy
        self.cell = xy
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
    def __init__(self, id_, xy, sides):
        self.id_ = id_
        self.parent_id = id_ # for find-union
        self.cells = set([xy])
        self.sides = sides[:]
        self.tokens = []

    @classmethod
    def from_fragment(cls, fragment, xy, orient):
        sides = [(xy, rotate_ccw(s, orient)) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, xy=xy, sides=sides)

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
    def __init__(self, id_, xy, sides, shield=False):
        self.id_ = id_
        self.parent_id = id_
        self.cells = set([xy])
        self.sides = sides
        self.shields = int(shield)
        self.tokens = []

    @classmethod
    def from_fragment(cls, fragment, xy, orient):
        sides = [(xy, rotate_ccw(s, orient)) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, xy=xy, sides=sides, shield=fragment.shield)

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
    def __init__(self, id_, xy, sides, castle_graph):
        self.id_ = id_
        self.parent_id = id_
        self.cells = set([xy])
        self.sides = sides
        self.tokens = []

        self.castle_graph = castle_graph
        self.castle_ids = set()
        for s in self.adjacent_sides():
            c = self.castle_graph.find_root_id((xy, s))
            if c:
                self.castle_ids.add(c)

    @classmethod
    def from_fragment(cls, fragment, xy, orient, castle_graph):
        sides = [(xy, rotate_ccw(s, orient)) for s in fragment.sides]
        id_ = sides[0]
        return cls(id_=id_, xy=xy, sides=sides, castle_graph=castle_graph)

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
            castle = self.castle_graph.get(c)
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
            new_castles.add(self.castle_graph.find_root_id(c))
        for c in dest.castle_ids:
            new_castles.add(self.castle_graph.find_root_id(c))

        dest.castles = new_castles


class Card:
    # resources is the list of resources
    def __init__(self, resources):
        self.resources = resources

    def get_borders(self, orient):
        result = defaultdict(list)
        for r in self.resources:
            c = r.code()
            for s in r.sides:
                result[rotate_ccw(s, orient)].append(c)
        return result


g_dirs_ccw = dict(zip('wsen', 'senw'))

# counterclockwise
def rotate_ccw(direction, n):
    for i in range(n):
        direction = g_dirs_ccw[direction]
    return direction


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
            self.maybe_merge(s)


    def find_root_id(self, id_):
        while True:
            parent_id = self.ids.get(id_)
            if not parent_id:
                return None
            if parent_id == id_:
                return parent_id
            id_ = parent_id


    def get(self, id_):
        root_id = self.find_root_id(id_)
        r = self.objects.get(root_id)
        return r


    def maybe_merge(self, id_):
        xy,side = id_
        obj0 = self.get(id_)
        if not obj0:
            raise ValueError('No object at ' + str(xy) + ' ' + side)
        obj1 = self.get(adjacent(xy,side))
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
    def __init__(self):
        # (x,y) -> (dir -> card side)
        self.cell_borders = dict()

        # (x,y) -> Monastery
        self.monasteries = dict()

        self.roads = Graph()
        self.castles = Graph()
        self.meadows = Graph()

        self.last = None


    def can_put_card(self, card, xy, orient):
        if self.cell_borders.get(xy):
            return False

        sides = 'enws'
        card_borders = card.get_borders(orient)

        has_neighbor = False
        for s in sides:
            x1y1,s1 = adjacent(xy,s)
            neighbor_borders = self.cell_borders.get(x1y1)
            if neighbor_borders:
                has_neighbor = True
                if not self.do_sides_match(card_borders[s], neighbor_borders[s1]):
                    return False

        if not has_neighbor and self.cell_borders:
            return False

        return True


    def add_card(self, card, xy, orient=0):
        if not self.can_put_card(card, xy, orient):
            return False

        self.cell_borders[xy] = card.get_borders(orient)
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
                road = Road.from_fragment(r, xy, orient)
                self.roads.add(road)
            elif r.code() == 'c':
                castle = Castle.from_fragment(r, xy, orient)
                self.castles.add(castle)
            elif r.code() == 'm':
                meadow = Meadow.from_fragment(r, xy, orient, self.castles)
                self.meadows.add(meadow)

        return True


    def find_resource(self, res_id):
        code,id_ = res_id
        objs = {'r': self.roads,
                'c': self.castles,
                'm': self.meadows,
                'M': self.monasteries}
        return objs[code].get(id_)


    def neighbors(self, (x, y)):
        return [(x-1,y-1), (x,y-1), (x+1,y-1), (x-1,y), (x+1,y), (x-1,y+1), (x,y+1), (x+1,y+1)]

    # TODO: return status -- why the token could not be put
    def put_token(self, resource, player):
        if player.token_count == 0:
            return False
        if not resource:
            return False
        if not resource.contains(self.last):
            return False
        if resource.tokens:
            return False

        resource.tokens.append(player)
        player.claimed_resource_ids.append((resource.code(), resource.id_))
        player.token_count -= 1
        return True

    def do_sides_match(self, side1, side2):
        return side1 == side2[::-1]

    def find_monastery(self, xy):
        return self.monasteries.get(xy)


class CarcassoneTest(unittest.TestCase):

    # test roads and monasteries
    def test1(self):
        p0 = Player(token_count=5)
        p1 = Player(token_count=5)

        board = Board()
        game = Game([p0, p1], board)

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
        status = board.add_card(card2, (1,0), 1)
        # card2 doesn't combine with card0 with this orientation
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.add_card(card2, (1,0), 2)
        self.assertTrue(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.get(((1,0), 'e')), p0)
        # there is no road at given coords
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.get(((0,0), 'n')), p0)
        # (0,0) was not the last turn
        self.assertFalse(status)
        self.assertEqual(p0.score, 0)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.get(((1,0), 'n')), p0)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card3 = Card([RoadFragment(['e', 'w'])])
        status = board.add_card(card3, (2,0), 1)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 1)
        self.assertEqual(p1.score, 0)

        card4 = Card([RoadFragment(['w'])])
        status = board.add_card(card4, (0,-1), 3)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)

        status = board.put_token(board.roads.get(((0,-1), 'n')), p0)
        self.assertTrue(status)
#        self.assertEqual(p0.score, 2)
        self.assertEqual(p1.score, 0)

        card = Card([RoadFragment(['s'])])
        status = board.add_card(card, (0,1))
        self.assertTrue(status)

        road1 = board.roads.get(((0,-1), 'n'))
        road2 = board.roads.get(((0,0), 's'))
        self.assertTrue(road1)
        self.assertEqual(road1, road2)
        self.assertEqual(road1.score(), 3)

        game.on_turn_end()
        self.assertEqual(p0.score, 3)
        self.assertEqual(p1.score, 0)

        card = Card([RoadFragment(['s'])])
        board.add_card(card, (-1,1))
        status = board.put_token(board.roads.get(((-1,1), 's')), p0)
        self.assertTrue(status)
        card = Card([RoadFragment(['n'])])
        board.add_card(card, (-1,-1))
        status = board.put_token(board.roads.get(((-1,-1), 'n')), p1)
        self.assertTrue(status)
        # NB: merges to 2 other roads
        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (-1,0))

        game.on_turn_end()
        road = board.roads.get(((-1,0), 's'))
        self.assertEqual(road.score(), 3)
        self.assertEqual(p0.score, 6)
        self.assertEqual(p1.score, 3)

        self.assertEqual(monastery.score(), 7)

        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (1,1))
        card = Card([RoadFragment(['n', 's'])])
        board.add_card(card, (1,-1))

        game.on_turn_end()
        self.assertTrue(monastery.is_closed())

        self.assertEqual(monastery.score(), 9)
        self.assertEqual(p0.score, 15)


    # add castles and meadows
    def test2(self):
        p0 = Player(token_count=2)
        p1 = Player(token_count=2)

        board = Board()
        game = Game([p0, p1], board)

        card = Card([CastleFragment(['e']), CastleFragment(['w']), MeadowFragment(['n', 's'])])
        status = board.add_card(card, (0,0))
        self.assertTrue(status)

        meadow1 = board.meadows.get(((0,0), 'n'))
        status = board.put_token(meadow1, p1)
        self.assertTrue(status)

        card = Card([CastleFragment(['n', 'w'], shield=True)])
        status = board.add_card(card, (-1,0), 3)
        self.assertTrue(status)

        status = board.put_token(board.castles.get(((-1,0), 'e')), p0)
        self.assertTrue(status)

        castle1 = board.castles.get(((0,0), 'w'))
        castle2 = board.castles.get(((-1,0), 'e'))
        self.assertTrue(castle1)
        self.assertEqual(castle1, castle2)
        self.assertFalse(castle1.is_closed())
        self.assertEqual(castle1.score(), 3)

        card = Card([CastleFragment(['s']), MeadowFragment(['n', 'e', 'w'])])
        status = board.add_card(card, (-1,1))
        self.assertTrue(status)
        self.assertTrue(castle1.is_closed())

        meadow2 = board.meadows.get(((-1,1), 'w'))
        self.assertTrue(meadow2)
        self.assertTrue(meadow1)
        self.assertNotEqual(meadow1, meadow2)
        self.assertEqual(meadow1.score(), 3)
        self.assertEqual(meadow2.score(), 3)

        status = board.put_token(meadow2, p1)
        self.assertTrue(status)

        game.on_turn_end()

        self.assertEqual(p0.score, 8)
        self.assertEqual(p1.score, 0)

        card = Card([MeadowFragment(['w', 's', 'n', 'e'])])
        status = board.add_card(card, (0,1))
        self.assertTrue(status)

        meadow1 = board.meadows.get(((0,0), 'n'))
        meadow2 = board.meadows.get(((-1,1), 'w'))
        self.assertTrue(meadow2)
        self.assertTrue(meadow1)
        self.assertEqual(meadow1, meadow2)
        self.assertEqual(meadow1.score(), 3)

        card = Card([CastleFragment(['w', 's']), MeadowFragment(['n', 'e'])])
        status = board.add_card(card, (1,0))
        self.assertTrue(status)

        status = board.put_token(board.meadows.get(((1,0), 'n')), p1)
        # player 1 is out of tokens
        self.assertFalse(status)
        self.assertEqual(p0.token_count, 2)

        game.on_game_end()
        self.assertEqual(p0.score, 8)
        self.assertEqual(p1.score, 3)

if __name__ == '__main__':
    unittest.main()
