import pyxel

import pendulum

TIME_DURATION = 30  # Time duration in seconds
SIMURATION_FLAME = 300

LENGTH_RANGE = (5.0, 30.0)  # Length of the pendulum strings in meters
WEIGHT_RANGE = (1.0, 10.0)  # Weight of the pendulum bob in kg
# Initial angles of the pendulum bobs in radians
INIT_ANGLE_RANGE = (-3.14, 3.14)
# Initial velocities of the pendulum bobs in m/s
INIT_VELOCITY_RANGE = (-1.0, 1.0)

class AffterImage:
    MAX_SIZE = 5
    MIN_SIZE = 3
    COUNT = 20
    circles = [] # [(x, y, count)]

    @classmethod
    def add_circle(cls, x, y):
        cls.circles.append((x, y, cls.COUNT))

    @classmethod
    def update(cls):
        cls.circles = [(x, y, count - 1) for x, y, count in cls.circles if count > 0]

    @classmethod
    def draw(cls):
        for circle in cls.circles:
            size = cls.MIN_SIZE + (cls.MAX_SIZE - cls.MIN_SIZE) * circle[2] / cls.COUNT
            pyxel.circ(circle[0], circle[1], size, 8)

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

    def draw(self, i):
        center = (80, 60)
        pos = [(x + center[0], -y + center[1]) for x, y in self.result[i]]
        pos.insert(0, center)
        for s, t in zip(pos[:-1], pos[1:]):
            pyxel.line(s[0], s[1], t[0], t[1], 7)
        for p in pos[:-1]:
            pyxel.circ(p[0], p[1], self.SIZE, 0)
            pyxel.circb(p[0], p[1], self.SIZE, 7)
        pyxel.circ(pos[-1][0], pos[-1][1], self.SIZE, 8)
        if i % 4 == 0:
            AffterImage.add_circle(*pos[-1])


class App:
    def __init__(self):
        pyxel.init(160, 120)

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
        AffterImage.draw()
        for pendulum in self.pendulums:
            pendulum.draw(self.count)
        


App()
