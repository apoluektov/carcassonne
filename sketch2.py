import unittest


class Player:
    def __init__(self):
        self.score = 0


class Game:
    def __init__(self, num_of_players):
        self.players = [Player() for i in range(num_of_players)]


class Card:
    def __init__(self):
        pass


class Board:
    def __init__(self, game):
        self.game = game
        # (x,y) -> Card
        self.cards = dict()

    def add_card(self, card, xy, orient):
        if self.cards.get(xy):
            return False
        # FIXME: check that combines with neighbors
        # FIXME: use orientation
        self.cards[xy] = card

        return True


class CarcassoneTest(unittest.TestCase):

    def testSomething(self):
        self.assertFalse(False)

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
        card = Card()
        status = board.add_card(card, (0,0), 0)
        self.assertTrue(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)

        # put another card to the same position
        # the card should not be put there
        # the score should not change
        card = Card()
        status = board.add_card(card, (0,0), 0)
        self.assertFalse(status)
        self.assertEqual(game.players[0].score, 0)
        self.assertEqual(game.players[1].score, 0)
        


if __name__ == '__main__':
    unittest.main()
