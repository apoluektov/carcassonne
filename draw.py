import pygame

from main import *

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
def draw_card(card, orient):
    img = pygame.Surface((100,100))

    pygame.draw.rect(img, (0,180,0), pygame.Rect(0,0,100,100))

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

            pygame.draw.polygon(img, brown, rotate(pts,orient,(50,50)))
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
                pygame.draw.circle(img, (0,0,150),
                                   rotate((mx,my), orient, (50, 50)), 10)

        elif fragment.code() == 'M':
            pygame.draw.rect(img, (200,0,0), pygame.Rect(30,30,40,40))
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
            pygame.draw.line(img,(230,230,230),
                             rotate(coords[0], orient, (50,50)),
                             rotate(coords[1], orient, (50,50)),
                             10)
            if len(fragment.sides) == 1:
                pygame.draw.rect(img, (0,0,0), pygame.Rect(44,44,12,12))
    return img


class App:
    def __init__(self, screen, screen_size):
        self.screen = screen
        self.screen_size = screen_size
        self.cx,self.cy = 0,0

        self.board = Board()
        self.deck = gen_standard_deck()
        self.orient = 0
        self.scale = 100.0

        self.draw_shadow = True

    def board_to_screen_coords(self, (x,y)):
        card_left = 300 + self.scale*x + self.cx
        card_top = 300 - self.scale*y + self.cy
        return (card_left,card_top)


    def redraw(self):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0,0,*self.screen_size))
        self.draw_board()
        card_left, card_top = self.board_to_screen_coords(self.cell_coords)
        if self.draw_shadow:
            pygame.draw.rect(self.screen, self.shadow_color(), (card_left, card_top, self.scale,self.scale))
            img = draw_card(self.card, self.orient)
            img = pygame.transform.scale(img,(int(self.scale),int(self.scale)))
            d = self.scale / 10
            self.screen.blit(img, pygame.Rect(card_left-d,card_top-d,self.scale,self.scale))
        else:
            img = draw_card(self.card, self.orient)
            img = pygame.transform.scale(img,(int(self.scale),int(self.scale)))
            self.screen.blit(img, pygame.Rect(card_left,card_top,self.scale,self.scale))


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
            img = draw_card(card, orient)
            img = pygame.transform.scale(img,(int(self.scale),int(self.scale)))
            screen_x, screen_y = self.board_to_screen_coords(xy)
            self.screen.blit(img, pygame.Rect(screen_x,screen_y,self.scale,self.scale))


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
                    self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEMOTION:
                    dx,dy = event.rel
                    if mouse_down:
                        self.cx += dx
                        self.cy += dy
                    else:
                        x,y = event.pos
                        self.cell_coords = (x - self.cx - 300) /int(self.scale), (300 - y + self.cy)/int(self.scale) + 1
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
                    if event.key == pygame.K_a:
                        self.scale /= 1.2
                    if event.key == pygame.K_s:
                        self.scale *= 1.2
                    self.redraw()

            pygame.display.flip()


def main():
    screen_size = (640,480)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    app = App(screen, screen_size)
    app.run()


if __name__ == '__main__':
    main()
