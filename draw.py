import unittest
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


class Geometry:
    def __init__(self):
        self.polygon = None
        self.polygon_color = None
        self.polygon2 = None
        self.polygon2_color = None
        self.circle = None
        self.circle_color = None


def is_point_in_polygon(p, polygon):
    # ray casting even odd
    n = 0
    for i in range(len(polygon)):
        s1,s2 = polygon[i%len(polygon)],polygon[(i+1)%len(polygon)]
        s1,s2 = sorted((s1,s2))
        S1x,S1y = s1
        S2x,S2y = s2
        Px,Py = p
        Sxmin = min(S1x,S2x)
        Sxmax = max(S1x,S2x)
        Symin = min(S1y,S2y)
        Symax = min(S1y,S2y)

        if min(S1y,S2y) > Py:
            if Sxmin <= Px and Px < Sxmax:
                n += 1
        elif max(S1y,S2y) < Py:
            pass
        else:
            d1 = abs((S1y - Py) * (Px - S2x))
            d2 = abs((S2y - Py) * (Px - S1x))
            if S1y == Symax:
                if d1 >= d2:
                    n += 1
            else:
                if d1 <= d2:
                    n += 1

    return n % 2 == 1


class CardView:
    def __init__(self, card, orient):
        self.card = card
        self.orient = orient
        self.geometries = []
        self.calculate_geometries()

    def calculate_geometries(self):
        # want to draw roads first -- so the monasteries and castles are drawn on top
        for fragment in sorted(self.card.resources, key=lambda r: -ord(r.code())):
            if fragment.code() == 'c':
                self.geometries.append(self.castle_geometry(fragment))
            elif fragment.code() == 'M':
                self.geometries.append(self.monastery_geometry(fragment))
            elif fragment.code() == 'r':
                self.geometries.append(self.road_geometry(fragment))
            elif fragment.code == 'm':
                # TODO: handle meadows
                pass

    def castle_geometry(self, fragment):
        sides = fragment.sides
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

        geom = Geometry()
        geom.polygon = rotate(pts, self.orient, (50,50))
        geom.polygon_color = (140,70,20)

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

            geom.circle = (rotate((mx,my), self.orient, (50,50)), 10)
            geom.circle_color = (0,0,150)

        return geom

    def monastery_geometry(self, fragment):
        pts = [(30,30), (30,70), (70,70), (70,30)]
        geom = Geometry()
        geom.polygon = pts
        geom.polygon_color = (200,0,0)
        return geom

    def road_geometry(self, fragment):
        coords = []
        for s in fragment.sides:
            if s == north_center:
                coords.append((45,0))
                coords.append((55,0))
                if len(fragment.sides) == 1:
                    coords.append((55,45))
                    coords.append((45,45))
            elif s == east_center:
                coords.append((100,45))
                coords.append((100,55))
                if len(fragment.sides) == 1:
                    coords.append((55,55))
                    coords.append((55,45))
            elif s == south_center:
                coords.append((55,100))
                coords.append((45,100))
                if len(fragment.sides) == 1:
                    coords.append((45,55))
                    coords.append((55,55))
            elif s == west_center:
                coords.append((0,55))
                coords.append((0,45))
                if len(fragment.sides) == 1:
                    coords.append((45,45))
                    coords.append((45,55))

        geom = Geometry()
        geom.polygon = rotate(coords, self.orient, (50,50))
        geom.polygon_color = (230,230,230)
        if len(fragment.sides) == 1:
            geom.polygon2 = [(44,44), (44,56), (56,56), (56,44)]
            geom.polygon2_color = (0,0,0)
        return geom


def draw_card(card, orient):
    img = pygame.Surface((100,100))
    pygame.draw.rect(img, (0,180,0), pygame.Rect(0,0,100,100))

    card_view = CardView(card, orient)
    for geom in card_view.geometries:
        if geom.polygon:
            pygame.draw.polygon(img, geom.polygon_color, geom.polygon)
        if geom.polygon2:
            pygame.draw.polygon(img, geom.polygon2_color, geom.polygon2)
        if geom.circle:
            pygame.draw.circle(img, geom.circle_color, geom.circle[0], geom.circle[1])
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
        self.card_idx = -1

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
        self.card_idx = (self.card_idx + 1) % len(self.cards)
        self.card = self.cards[chr(ord('A') + self.card_idx)]
        self.dirty = True

    def previous_card(self):
        self.card_idx = (self.card_idx - 1) % len(self.cards)
        self.card = self.cards[chr(ord('A') + self.card_idx)]
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
                    if event.key == pygame.K_RIGHTBRACKET:
                        view.next_card()
                    if event.key == pygame.K_LEFTBRACKET:
                        view.previous_card()
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


class IntersectionTest(unittest.TestCase):
    def test1(self):
        pts = [(0,0), (30,20), (70,20), (100,0), (100,100), (0,100)]
        self.assertTrue(is_point_in_polygon((50,50), pts))
        self.assertFalse(is_point_in_polygon((50,0), pts))
        self.assertTrue(is_point_in_polygon((30,50), pts))
        self.assertFalse(is_point_in_polygon((10,10), pts))
        self.assertFalse(is_point_in_polygon((30,10), pts))
        self.assertFalse(is_point_in_polygon((40,20), pts))
        self.assertTrue(is_point_in_polygon((0,0), pts))


if __name__ == '__main__':
    unittest.main()
    main()
