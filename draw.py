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


class View:
    def __init__(self, screen, screen_size, board):
        self.screen = screen
        self.size = screen_size
        # TODO: maybe instead of scale and center have topleft and bottomright? Dunno
        self.scale = 100.0
        self.scale_factor = 1.2
        self.center = 0,0
        self.mouse_pointer = 0,0

        self.orient = 0
        self.card_down = False

        self.board = board
        self.card = None
        # TODO: deck object?
        self.cards, self.freqs = gen_standard_deck()
        self.cards_it = iter(self.cards.values())

        self.dirty = True

    def resize(self, new_size):
        self.size = new_size
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.dirty = True

    def move_center(self, (dx,dy)):
        self.center = (self.center[0] + dx, self.center[1] + dy)
        self.dirty = True

    def zoom_in(self):
        self.scale *= self.scale_factor
        self.dirty = True

    def zoom_out(self):
        self.scale /= self.scale_factor
        self.dirty = True

    def rotate_current_card(self):
        self.orient = (self.orient + 1) % 4
        self.dirty = True

    def move_current_card_to(self, (x,y)):
        self.mouse_pointer = x,y
        self.dirty = True

    def maybe_put_current_card(self):
        model_coords = self.screen_to_model(self.mouse_pointer)
        if self.board.can_put_card(self.card, model_coords, self.orient):
            self.board.add_card(self.card, model_coords, self.orient)
            self.card_down = True
            self.dirty = True

    def next_card(self):
        try:
            self.card = self.cards_it.next()
        except StopIteration:
            self.cards_it = iter(self.cards.values())
            self.card = self.cards_it.next()
        self.dirty = True

    def needs_redraw(self):
        return self.dirty

    def redraw(self):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0,0,*self.size))

        model_coords = self.screen_to_model(self.mouse_pointer)
        left0, top0 = self.model_to_screen(model_coords)

        # the shadow
        if not self.card_down:
            if self.board.can_put_card(self.card, model_coords, self.orient):
                color = (200,255,200)
            else:
                color = (255,200,200)
            pygame.draw.rect(self.screen, color, (left0, top0, self.scale, self.scale))

        # the board
        for xy, (card, orient) in self.board.cards.items():
            img = draw_card(card, orient)
            img = pygame.transform.scale(img,(int(self.scale),int(self.scale)))
            left, top = self.model_to_screen(xy)
            self.screen.blit(img, pygame.Rect(left, top, self.scale, self.scale))

        # the card
        if not self.card_down:
            dx, dy = self.scale/10, self.scale/10
        else:
            dx, dy = 0, 0
        img = draw_card(self.card, self.orient)
        img = pygame.transform.scale(img,(int(self.scale), int(self.scale)))
        self.screen.blit(img, pygame.Rect(left0-dx, top0-dy, self.scale, self.scale))


        pygame.display.flip()
        self.dirty = False


    def model_to_screen(self, (x,y)):
        left = 300 + self.scale*x + self.center[0]
        top = 300 - self.scale*y + self.center[1]
        return left, top

    def screen_to_model(self, (x,y)):
        cx,cy = self.center
        s = int(self.scale)
        return (x - cx - 300)/s,  (300 - y + cy)/s + 1


class App:
    def __init__(self, screen, screen_size):
        board = Board()
        self.view = View(screen, screen_size, board)


    def run(self):
        view = self.view
        view.next_card()
        right_mouse_down = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    view.resize((event.w, event.h))
                elif event.type == pygame.MOUSEMOTION:
                    dx,dy = event.rel
                    if right_mouse_down:
                        view.move_center(event.rel)
                    view.move_current_card_to(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        right_mouse_down = True
                    else:
                        view.maybe_put_current_card()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        right_mouse_down = False
                    else:
                        # FIXME: meh, method
                        view.card_down = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        view.rotate_current_card()
                    if event.key == pygame.K_SPACE:
                        view.next_card()
                    if event.key == pygame.K_a:
                        view.zoom_out()
                    if event.key == pygame.K_s:
                        view.zoom_in()

            if view.needs_redraw():
                view.redraw()


def main():
    screen_size = (640,480)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    app = App(screen, screen_size)
    app.run()


if __name__ == '__main__':
    main()
