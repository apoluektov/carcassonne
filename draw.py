import pygame

from main import *

screen_size = (640,480)
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)


def translate(pts, (dx,dy)):
    if isinstance(pts,list):
        return [(x0+dx,y0+dy) for (x0,y0) in pts]
    else:
        x0,y0 = pts
        return x0+dx,y0+dy


def rotate(pts, orient, center):
    cx,cy = center

    def rot(x,y,orient):
        if orient == 0:
            return cx + x, cy + y
        elif orient == 1:
            return cx + y, cy - x
        elif orient == 2:
            return cx - x, cy - y
        elif orient == 3:
            return cx - y, cy + x


    if isinstance(pts,list):
        return[rot(x0-cx,y0-cy,orient) for (x0,y0) in pts]
    else:
        x0,y0 = pts
        return rot(x0-cx,y0-cy,orient)


# FIXME: this last arg is a hack
def draw_card(card, orient, topleft):
    dxdy = topleft

    pygame.draw.rect(screen, (0,180,0), pygame.Rect(0,0,100,100).move(*dxdy))

    # want to draw roads first -- so the monasteries and castles are drawn on top
    for fragment in sorted(card.resources, key=lambda r: -ord(r.code())):
        if fragment.code() == 'c':
            sides = fragment.sides
            brown = (140,70,20)

            pts = None
            # FIXME: uglier than ugly
            if len(sides) == 4:
                pts = [(0,0), (100,0), (100,100), (0,100)]
            elif len(sides) == 3:
                if not north_side in sides:
                    pts = [(0,0), (30,20), (70,20), (100,0), (100,100), (0,100)]
                elif not east_side in sides:
                    pts = [(100,0), (80,30), (80,70), (100,100), (0,100), (0,0)]
                elif not south_side in sides:
                    pts = [(100,100), (70,80), (30,80), (0,100), (0,0), (100,0)]
                elif not west_side in sides:
                    pts = [(0,100), (20,70), (20,30), (0,0), (100,0), (100,100)]
            elif len(sides) == 2:
                if north_side in sides and south_side in sides:
                    pts = [(0,0), (100,0), (80,30), (80,70), (100,100), (0,100), (20,70), (20,30)]
                elif east_side in sides and west_side in sides:
                    pts = [(100,0), (100,100), (70,80), (30,80), (0,100), (0,0), (30,20), (70,20)]
                elif north_side in sides and west_side in sides:
                    pts = [(0,0), (100,0), (0,100)]
                elif north_side in sides and east_side in sides:
                    pts = [(0,0), (100,0), (100,100)]
                elif south_side in sides and west_side in sides:
                    pts = [(100,100), (0,100), (0,0)]
                elif south_side in sides and east_side in sides:
                    pts = [(100,100), (0,100), (100,0)]
            elif len(sides) == 1:
                if north_side in sides:
                    pts = [(0,0), (30,20), (70,20), (100,0)]
                elif east_side in sides:
                    pts = [(100,0), (80,30), (80,70), (100,100)]
                elif south_side in sides:
                    pts = [(100,100), (70,80), (30,80), (0,100)]
                elif west_side in sides:
                    pts = [(0,100), (20,70), (20,30), (0,0)]

            pygame.draw.polygon(screen, brown, translate(rotate(pts,orient,(50,50)), dxdy))
            if fragment.shield:
                sides = fragment.sides[:]
                # in standard deck there no castle fragments with just one side that have shields
                assert(len(sides) >= 2)
                mx,my = 0,0
                xyS = 0,0
                # want to be shield shifted towards one of the side
                for i in range(len(sides)-1):
                    sides.append(sides[0])
                for s in sides:
                    if s == north_side:
                        mx, my = mx+50, my
                    if s == east_side:
                        mx, my = mx+100, my+50
                    if s == south_side:
                        mx, my = mx+50, my+100
                    if s == west_side:
                        mx, my = mx, my+50
                mx, my = mx/len(sides), my/len(sides)
                pygame.draw.circle(screen, (0,0,150),
                                   translate(rotate((mx,my), orient, (50,50)),
                                             dxdy),
                                   10)

        elif fragment.code() == 'M':
            pygame.draw.rect(screen, (200,0,0), pygame.Rect(30,30,40,40).move(*dxdy))
        elif fragment.code() == 'r':
            coords = []
            for s in fragment.sides:
                if s == north_center:
                    coords.append((50,0))
                elif s == east_center:
                    coords.append((100,50))
                elif s == south_center:
                    coords.append((50,100))
                elif s == west_center:
                    coords.append((0,50))
            if len(fragment.sides) == 1:
                coords.append((50,50))
            pygame.draw.line(screen,(230,230,230),
                             translate(rotate(coords[0], orient, (50,50)), dxdy),
                             translate(rotate(coords[1], orient, (50,50)), dxdy),
                             10)
            if len(fragment.sides) == 1:
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(44,44,12,12).move(*dxdy))


