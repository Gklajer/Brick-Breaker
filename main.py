import math
from random import randrange

import pygame

pygame.init()

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
BALL_UNSTUCK_EPS = 1

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

LIVES_FONT_SIZE = 40
LIVES_FONT_COLOR = "black"
LIVES_FONT = pygame.font.SysFont("comics", LIVES_FONT_SIZE)
LIVES_INIT_NUMBER = 3
LIVES_TEXT_POS_MARGIN = WINDOW_WIDTH/80


class Paddle:
    VEL = PADDLE_VEL

    def __init__(self, x, y, width, height, color):
        self.init_pos = x, y
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

    def reset_pos(self):
        self.rect.topleft = self.init_pos


class Ball:
    VEL = BALL_VEL

    def __init__(self, x, y, radius, color):
        self.init_pos = x, y
        self.radius = radius
        self.color = color
        self.x_vel, self.y_vel = 2, -self.VEL
        self.rect = pygame.draw.circle(WINDOW, self.color, (x, y), self.radius)

    def draw(self):
        pygame.draw.circle(WINDOW, self.color, self.rect.center, self.radius)

    def _bounce_rand(self, vel: float):
        return vel*(1-randrange(-20, 21)/100)

    def bounce_x(self, old_vel: float = None):
        if old_vel is None:
            old_vel = self.x_vel

        self.x_vel = (rand_bounce := self._bounce_rand(-old_vel))

        if abs(self.y_vel) <= BALL_UNSTUCK_EPS:
            self.y_vel = -abs(rand_bounce)

    def bounce_y(self, old_vel: float = None):
        if old_vel is None:
            old_vel = self.y_vel

        self.y_vel = (rand_bounce := self._bounce_rand(-old_vel))

        if abs(self.x_vel) <= BALL_UNSTUCK_EPS:
            self.x_vel = -rand_bounce

    def _collide_boundaries(self):
        # Check boundaries collisions

        # Left and right walls
        if not (
            0 < self.rect.left + self.x_vel
            and self.rect.right + self.x_vel < WINDOW_WIDTH
        ):
            # Reverse x velocity
            self.bounce_x()

        # Ceilling
        if not (0 < self.rect.top + self.y_vel):
            # Reverse y velocity
            self.bounce_y()

    def move(self):
        self._collide_boundaries()
        self.rect.left += self.x_vel
        self.rect.bottom += self.y_vel

    def reset_pos(self):
        self.rect.topleft = self.init_pos


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
            ball.bounce_x()
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
            ball.bounce_y()
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


def draw(paddle: Paddle, ball: Ball, bricks: list[Brick], lives_number: int):
    WINDOW.fill(WINDOW_COLOR)
    paddle.draw()
    ball.draw()

    for brick in bricks:
        brick.draw()

    lives_text = LIVES_FONT.render(f"Lives : {lives_number}",
                                   True,
                                   LIVES_FONT_COLOR)
    WINDOW.blit(lives_text, (LIVES_TEXT_POS_MARGIN,
                             WINDOW_HEIGHT -
                             LIVES_TEXT_POS_MARGIN -
                             lives_text.get_height()))


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
    ball.bounce_x(-math.sin(angle_rad) * ball.VEL)
    ball.bounce_y(math.cos(angle_rad) * ball.VEL)


def ball_bricks_collision(ball: Ball, bricks: list[Brick]):
    for brick in bricks[:]:
        brick.collide(ball)

        if brick.health <= 0:
            bricks.remove(brick)


def ball_hits_ground(ball: Ball, lives_number: int):
    if (ball.rect.top > WINDOW_HEIGHT):
        return lives_number - 1

    return None


def reset_pos(ball: Ball, paddle: Paddle):
    ball.reset_pos()
    paddle.reset_pos()


def main():
    pygame.display.set_caption(GAME_TITLE)

    clock = pygame.time.Clock()

    paddle = Paddle(
        PADDLE_INIT_X, PADDLE_INIT_Y, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR
    )

    ball = Ball(BALL_INIT_X, BALL_INIT_Y, BALL_RADIUS, BALL_COLOR)

    bricks = generate_bricks()

    lives_number = LIVES_INIT_NUMBER

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

        if (result := ball_hits_ground(ball, lives_number)) is None:
            pass
        elif result <= 0:
            return True
        else:
            lives_number = result
            print(lives_number)
            reset_pos(ball, paddle)

        draw(paddle, ball, bricks, lives_number)
        pygame.display.update()

    pygame.quit()
    return False


if __name__ == "__main__":
    while main():
        continue

    quit()
