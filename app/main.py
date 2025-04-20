import pyxel

import pendulum

WINDOW_W = 160
WINDOW_H = 120

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


class App:
    def __init__(self):
        pyxel.init(WINDOW_W, WINDOW_H)
        for i, c in enumerate(GRADATION):
            pyxel.colors[i] = c

        self.pendulums = [Pendulum(3)]
        self.count = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.count += 1
        if self.count >= SIMURATION_FLAME:
            self.count = 0
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


App()