def draw():
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(0,0,*screen_size))

    draw_card((-1,0), Card([
        CastleFragment([north_side], shield=True),
        MeadowFragment([east_north_half, west_north_half]),
        MeadowFragment([east_south_half, south_side, west_south_half]),
        RoadFragment([east_center, west_center]),
    ]), 0)

    draw_card((0,0), Card([
        MeadowFragment([north_side, east_side, south_east_half, south_west_half, west_side]),
        MonasteryFragment(),
        RoadFragment([south_center]),
    ]), 0)

    draw_card((1,0), Card([
        CastleFragment([east_side, west_side], shield=True),
        MeadowFragment([north_side]),
        MeadowFragment([south_side]),
    ]), 0)

    draw_card((-1,1), Card([
        CastleFragment([north_side, west_side]),
        MeadowFragment([east_north_half, south_west_half]),
        MeadowFragment([east_south_half, south_east_half]),
        RoadFragment([east_center, south_center]),
    ]), 0)

    draw_card((0,1), Card([
        CastleFragment([north_side, east_side, west_side], shield=True),
        MeadowFragment([south_east_half]),
        MeadowFragment([south_west_half]),
        RoadFragment([south_center]),
    ]), 0)

    draw_card((1,1), Card([
        CastleFragment([north_side, east_side, west_side], shield=True),
        MeadowFragment([south_east_half]),
        MeadowFragment([south_west_half]),
        RoadFragment([south_center]),
    ]), 1)

    pygame.display.flip()


class App:
    def __init__(self, screen, screen_size):
        self.screen = screen
        self.screen_size = screen_size
        self.cx,self.cy = 0,0

        self.board = Board()
        self.deck = gen_standard_deck()
        self.orient = 0

        self.draw_shadow = True

    def board_to_screen_coords(self, (x,y)):
        card_left = 100 + 100*x + self.cx
        card_top = 300 - 100*y + self.cy
        return (card_left,card_top)


    def redraw(self):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0,0,*self.screen_size))
        self.draw_board()
        card_left, card_top = self.board_to_screen_coords(self.cell_coords)
        if self.draw_shadow:
            pygame.draw.rect(self.screen, self.shadow_color(), (card_left, card_top, 100,100))
            draw_card(self.card, self.orient, (card_left-10, card_top-10))
        else:
            draw_card(self.card, self.orient, (card_left, card_top))


    def next_card(self):
        try:
            self.card = self.cards_it.next()
        except StopIteration:
            self.cards_it = iter(self.cards.values())
            self.card = self.cards_it.next()

    def maybe_put_card(self):
        if self.board.can_put_card(self.card, self.cell_coords, self.orient):
            self.draw_shadow = False
            self.board.add_card(self.card, self.cell_coords, self.orient)

    # TODO: draw tokens
    # TODO: show *resources*
    def draw_board(self):
        for xy,(card,orient) in self.board.cards.items():
            draw_card(card, orient, self.board_to_screen_coords(xy))


    def shadow_color(self):
        if self.board.can_put_card(self.card, self.cell_coords, self.orient):
            return (200,255,200)
        else:
            return (255,200,200)


    def run(self):
        self.cards,_ = self.deck

        self.cards_it = iter(self.cards.values())
        self.next_card()

        mouse_down = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_size = event.w,event.h
                    self.screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEMOTION:
                    dx,dy = event.rel
                    if mouse_down:
                        self.cx += dx
                        self.cy += dy
                    else:
                        x,y = event.pos
                        self.cell_coords = (x - self.cx) /100 - 1, 2 - ((y - self.cy)/100 - 1)
                    self.redraw()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        mouse_down = True
                    else:
                        self.maybe_put_card()
                    self.redraw()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        mouse_down = False
                    self.draw_shadow = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.orient = (self.orient + 1) % 4
                    if event.key == pygame.K_SPACE:
                        self.next_card()
                    self.redraw()

            pygame.display.flip()


if __name__ == '__main__':
    app = App(screen, screen_size)
    app.run()
