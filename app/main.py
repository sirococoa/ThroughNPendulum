import pyxel

from enum import Enum

import pendulum

WINDOW_W = 160
WINDOW_H = 120

FLOAR = WINDOW_H // 4 * 3

TIME_DURATION = 30  # Time duration in seconds
SIMURATION_FLAME = 300

LENGTH_RANGE = (5.0, 30.0)  # Length of the pendulum strings in meters
WEIGHT_RANGE = (1.0, 10.0)  # Weight of the pendulum bob in kg
# Initial angles of the pendulum bobs in radians
INIT_ANGLE_RANGE = (-3.14, 3.14)
# Initial velocities of the pendulum bobs in m/s
INIT_VELOCITY_RANGE = (-1.0, 1.0)

def generate_gradation(start_color, end_color, steps):
    def interpolate(start, end, factor):
        return int(start + (end - start) * factor)

    gradation = []
    for i in range(steps):
        factor = i / (steps - 1)
        r = interpolate((start_color >> 16) & 0xFF, (end_color >> 16) & 0xFF, factor)
        g = interpolate((start_color >> 8) & 0xFF, (end_color >> 8) & 0xFF, factor)
        b = interpolate(start_color & 0xFF, end_color & 0xFF, factor)
        gradation.append((r << 16) | (g << 8) | b)
    return tuple(gradation)

GRADATION = generate_gradation(0x2b335f, 0xA9C1FF, 8)

class AffterImage:
    SIZE = 5
    COUNT = 20
    circles = [] # [(x, y, count)]

    @classmethod
    def add_circle(cls, x, y):
        cls.circles.append((x, y, cls.COUNT))

    @classmethod
    def update(cls):
        cls.circles = [(x, y, count - 1) for x, y, count in cls.circles if count > 0]

    @classmethod
    def draw(cls, reverse=False):
        for circle in cls.circles:
            c = len(GRADATION) * circle[2] // cls.COUNT
            if reverse:
                c = len(GRADATION) - c - 1
            pyxel.circ(circle[0], circle[1], cls.SIZE, c)

class Pendulum:
    SIZE = 5

    def __init__(self, n):
        lengths = [pyxel.rndf(*LENGTH_RANGE) for _ in range(n)]
        weights = [pyxel.rndf(*WEIGHT_RANGE) for _ in range(n)]
        init_angles = [pyxel.rndf(*INIT_ANGLE_RANGE) for _ in range(n)]
        init_velocities = [pyxel.rndf(*INIT_VELOCITY_RANGE) for _ in range(n)]
        p = pendulum.PendulumSolver(
            lengths,
            weights,
            TIME_DURATION,
            init_angles,
            init_velocities
        )
        self.result = p.solve(SIMURATION_FLAME)

    def draw(self, i, reverse=False):
        c1, c2 = 0, 7
        if reverse:
            c1, c2 = 7, 7
        center = (80, 30)
        pos = [(x + center[0], -y + center[1]) for x, y in self.result[i]]
        pos.insert(0, center)
        for s, t in zip(pos[:-1], pos[1:]):
            pyxel.line(s[0], s[1], t[0], t[1], c2)
        for p in pos[:-1]:
            pyxel.circ(p[0], p[1], self.SIZE, c1)
            pyxel.circb(p[0], p[1], self.SIZE, c2)
        pyxel.circ(pos[-1][0], pos[-1][1], self.SIZE, c2)
        if i % 4 == 0:
            AffterImage.add_circle(*pos[-1])


class StartPoint:
    W = 12
    H = 12
    X = WINDOW_W // 8
    Y = FLOAR - H
    COLOR = 11

    @classmethod
    def draw(cls):
        pyxel.rect(cls.X, cls.Y, cls.W, cls.H, cls.COLOR)

class Apple:
    R = 4
    COLOR = 8

    X_RANGE = (WINDOW_W // 4, WINDOW_W)
    Y_RANGE = (FLOAR - 50, FLOAR)

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self): 
        pyxel.circ(self.x, self.y, self.R, self.COLOR)

    @classmethod
    def generate(cls):
        x = pyxel.rndi(*cls.X_RANGE)
        y = pyxel.rndi(*cls.Y_RANGE)
        return cls(x, y)


class CharacterStatus(Enum):
    NONE = 0
    JUMP = 1

