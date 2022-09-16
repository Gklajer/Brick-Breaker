import math

import pygame


FPS = 60
GAME_TITLE = "Brick Breaker"

LEFT_DIR, RIGHT_DIR = -1, +1

WINDOW_COLOR = "white"
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

PADDLE_VEL = WINDOW_WIDTH/100
PADDLE_COLOR = "black"
PADDLE_WIDTH, PADDLE_HEIGHT = WINDOW_WIDTH/8, WINDOW_HEIGHT/40
PADDLE_INIT_X = WINDOW_WIDTH / 2 - PADDLE_WIDTH / 2
PADDLE_INIT_Y = WINDOW_HEIGHT - PADDLE_HEIGHT - \
    (PADDLE__INIT_Y_MARGIN := WINDOW_HEIGHT/120)

BALL_VEL = WINDOW_WIDTH/100
BALL_COLOR = "black"
BALL_RADIUS = 10
BALL_INIT_X = WINDOW_WIDTH / 2
BALL_INIT_Y = PADDLE_INIT_Y - BALL_RADIUS

GREEN = (0, 255, 0)
BRICKS_COLS_NUMBER, BRICKS_ROWS_NUMBER = 10, 3
BRICKS_COLOR = GREEN
BRICKS_GAP = 1
BRICKS_COLLIDER_EPS = BRICKS_GAP
BRICKS_GAP_COLLIDER_EPS = BRICKS_GAP/2
BRICKS_HEALTH = 4
BRICKS_COLOR_DIVISOR = 8 ** (1 / BRICKS_HEALTH)
BRICKS_TOTAL_HEIGHT = WINDOW_HEIGHT / 8
BRICKS_WIDTH = (
    WINDOW_WIDTH - (BRICKS_GAP * (BRICKS_COLS_NUMBER - 1))
) / BRICKS_COLS_NUMBER
BRICKS_HEIGHT = (
    BRICKS_TOTAL_HEIGHT - (BRICKS_GAP * (BRICKS_ROWS_NUMBER - 1))
) / BRICKS_ROWS_NUMBER


class Paddle:
    VEL = PADDLE_VEL

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect)

    def move(self, direction=RIGHT_DIR):
        # Check boundaries
        if not (
            0 < self.rect.left + (delta_x := self.VEL * direction)
            and self.rect.right + delta_x < WINDOW_WIDTH
        ):
            return None

        self.rect.left += delta_x


class Ball:
    VEL = BALL_VEL

    def __init__(self, x, y, radius, color):
        self.radius = radius
        self.color = color
        self.x_vel, self.y_vel = 2, -self.VEL
        self.rect = pygame.draw.circle(WINDOW, self.color, (x, y), self.radius)

    def draw(self):
        pygame.draw.circle(WINDOW, self.color, self.rect.center, self.radius)

    def _collide_boundaries(self):
        # Check boundaries collisions

        # Left and right walls
        if not (
            0 < self.rect.left + self.x_vel
            and self.rect.right + self.x_vel < WINDOW_WIDTH
        ):
            # Reverse x velocity
            self.x_vel *= -1

        # Ceilling
        if not (0 < self.rect.top + self.y_vel):
            # Reverse y velocity
            self.y_vel *= -1

        # Floor TODO
        if not (self.rect.bottom > WINDOW_HEIGHT):
            pass

    def move(self):
        self._collide_boundaries()
        self.rect.left += self.x_vel
        self.rect.bottom += self.y_vel


class Brick:

    def __init__(self, x, y, width, height, health, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.health = health
        self.color = color

    def draw(self):
        pygame.draw.rect(
            WINDOW,
            self.color,
            self.rect,
        )

    def hit(self):
        self.health -= 1
        self.color = tuple(map(lambda i: i / BRICKS_COLOR_DIVISOR, self.color))

    def _x_collision(self, ball: Ball):
        # Collision left or right
        if ((self.rect.top - BRICKS_GAP_COLLIDER_EPS <=
             ball.rect.centery
             <= self.rect.bottom + BRICKS_GAP_COLLIDER_EPS)
                and ((self.rect.left - BRICKS_COLLIDER_EPS <=
                      ball.rect.right
                      <= self.rect.right)
                     or
                     (self.rect.left <=
                      ball.rect.left
                      <= self.rect.right + BRICKS_COLLIDER_EPS))):
            ball.x_vel *= -1
            return True
        else:
            return False

    def _y_collision(self, ball: Ball):
        # Collision bottom ot top
        if ((self.rect.left - BRICKS_GAP_COLLIDER_EPS <=
             ball.rect.centerx
             <= self.rect.right + BRICKS_GAP_COLLIDER_EPS)
            and ((self.rect.top <=
                  ball.rect.top
                  <= self.rect.bottom + BRICKS_COLLIDER_EPS)
                 or
                 (self.rect.top - BRICKS_COLLIDER_EPS <=
                 ball.rect.bottom
                 <= self.rect.bottom))):
            ball.y_vel *= -1
            return True

        return False

    def collide(self, ball: Ball):
        if self._x_collision(ball) or self._y_collision(ball):
            self.hit()
            return True

        return False


def generate_bricks():
    return [
        Brick(
            (BRICKS_WIDTH + BRICKS_GAP) * col,
            (BRICKS_HEIGHT + BRICKS_GAP) * row,
            BRICKS_WIDTH,
            BRICKS_HEIGHT,
            BRICKS_HEALTH,
            BRICKS_COLOR,
        )
        for col in range(BRICKS_COLS_NUMBER)
        for row in range(BRICKS_ROWS_NUMBER)
    ]


def draw(paddle: Paddle, ball: Ball, bricks: list[Brick]):
    WINDOW.fill(WINDOW_COLOR)
    paddle.draw()
    ball.draw()

    for brick in bricks:
        brick.draw()


def check_ball_paddle_collision(ball: Ball, paddle: Paddle):
    return (paddle.rect.left <= ball.rect.centerx <= paddle.rect.right) and (
        ball.rect.bottom >= paddle.rect.top
    )


def ball_paddle_collision(ball: Ball, paddle: Paddle):
    if not check_ball_paddle_collision(ball, paddle):
        return None
    distance_center = ball.rect.centerx - paddle.rect.centerx
    percent_width = (distance_center) / (
        paddle.rect.width / 2
    )
    angle_deg = percent_width * 90
    angle_rad = math.radians(angle_deg)
    ball.x_vel = math.sin(angle_rad) * ball.VEL
    ball.y_vel = -math.cos(angle_rad) * ball.VEL


def ball_bricks_collision(ball: Ball, bricks: list[Brick]):
    for brick in bricks[:]:
        brick.collide(ball)

        if brick.health <= 0:
            bricks.remove(brick)


def main():
    pygame.display.set_caption(GAME_TITLE)

    clock = pygame.time.Clock()

    paddle = Paddle(
        PADDLE_INIT_X, PADDLE_INIT_Y, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR
    )

    ball = Ball(BALL_INIT_X, BALL_INIT_Y, BALL_RADIUS, BALL_COLOR)

    bricks = generate_bricks()

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

        ball_paddle_collision(ball, paddle)
        ball_bricks_collision(ball, bricks)
        ball.move()
        draw(paddle, ball, bricks)
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
