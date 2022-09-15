import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

GAME_TITLE = "Brick Breaker"
pygame.display.set_caption(GAME_TITLE)

FPS = 60


def draw():
    WINDOW.fill("white")
    pygame.display.update()


def main():
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                    break

        draw()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
