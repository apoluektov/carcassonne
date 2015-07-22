import pygame

from main import *


screen = pygame.display.set_mode((640,480), pygame.RESIZABLE)


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
            return cx - y, cy + x
        elif orient == 2:
            return cx - x, cy - y
        elif orient == 3:
            return cx + y, cy - x

    if isinstance(pts,list):
        return[rot(x0-cx,y0-cy,orient) for (x0,y0) in pts]
    else:
        x0,y0 = pts
        return rot(x0-cx,y0-cy,orient)


def draw_card(xy, card, orient):
    x,y = xy
    dxdy = (100 + 100*x,100 + 100*y)

    pygame.draw.rect(screen, (0,180,0), pygame.Rect(0,0,100,100).move(*dxdy))

    for fragment in card.resources:
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
                xyS = 0,0
                if north_side in sides:
                    xyS = 50,10
                elif east_side in sides:
                    xyS = 90,50
                elif south_side in sides:
                    xyS = 50,90
                elif west_side in sides:
                    xyS = 10,50
                pygame.draw.circle(screen, (0,0,100),
                                   translate(rotate(xyS, orient, (50,50)),
                                             dxdy),
                                   5)

        elif fragment.code() == 'M':
            pygame.draw.rect(screen, (200,0,0), pygame.Rect(40,40,20,20).move(*dxdy))
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
            if len(coords) == 1:
                coords.append((50,50))
            pygame.draw.line(screen,(230,230,230),
                             translate(rotate(coords[0], orient, (50,50)), dxdy),
                             translate(rotate(coords[1], orient, (50,50)), dxdy),
                             10)


# TODO: draw tokens
# TODO: show *resources*
def draw_board(board):
    for xy,(card,orient) in board.cards.items():
        draw_card(xy, card, orient)


def draw():
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(0,0,640,480))

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


def run():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        draw()


if __name__ == '__main__':
    run()