class Character:
    W = 10
    H = 10
    MAX_X_VELOCITY = 2
    MAX_Y_VELOCITY = 8
    SPEED = 1
    JUMP = 6

    JUMP_COUNT = 5
    JUMP_CHARGE_COUNT = 2

    COLOR = 10

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.count = 0
        self.status = CharacterStatus.NONE
        self.double_jumped = False

    def update(self):
        if self.count > 0:
            self.count -= 1
        if self.count == 0:
            self.status = CharacterStatus.NONE
        if self.on_floor():
            self.double_jumped = False

        self.x += self.vx
        self.y += self.vy
        self.x_limit()

        match self.status:
            case CharacterStatus.NONE:
                self.update_none()
            case CharacterStatus.JUMP:
                self.update_jump()

    def update_none(self):
        self.gravity()
        self.move_x()
        self.speed_limit()
        if self.pushed_jump_button():
            if self.on_floor():
                self.vy = -self.JUMP
                self.status = CharacterStatus.JUMP
                self.count = self.JUMP_COUNT
            elif not self.double_jumped:
                self.vy = -self.JUMP
                self.status = CharacterStatus.JUMP
                self.count = self.JUMP_COUNT
                self.double_jumped = True

    def update_jump(self):
        self.gravity()
        self.move_x()
        self.speed_limit()

    def on_floor(self):
        if self.y + self.H >= FLOAR:
            return True
        return False

    # Applies gravity to the character.
    def gravity(self):
        if self.on_floor():
            self.vy = 0
            self.y = FLOAR - self.H
        else:
            self.vy += 1

    # Moves the character left or right based on button presses.
    def move_x(self):
        vx = 0
        if self.pushed_right_button():
            vx += self.SPEED
        if self.pushed_left_button():
            vx -= self.SPEED
        if vx == 0:
            if self.vx > 0:
                self.vx -= 1
            elif self.vx < 0:
                self.vx += 1
        else:
            self.vx += vx

    # Clamps the horizontal (vx) and vertical (vy) velocities to ensure they
    # do not exceed the defined maximum limits for smooth character movement.
    def speed_limit(self):
        self.vx = min(max(self.vx, -self.MAX_X_VELOCITY), self.MAX_X_VELOCITY)
        self.vy = min(max(self.vy, -self.MAX_Y_VELOCITY), self.MAX_Y_VELOCITY)

    def x_limit(self):
        self.x = min(max(self.x, 0), WINDOW_W - self.W)

    # Checks if the jump button is pressed (W, SPACE, or UP arrow keys)
    def pushed_jump_button(self):
        return pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP)

    # Checks if the left button is pressed (A or LEFT arrow keys)
    def pushed_left_button(self):
        return pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT)

    # Checks if the right button is pressed (D or RIGHT arrow keys)
    def pushed_right_button(self):
        return pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)

    def draw(self):
        dx, dy = 0, 0
        if self.status == CharacterStatus.JUMP:
            if self.JUMP - self.count < self.JUMP_CHARGE_COUNT:
                dx, dy = -1, 1
            elif self.JUMP - self.count > self.JUMP_CHARGE_COUNT:
                dx, dy = 1, -1
        pyxel.rect(self.x + dx, self.y + dy, self.W - 2*dx, self.H - 2*dy, self.COLOR)

class App:
    def __init__(self):
        pyxel.init(WINDOW_W, WINDOW_H)
        for i, c in enumerate(GRADATION):
            pyxel.colors[i] = c

        self.pendulums = [Pendulum(3)]
        self.character = Character()
        self.apples = [Apple.generate() for _ in range(3)]
        self.count = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.count += 1
        if self.count >= SIMURATION_FLAME:
            self.count = 0
        self.character.update()
        AffterImage.update()

    def draw(self):
        pyxel.cls(0)
        draw_split = WINDOW_H * self.count // SIMURATION_FLAME

        pyxel.clip(0, 0, WINDOW_W, draw_split)
        pyxel.rect(0, 0, WINDOW_W, draw_split, 0)
        for pendulum in self.pendulums:
            pendulum.draw(self.count)
        AffterImage.draw()

        pyxel.clip(0, draw_split, WINDOW_W, WINDOW_H - draw_split)
        pyxel.rect(0, draw_split, WINDOW_W, WINDOW_H - draw_split, 7)
        for pendulum in self.pendulums:
            pendulum.draw(self.count, reverse=True)
        AffterImage.draw(reverse=True)

        pyxel.clip()
        StartPoint.draw()
        for apple in self.apples:
            apple.draw()
        self.character.draw()

        pyxel.line(0, FLOAR, WINDOW_W, FLOAR, 9)

App()
