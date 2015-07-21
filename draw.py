import pygame

from main import *


screen = pygame.display.set_mode((640,480), pygame.RESIZABLE)


def draw_card(card):
    pygame.draw.rect(screen, (0,180,0), pygame.Rect(100,100,100,100))
    for fragment in card.resources:
        if fragment.code() == 'c':
            sides = fragment.sides
            brown = (140,70,20)

            # FIXME: uglier than ugly
            if len(sides) == 4:
                pygame.draw.rect(brown, pygame.Rect(100,100,100,100))
            elif len(sides) == 3:
                if not north_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,100), (130,120), (170,120), (200,100),
                                         (200,200), (100,200)])
                elif not east_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,100), (180,130), (180,170), (200,200),
                                         (100,200), (100,100)])
                elif not south_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,200), (170,180), (130,180), (100,200),
                                         (100,100), (200,100)])
                elif not west_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,200), (120,170), (120,130), (100,100),
                                         (200,100), (200,200)])
            elif len(sides) == 2:
                if north_side in sides and south_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,100), (200,100), (180,130), (180,170),
                                         (200,200), (100, 200), (120,170), (120,130)])
                elif east_side in sides and west_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,100), (200,200), (170,180), (130,180),
                                         (100,200), (100,100), (130,120), (170,120)])
                elif north_side in sides and west_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,100), (200,100), (100,200)])
                elif north_side in sides and east_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,100), (200,100), (200,200)])
                elif south_side in sides and west_side in sides:
                    pygane.draw.polygon(screen, brown,
                                        [(200,200), (100,200), (100,100)])
                elif south_side in sides and east_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,200), (100,200), (200,100)])
            elif len(sides) == 1:
                if north_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,100), (130,120), (170,120), (200,100)])
                elif east_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,100), (180,130), (180,170), (200,200)])
                elif south_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(200,200), (170,180), (130,180), (100,200)])
                elif west_side in sides:
                    pygame.draw.polygon(screen, brown,
                                        [(100,200), (120,170), (120,130), (100,100)])
            if fragment.shield:
                xy = 0,0
                if north_side in sides:
                    xy = 150,110
                elif east_side in sides:
                    xy = 190,150
                elif south_side in sides:
                    xy = 150,190
                elif west_side in sides:
                    xy = 110,150
                pygame.draw.circle(screen, (0,0,100), xy, 5)

        elif fragment.code() == 'M':
            pygame.draw.rect(screen, (200,0,0), pygame.Rect(140,140,20,20))
        elif fragment.code() == 'r':
            coords = []
            for s in fragment.sides:
                if s == north_center:
                    coords.append((150,100))
                elif s == east_center:
                    coords.append((200,150))
                elif s == south_center:
                    coords.append((150,200))
                elif s == west_center:
                    coords.append((100,150))
            if len(coords) == 1:
                coords.append((150,150))
            pygame.draw.line(screen,(230,230,230),coords[0],coords[1], 10)



def draw():
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(0,0,640,480))

    draw_card(Card([
        CastleFragment([north_side], shield=True),
        MeadowFragment([east_north_half, west_north_half]),
        MeadowFragment([east_south_half, south_side, west_south_half]),
        RoadFragment([east_center, west_center]),
    ]))

    draw_card(Card([
        MeadowFragment([north_side, east_side, south_east_half, south_west_half, west_side]),
        MonasteryFragment(),
        RoadFragment([south_center]),
    ]))

    draw_card(Card([
        CastleFragment([east_side, west_side], shield=True),
        MeadowFragment([north_side]),
        MeadowFragment([south_side]),
    ]))

    draw_card(Card([
        CastleFragment([north_side, west_side]),
        MeadowFragment([east_north_half, south_west_half]),
        MeadowFragment([east_south_half, south_east_half]),
        RoadFragment([east_center, south_center]),
    ]))

    draw_card(Card([
        CastleFragment([north_side, east_side, west_side], shield=True),
        MeadowFragment([south_east_half]),
        MeadowFragment([south_west_half]),
        RoadFragment([south_center]),
    ]))

    pygame.display.flip()


def run():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        draw()


if __name__ == '__main__':
    run()
