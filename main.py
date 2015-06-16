class Card:
    def __init__(self, e, n, w, s):
        self.sides = [e, n, w, s]

    def rotate(self, n):
        self.sides = self.sides[n:] + self.sides[:n]


def rotated(card, n):
    new = Card(*card.sides)
    new.rotate(n)
    return new    


coordDiffToMutualOrientation = { (0,-1): 0, (1,0): 1, (0,1): 2, (-1,0): 3 }
def match(card1, card2, coordDiff):
    mutOr = coordDiffToMutualOrientation[coordDiff]
    return card1.sides[mutOr%4] == card2.sides[(2+mutOr)%4]


class Board:
    def __init__(self):
        self.cards = dict()
        
    def add(self, card, x, y, orient):
        if not self.match(card, x, y, orient):
            raise BaseException("invalid move")
        self.cards[(x,y)] = rotated(card, orient)

    def match(self, card, x, y, orient):
        if not self.cards:
            return True

        rotCard = rotated(card, orient)
        foundNeighbor = False
        for coordDiff in [(0,-1), (1,0), (0,1), (-1,0)]:
            (x1,y1) = (x + coordDiff[0], y + coordDiff[1])
            neighbor = self.cards.get((x1,y1))
            if not neighbor:
                continue
            foundNeighbor = True
            if not match(rotCard, neighbor, coordDiff):
                return False
        return foundNeighbor

    def possibleMoves(self, card):
        result = []
        for (x,y),c in self.cards.items():
            for coordDiff in [(0,-1), (1,0), (0,1), (-1,0)]:
                (x1,y1) = (x + coordDiff[0], y + coordDiff[1])
                if self.cards.get((x1,y1)):
                    # (x1,y1) occupied by another card
                    continue
                for orient in [0,1,2,3]:
                    rotCard = rotated(card, orient)
                    if match(c, rotCard, coordDiff):
                        # TODO: handle cases when card is neghboring several others
                        result.append((x,y1,orient))
        return result

