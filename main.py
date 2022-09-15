import pygame


FPS = 60
GAME_TITLE = "Brick Breaker"

LEFT_DIR, RIGHT_DIR = -1, +1

WINDOW_COLOR = "white"
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

PADDLE_COLOR = "black"
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
PADDLE_INIT_X = WINDOW_WIDTH/2 - PADDLE_WIDTH/2
PADDLE_INIT_Y = WINDOW_HEIGHT - PADDLE_HEIGHT - (PADDLE__INIT_Y_MARGIN := 5)


class Paddle:
    VEL = 5

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect)

    def move(self, direction=RIGHT_DIR):
        self.rect.left += (delta_x := self.VEL * direction)


def draw(paddle: Paddle):
    WINDOW.fill(WINDOW_COLOR)
    paddle.draw()


def main():
    pygame.display.set_caption(GAME_TITLE)

    clock = pygame.time.Clock()

    paddle = Paddle(PADDLE_INIT_X,
                    PADDLE_INIT_Y,
                    PADDLE_WIDTH,
                    PADDLE_HEIGHT,
                    PADDLE_COLOR)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            paddle.move(LEFT_DIR)
        if keys[pygame.K_RIGHT]:
            paddle.move(RIGHT_DIR)

        draw(paddle)
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
